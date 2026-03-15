from django.contrib import admin

# Register your models here.

from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "activo", "categoria")
    list_filter = ("activo", "categoria")
    search_fields = ("nombre",)
