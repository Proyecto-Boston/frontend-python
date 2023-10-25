from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField()
    contrasena = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Archivo(models.Model):
    nombre = models.CharField(max_length=255)
    ruta = models.CharField(max_length=255)
    tamano = models.FloatField()
    usuario_id = models.IntegerField()
    nodo_id = models.IntegerField()
    directorio_id = models.IntegerField()

    def __str__(self):
        return self.nombre