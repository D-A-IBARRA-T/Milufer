from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("producto/<int:producto_id>/", views.producto_detalle, name="producto_detalle"),
    
]
