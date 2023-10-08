from django.http import HttpResponse
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
    return render(request, 'file_manager.html')