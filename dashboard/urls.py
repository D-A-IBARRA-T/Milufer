from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("clientes/", views.clientes_view, name="clientes"),
    
    path("estadisticas/", views.estadisticas_view, name="estadisticas"),
    
    path("pedidos/", views.pedidos_view, name="pedidos"),
    path("pedidos/<int:pedido_id>/detalle/", views.detalle_pedido, name="admin_detalle_pedido"),
    path("pedidos/<int:pedido_id>/confirmar/", views.confirmar_pedido, name="admin_confirmar_pedido"),
    path("pedidos/<int:pedido_id>/cancelar/", views.cancelar_pedido, name="admin_cancelar_pedido"),

    path("productos/", views.productos_view, name="productos"),
    path("producto/nuevo/", views.admin_agregar_producto, name="admin_agregar_producto"),
    path("producto/editar/<int:producto_id>/", views.admin_editar_producto, name="admin_editar_producto"),
    path("producto/eliminar/<int:producto_id>/", views.admin_eliminar_producto, name="admin_eliminar_producto"),
    
    path("clientes/<int:cliente_id>/", views.admin_detalle_cliente, name="admin_detalle_cliente"),
    path("clientes/editar/<int:cliente_id>/", views.admin_editar_cliente, name="admin_editar_cliente"),
    
]
