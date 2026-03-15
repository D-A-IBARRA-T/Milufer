from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("perfil/", views.perfil_view, name="perfil"),
    path("direccion/agregar/", views.agregar_direccion, name="agregar_direccion"),
    path("direccion/eliminar/<int:direccion_id>/", views.eliminar_direccion, name="eliminar_direccion"),
    path("logout/", views.logout_view, name="logout"),  # nueva ruta
]
