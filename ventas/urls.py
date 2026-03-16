from django.urls import path
from . import views

app_name = "ventas"

urlpatterns = [
    path("carrito/", views.ver_carrito, name="carrito"),
    path("carrito/agregar/<int:producto_id>/", views.agregar_carrito, name="agregar_carrito"),
    path("carrito/eliminar/<int:producto_id>/", views.eliminar_carrito, name="eliminar_carrito"),
    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path("carrito/eliminar_uno/<int:producto_id>/", views.eliminar_uno, name="eliminar_uno"),

]