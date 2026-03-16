from django.shortcuts import render, get_object_or_404

# Create your views here.

from .models import Producto, Categoria

# Página de inicio
def inicio(request):
    # Seleccionamos algunos productos destacados (los primeros 5)
    productos_destacados = Producto.objects.filter(activo=True)[:5]
    return render(request, "inicio.html", {"productos_destacados": productos_destacados})

# Catálogo completo
def catalogo(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(activo=True)
    return render(request, "catalogo.html", {
        "categorias": categorias,
        "productos": productos,
    })

# Detalle de un producto
def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, "producto.html", {"producto": producto})
