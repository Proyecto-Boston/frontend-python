from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render, redirect
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Fault
import requests
import json

# Request: Realizar peticiones al servidor
# HttpResponse: Enviar la respuesta a las peticiones usando el protocolo Http

# Inicialización de zeep, una libreria que permite interactuar con el WSDL usando Python
transport = Transport(session=requests.Session())
cliente = Client('http://localhost:2376/app?wsdl', transport=transport)
print("Conectado a WSDL")


def bienvenida(request):  # Pasamos un objeto de tipo request como primer argumento
    return render(request, 'homepage.html')


def signin(request):
    if request.method == 'POST':
        # Recopilar los datos que el usuario digitó en el form
        email = request.POST['email']
        password = request.POST['password']

        print("email " + email + " password " + password)

        try:
            # Crear un objeto Usuario
            user_data = {"id": 1002, "email": email, "password": password}

            # Enviar la solicitud SOAP al servidor
            response = cliente.service.login(user_data)

            # Se pudo iniciar sesión?
            if response.statusCode == 202:
                # Redireccionar al administrador de archivos
                print("Login exitoso")
                # Almacenar el JWT que retorna el servidor en una HttpCookie
                token_data = json.loads(response.json)
                jwt_token = token_data.get('token')
                print("Token "+jwt_token)
                response = HttpResponseRedirect('/manage/')
                response.set_cookie(
                    'jwt', jwt_token, httponly=True, samesite='Strict')
                request.session['current_path'] = ""
                request.session['current_parent'] = 0
                return response
            else:
                # Si el login no pudo hacerse
                error_message = "El inicio de sesión falló. Por favor revise las credenciales"
                print(error_message)
                return render(request, 'login.html', {'error_message': error_message})
        except Fault as e:
            # Errores SOAP (exceptions returned by the server)
            error_message = f"SOAP Fault: {e.message}"
            print(error_message)
            return render(request, 'login.html', {'error_message': error_message})
        except requests.exceptions.RequestException as e:
            # Errores de conexión (e.g., server unreachable)
            error_message = f"Network Error: {str(e)}"
            print(error_message)
            return render(request, 'login.html', {'error_message': error_message})
        except Exception as e:
            # Errores inesperados
            error_message = f"Unexpected Error: {str(e)}"
            print(error_message)
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def logout(request):
    # Cerrar la sesión
    request.session.flush()

    # Borrar el cookie JWT de la sesión
    response = redirect('homepage')
    response.delete_cookie('jwt')

    print("La sesión se cerró exitosamente")
    return response


def signup(request):
    if request.method == 'POST':
        # Recopilar los datos que el usuario digitó en el form
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        print("email " + email + " password " + password)

        try:
            # Crear un objeto Usuario
            user_data = {"email": email, "password": password,
                         "name": first_name, "surname": last_name}

            # Enviar la solicitud SOAP al servidor
            response = cliente.service.register(user_data)

            # Se pudo registrar?
            if response.statusCode == 201:
                # Mostrar un mensaje de registro exitoso
                success_message = "Registro exitoso"
                print(success_message)
                return render(request, 'register.html', {'success_message': success_message}, status=201)
            else:
                # Si el registro no pudo hacerse
                error_message = "El registro falló. Por favor revise que los campos sean válidos"
                print(error_message)
                return render(request, 'register.html', {'error_message': error_message})
        except Fault as e:
            # Errores SOAP (exceptions returned by the server)
            error_message = f"SOAP Fault: {e.message}"
            print(error_message)
            return render(request, 'register.html', {'error_message': error_message})
        except requests.exceptions.RequestException as e:
            # Errores de conexión (e.g., server unreachable)
            error_message = f"Network Error: {str(e)}"
            print(error_message)
            return render(request, 'register.html', {'error_message': error_message})
        except Exception as e:
            # Errores inesperados
            error_message = f"Unexpected Error: {str(e)}"
            print(error_message)
            return render(request, 'register.html', {'error_message': error_message})

    return render(request, 'register.html')


