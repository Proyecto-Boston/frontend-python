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
    print("Vista: ID del usuario iniciando sesión " + str(userId))
    try:
        # Enviar la solicitud SOAP al servidor
        response = cliente.service.getUserFiles(userId)

        # Se pudieron cargar los archivos?
        if response.statusCode == 200:
            # Mostrar los archivos
            print("--- INTENTANDO IMPORTAR LOS ARCHIVOS DEL  USUARIO ---")
            print(str(response.statusCode))
            print(str(response.details))
            if str(response.details)=="Operacion exitosa.":
                print("Importados archivos y carpetas")
                server_data = json.loads(response.json)
                for file_info in server_data['files']:
                    file_entry = {
                        "id": file_info['id'],
                        "name": file_info['nombre'],
                        "size": f"{file_info['tamano']}kb",
                        "path": file_info['ruta'],
                        "userId": userId,
                        "directory_id": file_info['directorio_id'],
                        "nodeId": file_info['nodo_id'],
                        "backNodeId": file_info['respaldo_id']
                    }
                    files.append(file_entry)
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
                print("Importadas carpetas, no hay archivos")
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
                print("El usuario no tiene archivos ni carpetas")
            success_message = "---Operación completada exitosamente---"
        else:
            # Si no se pudo importar archivos
            error_message = "No pudieron importarse los archivos. Por favor vuelva a iniciar sesión"
            print(error_message)
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
            if folder_name and crear_carpeta(folder_name, userId):
                print("Se creó la carpeta exitosamente")
                # Refrescar la vista para mostrar la nueva carpeta
                return redirect('manager')
            else:
                print("No se pudo crear la carpeta, revise su conexión o que haya digitado un nombre válido")
        # SI SE ESTÁ TRATANDO DE BORRAR UNA CARPETA...
        if 'delete_folder' in request.POST:
            print("------Tratando de borrar la carpeta:------")
            delete_folder_id = request.POST['delete_folder_id']
            print(str(delete_folder_id))
            print("directorios: " + str(directories))
            folder_to_delete = get_directory_attributes(delete_folder_id, directories)
            if (folder_to_delete!=None):
                print("Se borrará la carpeta: "+str(folder_to_delete))
                response = cliente.service.deleteFolder(folder_to_delete)
                if response.statusCode == 200:
                    #Se elimino exitosamente
                    print("Carpeta eliminada exitosamente")
                    return redirect('manager')
                else:
                    print("Error eliminando la carpeta")
            else:
                print("Error procesando directorio a eliminar")
        # SI SE ESTÁ TRATANDO DE SUBIR UN ARCHIVO...
        if 'upload_file_button' in request.POST:
            archivo_subido = request.FILES['file']
            print("ARCHIVO SELECCIONADO")
            directorio_destino = request.POST.get('directory', None)
            print("DIRECTORIO DESTINO VALUE: " + str(directorio_destino))
            if str(directorio_destino) != "None":
                print("---------------EL ARCHIVO ESTÁ EN UN DIRECTORIO--------------")
                nombre_directorio_destino = get_directory_name_by_id(directorio_destino, directories)
                print("NOMBRE DEL DIRECTORIO DEL ARCHIVO: " + nombre_directorio_destino)
                archivo_data = {"id":1, "name": archivo_subido.name, "path": (nombre_directorio_destino+"/"+archivo_subido.name), "size": archivo_subido.size, "userId": userId, "folderId": directorio_destino, "nodeId": 1}
            else:
                print("---------------EL ARCHIVO NO TIENE DIRECTORIO----------")
                archivo_data = {"id":1, "name": archivo_subido.name, "path": archivo_subido.name, "size": archivo_subido.size, "userId": userId, "folderId": 0, "nodeId": 1}
            print("--- Se eligió un archivo, intentando subirlo al servidor... ---")
            response = cliente.service.uploadFile(archivo_data)
            # Se pudo subir el archivo?
            if response.statusCode == 200:
                # Se subio el archivo
                success_message = "Subida exitosa"
                print(success_message)
                return HttpResponseRedirect('/manage/?upload_success=1')
            else:
                # Si no se puede subir el archivo
                error_message = "Fallo al subir el archivo. Intentelo nuevamente"
                print(error_message)
                return redirect('manager')
        if 'delete_file_name' in request.POST:
            file_to_delete = request.POST['delete_file_name']
            file_data = {"id": file_to_delete}
            response = cliente.service.deleteFile(file_data)
            if response.statusCode == 200:
                # Se borró el archivo exitosamente
                success_message = "Archivo eliminado exitosamente"
                print(success_message)
                # Redireccionar a la misma página solo para que vuelva a ejecutarse importar archivos
                return redirect('manager')
            else:
                # No se pudo borrar el archivo
                error_message = "Fallo al eliminar el archivo. Intentelo nuevamente"
                print(error_message)
                return redirect('manager')
        if 'move_file_name' in request.POST:
            file_to_move = request.POST['move_file_name']
            file_moved_name = request.POST['move_file_fullname']
            target_directory_name = request.POST['target_directory_name']
            file_data = {"routeName": (target_directory_name+"/"+file_moved_name), "fileId": file_to_move}
            response = cliente.service.changeFilePath(file_data)
            if response.statusCode == 200:
                # Se movió el archivo exitosamente
                success_message = "Archivo movido exitosamente"
                print(success_message)
                return redirect('manager')
            else:
                # No se pudo mover el archivo
                error_message = "Fallo al mover el archivo. Intentelo nuevamente"
                print(error_message)
                return redirect('manager')
        if 'download_file_name' in request.POST:
            file_to_download = request.POST['download_file_name']
            # Consultar los atributos del archivo con este ID en la lista de files
            for file_entry in files:
                if file_entry["id"] == file_to_download:
                    file_name = file_entry["name"]
                    file_size = file_entry["size"]
                    file_route = file_entry["route"]
                    file_directory_id = file_entry["directory_id"]
                    break
            file_data = {"id":file_to_download, "name": file_name, "path": file_route, "size": file_size, "userId": userId, "folderId": file_directory_id, "nodeId": 1}
            response = cliente.service.downloadFile(file_data)
            if response.statusCode == 200:
                # Descargado exitosamente
                print("El archivo se descargo con exito")
                file_response = HttpResponse(response.fileData, content_type='application/octet-stream')
                file_response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return file_response
            else:
                print("Error: no pudo descargarse el archivo")
                return redirect('manager')


    return render(request, 'file_manager.html', {'files': files, 'directories': directories})

