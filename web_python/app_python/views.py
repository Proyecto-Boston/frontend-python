from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render
import requests

# Request: Realizar peticiones al servidor
# HttpResponse: Enviar la respuesta a las peticiones usando el protocolo Http


def bienvenida(request):  # Pasamos un objeto de tipo request como primer argumento
    return render(request, 'homepage.html')


def signin(request):
    if request.method == 'POST':
        # Retornar los datos digitados en el form de login
        email = request.POST['email']
        password = request.POST['password']
        payload = {'email': email, 'password': password}
        # AGREGAR LA INTERACCIÓN CON EL SERVIDOR JAVA PARA INICIAR SESIÓN
        # SI ES EXITOSO EJECUTAR EL SIGUIENTE COMENTARIO
        # return redirect('manager')
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        # Recopilar los datos del form de registro
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        payload = {'email': email, 'password': password, 'primer nombre': first_name, 'apellido': last_name}
        # Crear nuevo usuario
        # Iniciar sesión automáticamente tras el registro
        # return redirect('manager')
    return render(request, 'register.html')


def filemanager(request):
    if request.method == 'POST':
        archivo_subido = request.FILES['file']
        print("Se eligió un archivo")
        # AGREGAR LA INTERACCIÓN CON EL SERVIDOR JAVA PARA SUBIR EL ARCHIVO CUANDO LO AGREGUEN AL SERVIDOR
        # ESTE RETURN AGREGA UN PARÁMETRO DE 'SUBIDA EXITOSA' A LA URL PARA QUE EL TEMPLATE SE REFRESQUE
        return HttpResponseRedirect('/manage/?upload_success=1')
    else:
        print("No hay archivo")
        pass
    return render(request, 'file_manager.html')