def filemanager(request):
    # Lista de archivos (el arreglo contendrá la lista de archivos del usuario)
    files = []
    # Lista de directorios (el arreglo contendrá la lista de directorios del usuario)
    directories = []
    # ID del usuario que tiene la sesión abierta
    userId = request.session.get('user_id', None)
    # Ruta actual de la vista
    request.session['current_path'] = ""
    request.session['current_parent'] = 0
    current_path = request.session.get('current_path')
    current_parent = request.session.get('current_parent')
    print("Ruta actual: " + current_path)
    print("Padre actual: " + str(current_parent))
    print("Vista: ID del usuario iniciando sesión " + str(userId))
    try:
        # Enviar la solicitud SOAP al servidor
        response = cliente.service.getUserFiles(userId)

        # Se pudieron cargar los archivos?
        if response.statusCode == 200:
            # Mostrar los archivos
            print("--- Importando... ---")
            print(str(response.details))
            if str(response.details)=="Operacion exitosa.":
                print("Importados archivos y carpetas")
                sv_data = response.json.replace(",null", "")
                server_data = json.loads(sv_data)
                print(str(server_data))
                for file_info in server_data['files']:
                    file_entry = {
                        "id": file_info['id'],
                        "name": file_info['nombre'],
                        "size": f"{file_info['tamano']/1000}kb",
                        "path": file_info['ruta'],
                        "userId": userId,
                        "directory_id": file_info['directorio_id']
                    }
                    files.append(file_entry)
                if "folders" in server_data:
                    for folder_info in server_data['folders']:
                        folder_entry = {
                            "id": folder_info['id'],
                            "name": folder_info['nombre'],
                            "size": folder_info['tamano'],
                            "path": folder_info['ruta'],
                            "nodeId": folder_info['nodoId'],
                            "fatherId": folder_info['padreId'],
                            "backNodeId": folder_info['respaldo_id']
                        }
                        directories.append(folder_entry)
            elif str(response.details)=="El usuario no tiene archivos":
                print("Se trata de importar carpetas, no hay archivos")
                if (response.json!=None):
                    server_data = json.loads(response.json)
                    for folder_info in server_data['folders']:
                        folder_entry = {
                            "id": folder_info['id'],
                            "name": folder_info['nombre'],
                            "size": folder_info['tamano'],
                            "path": folder_info['ruta'],
                            "nodeId": folder_info['nodoId'],
                            "fatherId": folder_info['padreId'],
                            "backNodeId": folder_info['respaldo_id']
                        }
                        directories.append(folder_entry)
                else:
                    print("El usuario tampoco tiene carpetas")
            else:
                print("El usuario no tiene archivos ni carpetas")
        else:
            # Si no se pudo importar archivos
            error_message = "No pudieron importarse los archivos. Por favor vuelva a iniciar sesión"
            print(error_message)
            print(response.statusCode)
            print(response.details)
            return render(request, 'file_manager.html', {'error_message': error_message, 'directories': directories})
    except Fault as e:
        # Errores SOAP (exceptions returned by the server)
        error_message = f"SOAP Fault: {e.message}"
        print(error_message)
        return render(request, 'file_manager.html', {'error_message': error_message, 'directories': directories})
    except Exception as e:
        # Errores inesperados
        error_message = f"Unexpected Error: {str(e)}"
        print(error_message)
        return render(request, 'file_manager.html', {'error_message': error_message, 'directories': directories})

    if request.method == 'POST':
        # SI SE ESTÁ TRATANDO DE CREAR UNA CARPETA...
        if 'create_folder' in request.POST:
            folder_name = request.POST['folder_name']
            print("Nombre carpeta digitado: " + folder_name)
            current_path = request.session.get('current_path')
            print("Ruta donde se está actualmente: " + current_path)
            current_parent = request.session.get('current_parent')
            print("Padre actual: " + str(current_parent))
            if folder_name and crear_carpeta(folder_name, userId, current_path, current_parent):
                print("Se creó la carpeta exitosamente")
                # Refrescar la vista para mostrar la nueva carpeta
                return redirect('manager')
            else:
                print("No se pudo crear la carpeta, revise su conexión o que haya digitado un nombre válido")
        # SI SE ESTÁ TRATANDO DE BORRAR UNA CARPETA...
        if 'delete_folder' in request.POST:
            print("------Tratando de borrar la carpeta:------")
            folder_to_delete = request.POST['delete_folder_id']
            print("Intentando borrar carpeta ID " + str(folder_to_delete))
            print("directorios: " + str(directories))
            if (folder_to_delete!=None):
                print("Se borrará la carpeta: "+str(folder_to_delete))
                response = cliente.service.deleteFolder(folder_to_delete)
                if response.statusCode == 201:
                    #Se elimino exitosamente
                    print("Carpeta eliminada exitosamente")
                    print(response.statusCode)
                    print(response.details)
                    return redirect('manager')
                else:
                    print("Error eliminando la carpeta")
                    print(response.statusCode)
                    print(response.details)
            else:
                print("Error procesando directorio a eliminar")
        # SI SE ESTÁ TRATANDO DE SUBIR UN ARCHIVO...
        if 'upload_file_button' in request.POST:
            print("-----------SE PRESIONÓ EL BOTÓN DE SUBIR UN ARCHIVO-------------")
            archivos_subidos = request.FILES.getlist('file')  # Get a list of uploaded files
            num_files_uploaded = len(archivos_subidos)

            # ID del directorio donde se está guardando el archivo
            directorio_destino = request.POST.get('selected_directory', None)
            print("DIRECTORIO DESTINO VALUE: " + str(directorio_destino))

            for archivo_subido in archivos_subidos:
                print("ARCHIVO SELECCIONADO:", archivo_subido.name)
                # Leer el archivo y guardarlo in bytes
                file_data = archivo_subido.read()
                
                if str(directorio_destino) != "None" and str(directorio_destino) != "":
                    print("---------------EL ARCHIVO ESTÁ EN UN DIRECTORIO--------------")
                    nombre_directorio_destino = get_directory_name_by_id(directorio_destino, directories)
                    print("NOMBRE DEL DIRECTORIO DEL ARCHIVO:", nombre_directorio_destino)
                    archivo_data = {"id": 1, "name": archivo_subido.name, "path": nombre_directorio_destino,
                                    "fileData": file_data, "size": archivo_subido.size, "userId": userId,
                                    "folderId": directorio_destino, "nodeId": 1, "backNodeId": 2}
                else:
                    print("---------------EL ARCHIVO NO TIENE DIRECTORIO----------")
                    archivo_data = {"id": 1, "name": archivo_subido.name, "path": "", "fileData": file_data,
                                    "size": archivo_subido.size, "userId": userId, "folderId": 0, "nodeId": 1,
                                    "backNodeId": 2}

                print("--- Se eligió un archivo, intentando subirlo al servidor... ---")
                response = cliente.service.uploadFile(archivo_data)
                
                # Check the response for each file upload
                if response.statusCode == 201:
                    # Se subio el archivo exitosamente
                    success_message = "Subida exitosa: " + archivo_subido.name
                    print(success_message)
                    num_files_uploaded-=1
                    if num_files_uploaded==0:
                        return HttpResponseRedirect('/manage/?upload_success=1')
                else:
                    # Si no se pudo subir el archivo
                    error_message = "Fallo al subir el archivo: " + archivo_subido.name
                    print(error_message)
                    print(response.statusCode)
                    print(response.details)
                    num_files_uploaded-=1
                    if num_files_uploaded==0:
                        return redirect('manager')
        if 'delete_file_button' in request.POST:
            file_to_delete = request.POST['delete_file_name']
            response = cliente.service.deleteFile(file_to_delete)
            if response.statusCode == 200:
                # Se borró el archivo exitosamente
                print("Archivo eliminado exitosamente")
                print(response.statusCode)
                print(response.details)
                # Redireccionar a la misma página solo para que vuelva a ejecutarse importar archivos
                return redirect('manager')
            else:
                # No se pudo borrar el archivo
                print("Fallo al eliminar el archivo. Intentelo nuevamente")
                print(response.statusCode)
                print(response.details)
                return redirect('manager')
        if 'move_file_button' in request.POST:
            print("-------MOVIENDO ARCHIVO--------")
            file_to_move = request.POST['move_file_name']
            print("ID del archivo a moverse: " + str(file_to_move))
            moving_path = get_file_path_by_id(file_to_move, files)
            print("Ruta actual del archivo que se va a mover: " + moving_path)
            target_directory_id = request.POST.get('target_directory_move_'+str(file_to_move), None)
            if (target_directory_id!=None and target_directory_id!=""):
                print("ID de directorio al que se quiere mover el archivo: " + str(target_directory_id))
                target_directory_path = get_directory_path_by_id(target_directory_id, directories)
                print("Ruta completa de ese directorio: " + target_directory_path)
                # Remove the first character from target_directory_path
                if target_directory_path!="":
                    target_directory_path = target_directory_path[1:]+"/"
                print("Ruta completa a la que se moverá el archivo: " + target_directory_path)
                # Solo intentar mover el archivo si se seleccionó un directorio
                response = cliente.service.moveFile(file_to_move, target_directory_id, target_directory_path)
                if response.statusCode == 201:
                    # Se movió el archivo exitosamente
                    success_message = "Archivo movido exitosamente"
                    print(success_message)
                    print(response.statusCode)
                    print(response.details)
                    return redirect('manager')
                else:
                    # No se pudo mover el archivo
                    print("Fallo al mover el archivo. Intentelo nuevamente")
                    print(response.statusCode)
                    print(response.details)
                    return redirect('manager')
        if 'share_file_button' in request.POST:
            print("-------------------- COMPARTIENDO ARCHIVO-----------------")
            file_to_share = request.POST['share_file_id']
            print("Archivo que se va a compartir: " + str(file_to_share))
            user_to_share = request.POST['share_email']
            print("Usuario al que se le va a compartir el archivo: " + str(user_to_share))
            response = cliente.service.shareFile(str(user_to_share), file_to_share)
            if response.statusCode == 201:
                print("Se compartió el archivo exitosamente")
                print(response.statusCode)
                print(response.details)
            else:
                print("Error compartiendo el archivo con el usuario")
                print(response.statusCode)
                print(response.details)
        if 'download_file_button' in request.POST:
            file_to_download = request.POST['download_file_name']
            print("ID del archivo a descargar " + file_to_download)
            response = cliente.service.downloadFile(file_to_download)
            if response.statusCode == 200:
                # Descargado exitosamente
                print(response.statusCode)
                print(response.details)
                file_name = get_file_name_by_id(file_to_download,files)
                print("Nombre del archivo a descargar: " + str(file_name))
                if (file_name!=None and file_name!=""):
                    file_response = HttpResponse(response.fileData, content_type='application/octet-stream')
                    file_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    print("El archivo se descargo con exito")
                    return file_response
            else:
                print("Error: no pudo descargarse el archivo")
                return redirect('manager')
        if 'browse_folder_button' in request.POST:
            folder_to_enter = request.POST['folder_id']
            if (folder_to_enter!=None and str(folder_to_enter)!=""):
                print("ID del directorio al que se quiere entrar: " + str(folder_to_enter))
                nombre_directorio_acceso = get_directory_name_by_id(folder_to_enter, directories)
                print("Nombre del directorio al que se quiere entrar: " + nombre_directorio_acceso)
                ruta_directorio_acceso = get_directory_path_by_id(folder_to_enter, directories)
                ruta_directorio_acceso = ruta_directorio_acceso[1:]
                request.session['current_path'] = ruta_directorio_acceso
                current_path = request.session.get('current_path')
                print("Ruta actual: " + current_path)
                request.session['current_parent'] = folder_to_enter
                current_parent = request.session.get('current_parent')
                print("Padre actual: " + str(current_parent))
                subFiles = []
                subDirectories = []
                response = cliente.service.getSubFolderFiles(folder_to_enter)
                if (response.statusCode == 201):
                    print("Se entró a la carpeta exitosamente")
                    print(response.statusCode)
                    print(response.details)
                    if (response.json!=None and response.json!=""):
                        sv_data = response.json.replace(",null", "")
                        server_subdata = json.loads(sv_data)
                        print("server_subdata: " + str(server_subdata))
                        for file_info in server_subdata['files']:
                            file_entry = {
                                "id": file_info['id'],
                                "name": file_info['nombre'],
                                "size": f"{file_info['tamano']/1000}kb",
                                "path": file_info['ruta'],
                                "userId": userId,
                                "directory_id": file_info['directorio_id']
                            }
                            subFiles.append(file_entry)
                        print("Arreglo de archivos: " + str(subFiles))
                        if "folders" in server_subdata:
                            for folder_info in server_subdata['folders']:
                                folder_entry = {
                                    "id": folder_info['id'],
                                    "name": folder_info['nombre'],
                                    "size": folder_info['tamano'],
                                    "path": folder_info['ruta'],
                                    "nodeId": folder_info['nodoId'],
                                    "fatherId": folder_info['padreId'],
                                    "backNodeId": folder_info['respaldo_id']
                                }
                                subDirectories.append(folder_entry)
                            print("Arreglo de subdirectorios: " + str(subDirectories))
                    return render(request, 'file_manager.html', {'files': subFiles, 'directories': subDirectories})
                else:
                    print("Error comunicandose con la carpeta")
                    print(response.statusCode)
                    print(response.details)
                    return redirect('manager')

    return render(request, 'file_manager.html', {'files': files, 'directories': directories})


