from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "destacado", "activo", "categoria")
    list_filter = ("destacado", "activo", "categoria")
    search_fields = ("nombre",)
    list_editable = ("destacado",)
