from django.shortcuts import redirect
from zeep import Client
from zeep.transports import Transport
import json
import requests

# Middleware que autentica el JWT
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Iniciar cliente SOAP
        transport = Transport(session=requests.Session())
        self.cliente = Client('http://localhost:1802/app?wsdl', transport=transport)
        print("Conectado a WSDL")

    def __call__(self, request):
        # Vistas que no deben ejecutar el middleware
        excluded_paths = ['/login/', '/register/', '/homepage/', '/logout/'] 

        # Si la vista no está en la lista de excepciones...
        if request.path not in excluded_paths:
            # Obtener el JWT de la sesión actual de cookie HTTP        
            jwt_token = request.COOKIES.get('jwt')

            if jwt_token:
                # Validar si el JWT es correcto
                try:
                    response = self.cliente.service.verifySession(jwt_token)
                    if response.statusCode != 202:
                        print("JWT inválido o vencido. Por favor vuelva a iniciar sesión")
                        request.session.flush()
                        response = redirect('login')
                        response.delete_cookie('jwt')
                        return response
                    # Establecer el id del usuario que está en el sistema
                    user_data = json.loads(response.json)
                    request.session['user_id'] = user_data.get('user_id')
                    print("JWT validado correctamente")
                    print("Middleware: ID del usuario iniciando sesión " + str(user_data.get('user_id')))
                except Exception as e:
                    print(f"Error verificando JWT")
                    request.session.flush()
                    response = redirect('login')
                    response.delete_cookie('jwt')
                    return response
            else:
                # Si no hay JWT en las cookies
                print("No hay ningún JWT, debe iniciar sesión")
                response = redirect('login')
                return response

        # Llamar a la siguiente vista
        response = self.get_response(request)

        return response

# Middleware que verifica si el usuario ya inicio sesión (tiene un JWT) y redirecciona a /manage/ y al middleware de autenticación
class LoggedInRedirect:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vistas que no deben ejecutar el middleware
        excluded_paths = ['/manage/', '/logout/']

        # Si el usuario no está intentando cerrar sesión o acceder a administrador de archivos...
        if request.path not in excluded_paths:
            jwt_token = request.COOKIES.get('jwt')

            if jwt_token:
                print("El usuario ya inicio sesión, redireccionando a /manage/")
                return redirect('/manage/')

        # Llamar al siguiente middleware o vista
        return self.get_response(request)