def crear_carpeta(nombreCarpeta, userId):
    # Primero comprobar que no exista otra carpeta con el mismo nombre
    try:
        # DECLARAR CARPETA
        folder_data = {"id": 1, "name": nombreCarpeta, "path": nombreCarpeta, "userId": userId, "nodeId": 1,
                       "backNodeId": 2, "fatherId": 0}
        # ENVIAR SOLICITUD SOAP AL SERVIDOR
        response = cliente.service.createFolder(folder_data)
        # Se pudo crear la carpeta?
        if response.statusCode == 200:
            # Se creo exitosamente
            print("Carpeta creada exitosamente")
            return True
        else:
            # Si no se pudo crear la carpeta
            error_message = "No pudo crearse la carpeta. Por favor verifique que el nombre sea válido"
            print(error_message)
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
    
def get_directory_name_by_id(directory_id, directories):
    for directory in directories:
        if str(directory["id"]) == str(directory_id):
            print("Match found")
            return directory["name"]
    return None

def get_directory_attributes(directory_id, directories):
    for directory in directories:
        if str(directory["id"]) == str(directory_id):
            print("Match found")
            this_directory = {"id": directory["id"], "name": directory["name"], "size": directory["size"],
                              "path": directory["path"], "nodeId": directory["nodeId"], "fatherId": directory["fatherId"],
                              "backNodeId": directory["backNodeId"]}
            return this_directory
    return None
