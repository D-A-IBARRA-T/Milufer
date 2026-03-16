from django.contrib import admin

# Register your models here.

from .models import Direccion, UsuarioEliminado

admin.site.register(Direccion)
admin.site.register(UsuarioEliminado)