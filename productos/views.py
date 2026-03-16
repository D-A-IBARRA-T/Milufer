from django.shortcuts import get_object_or_404, render

from .models import Categoria, Producto


# Página de inicio

def inicio(request):
    productos_destacados = Producto.objects.filter(activo=True, destacado=True).order_by("-actualizado")[:8]

    if not productos_destacados:
        productos_destacados = Producto.objects.filter(activo=True).order_by("-actualizado")[:8]

    return render(request, "inicio.html", {"productos_destacados": productos_destacados})


# Catálogo completo

def catalogo(request):
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(activo=True)
    return render(
        request,
        "catalogo.html",
        {
            "categorias": categorias,
            "productos": productos,
        },
    )


# Detalle de un producto

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, "producto.html", {"producto": producto})
