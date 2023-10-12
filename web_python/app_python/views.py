from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Fault
import requests
import json

# Request: Realizar peticiones al servidor
# HttpResponse: Enviar la respuesta a las peticiones usando el protocolo Http

# Inicialización de zeep, una libreria que permite interactuar con el WSDL usando Python
transport = Transport(session=requests.Session())
cliente = Client('http://localhost:1802/app?wsdl', transport=transport)
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
                return HttpResponseRedirect('/manage/')
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
            user_data = {"id":1004, "email": email, "password": password, "name": first_name, "surname": last_name}

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
    # Lista de archivos (el arreglo contendrá la lista de archivos de la BD Scala)
    files = [
        {"name": "Archivo_1.docx", "date": "27/02/2023", "size": "745.60kb"},
        {"name": "Archivo_2.docx", "date": "13/03/2023", "size": "120.50mb"},
        {"name": "Video.mp4", "date": "05/04/2023", "size": "5.40gb"},
    ]
    # Lista de directorios (el arreglo contendrá la lista de directorios de la BD Scala)
    directories = [
        {"directory_id": 1, "name": "Universidad"},
        {"directory_id": 2, "name": "Familia"},
        {"directory_id": 3, "name": "Personal"}
    ]

    if request.method == 'POST':
        archivo_subido = request.FILES['file']
        print("Se eligió un archivo")
        # AGREGAR LA INTERACCIÓN CON EL SERVIDOR JAVA PARA SUBIR EL ARCHIVO CUANDO LO AGREGUEN AL SERVIDOR
        # ESTE RETURN AGREGA UN PARÁMETRO DE 'SUBIDA EXITOSA' A LA URL PARA QUE EL TEMPLATE SE REFRESQUE
        return HttpResponseRedirect('/manage/?upload_success=1')
    else:
        print("No hay archivo")
        pass
    return render(request, 'file_manager.html', {'files': files, 'directories': directories})
