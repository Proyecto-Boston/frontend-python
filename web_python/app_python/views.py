from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from django.shortcuts import render

# Request: Realizar peticiones al servidor
# HttpResponse: Enviar la respuesta a las peticiones usando el protocolo Http

# Esto es una vista
def bienvenida(request): # Pasamos un objeto de tipo request como primer argumento
    return render(request, 'homepage.html')

def signin(request):
    return render(request, 'login.html')

def signup(request):
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