def crear_carpeta(nombreCarpeta, userId, currentPath, currentParent):
    try:
        print("Ruta actual: " + currentPath)
        # DECLARAR CARPETA
        folder_data = {"id": 1, "name": nombreCarpeta, "path": currentPath, "userId": userId, "size":0,"nodeId": 1,
                       "backNodeId": 2, "fatherId": currentParent}
        print("Intentando crear carpeta:")
        print(str(folder_data))
        # ENVIAR SOLICITUD SOAP AL SERVIDOR
        response = cliente.service.createFolder(folder_data)
        # Se pudo crear la carpeta?
        if response.statusCode == 201:
            # Se creo exitosamente
            print("Carpeta creada exitosamente")
            return True
        else:
            # Si no se pudo crear la carpeta
            print("-----------------------------------")
            print("ERROR:")
            print(str(response.statusCode))
            print(str(response.details))
            return False
    except Fault as e:
        # Errores SOAP (exceptions returned by the server)
        error_message = f"SOAP Fault: {e.message}"
        print(error_message)
        return False
    except requests.exceptions.RequestException as e:
        # Errores de conexión (e.g., server unreachable)
        error_message = f"Network Error: {str(e)}"
        print(error_message)
        return False
    except Exception as e:
        # Errores inesperados
        error_message = f"Unexpected Error: {str(e)}"
        print(error_message)
        return False
    

