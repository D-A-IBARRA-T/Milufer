from django.shortcuts import render, get_object_or_404

from .models import Producto, Categoria


# Página de inicio
def inicio(request):
    productos_destacados = list(
        Producto.objects.filter(activo=True, destacado=True).order_by("-creado")[:8]
    )

    if not productos_destacados:
        productos_destacados = list(
            Producto.objects.filter(activo=True).order_by("-creado")[:8]
        )

    return render(request, "inicio.html", {"productos_destacados": productos_destacados})


# Catálogo completo
def catalogo(request):
    categorias = Categoria.objects.filter(activo=True)
    productos = Producto.objects.filter(activo=True)
    return render(request, "catalogo.html", {
        "categorias": categorias,
        "productos": productos,
    })


# Detalle de un producto
def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    return render(request, "producto.html", {"producto": producto})
