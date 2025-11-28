from django.contrib import admin
from .models import PerfilUsuario, Producto

admin.site.register(PerfilUsuario)
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio_formateado', 'activo', 'creado_en']
    list_editable = ['activo']
    list_filter = ['activo', 'creado_en']
    search_fields = ['nombre']
    readonly_fields = ['creado_en']

    def precio_formateado(self, obj):
        return f"${obj.precio:,}".replace(",", ".")
    precio_formateado.short_description = "Precio"