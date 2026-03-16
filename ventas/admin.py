from django.contrib import admin

# Register your models here.

from .models import Pedido, PedidoProducto

admin.site.register(Pedido)
admin.site.register(PedidoProducto)