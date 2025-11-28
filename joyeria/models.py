from django.db import models
from django.contrib.auth.models import User

# Tu modelo que ya tenías
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.usuario.username


# ← ESTE ES EL MODELO QUE FALTABA
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(help_text="Precio en pesos (ej: 45000)")
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-creado_en']