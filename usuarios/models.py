from django.db import models

# Create your models here.

from django.contrib.auth.models import User



class Direccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    referencia = models.CharField(max_length=255, blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return self.direccion


class UsuarioEliminado(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_registro = models.DateTimeField()
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