def shared(request):
    print("----- VISTA DE ARCHIVOS COMPARTIDOS CON EL USUARIO -----")
    # ID del usuario que tiene la sesión abierta
    userId = request.session.get('user_id', None)
    print("Vista: ID del usuario iniciando sesión " + str(userId))
    # Lista de archivos (el arreglo contendrá la lista de archivos del usuario)
    files = []
    try:
        # Enviar la solicitud SOAP al servidor
        response = cliente.service.getSharedFiles(userId)

        # Se pudieron cargar los archivos?
        if response.statusCode == 200:
            # Mostrar los archivos
            print("--- Importando... ---")
            print(str(response.details))
            if str(response.details)=="Operacion exitosa.":
                server_data = json.loads(response.json)
                for file_info in server_data:
                    file_entry = {
                        "id": file_info['id'],
                        "name": file_info['nombre'],
                        "size": f"{file_info['tamano']/1000}kb",
                        "userId": file_info['usuario_id']
                    }
                    files.append(file_entry)
                print("Archivos compartidos: " + str(files))
            else:
                print("El usuario no tiene archivos compartidos")
        else:
            # Si no se pudo importar archivos
            error_message = "No pudieron importarse los archivos. Por favor vuelva a iniciar sesión"
            print(error_message)
            return render(request, 'shared_manager.html', {'error_message': error_message, 'files': files})
    except Fault as e:
        # Errores SOAP (exceptions returned by the server)
        error_message = f"SOAP Fault: {e.message}"
        print(error_message)
        return render(request, 'shared_manager.html', {'error_message': error_message, 'files': files})
    except Exception as e:
        # Errores inesperados
        error_message = f"Unexpected Error: {str(e)}"
        print(error_message)
        return render(request, 'shared_manager.html', {'error_message': error_message, 'files': files})
    
    if request.method == 'POST':
        if 'download_file_button' in request.POST:
            file_to_download = request.POST['download_file_name']
            print("ID del archivo a descargar " + file_to_download)
            response = cliente.service.downloadFile(file_to_download)
            if response.statusCode == 200:
                # Descargado exitosamente
                print(response.statusCode)
                print(response.details)
                file_name = get_file_name_by_id(file_to_download,files)
                print("Nombre del archivo a descargar: " + str(file_name))
                if (file_name!=None and file_name!=""):
                    file_response = HttpResponse(response.fileData, content_type='application/octet-stream')
                    file_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                    print("El archivo se descargo con exito")
                    return file_response
            else:
                print("Error: no pudo descargarse el archivo")
                print(response.statusCode)
                print(response.details)
    return render (request, 'shared_manager.html', {'files': files})

def get_directory_name_by_id(directory_id, directories):
    for directory in directories:
        if str(directory["id"]) == str(directory_id):
            print("Match found")
            return directory["name"]
    return None

def get_file_name_by_id(file_id, files):
    for file in files:
        if str(file["id"]) == str(file_id):
            print("Match found")
            return file["name"]
    return None

def get_file_path_by_id(file_id, files):
    for file in files:
        if str(file["id"]) == str(file_id):
            print("Match found")
            return file["path"]
    return None

def get_directory_path_by_id(directory_id, directories):
    for directory in directories:
        if str(directory["id"]) == str(directory_id):
            print("Match found")
            return directory["path"]
    return None