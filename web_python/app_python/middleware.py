from django.shortcuts import redirect
from zeep import Client
from zeep.transports import Transport
import json
import requests

# Middleware que verifica si el usuario ya inicio sesión (tiene un JWT) y redirecciona a /manage/ y al middleware de autenticación
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        transport = Transport(session=requests.Session())
        self.cliente = Client('http://localhost:2376/app?wsdl', transport=transport)
        print("Conectado a WSDL")

    def __call__(self, request):
        jwt_token = request.COOKIES.get('jwt')

        if jwt_token:
            try:
                response = self.cliente.service.verifySession(jwt_token)
                if response.statusCode != 202:
                    print("Token inválido o vencido, redireccionando a login")
                    request.session.flush()
                    response = redirect('login')
                    response.delete_cookie('jwt')
                    return response
                
                if request.path != '/manage/' and request.path != '/logout/' and request.path != '/shared/' and request.path != '/favicon.ico':
                    print("El usuario ya inicio sesión, redireccionando a /manage/")
                    request.session['current_path'] = ""
                    request.session['current_parent'] = 0
                    response = redirect('manager')
                    return response

                user_data = json.loads(response.json)
                request.session['user_id'] = user_data.get('user_id')
                print("JWT validado correctamente")
                
            except Exception as e:
                print(f"Error verificando JWT: {str(e)}")
                request.session.flush()
                response = redirect('login')
                response.delete_cookie('jwt')
                return response
        elif request.path not in ['/login/', '/register/', '/homepage/', '/logout/']:
            print("El usuario no ha iniciado sesión. Redireccionar a login")
            response = redirect('login')
            return response

        return self.get_response(request)
