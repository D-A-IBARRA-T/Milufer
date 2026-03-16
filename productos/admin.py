from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock", "activo", "destacado", "categoria")
    list_filter = ("activo", "destacado", "categoria")
    search_fields = ("nombre",)
    list_editable = ("destacado", "activo")
