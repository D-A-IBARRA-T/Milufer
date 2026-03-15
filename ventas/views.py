# views.py (app "ventas")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from productos.models import Producto
from ventas.models import Pedido, PedidoProducto
from django.utils import timezone
from datetime import timedelta
from urllib.parse import quote


# ────────────────────────────────────────────────
# AGREGAR PRODUCTO AL CARRITO (sesión)
# ────────────────────────────────────────────────
@login_required
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)

    if producto.stock < 1:
        messages.error(request, f"¡Lo sentimos! {producto.nombre} está sin stock.")
        return redirect("productos:detalle", producto_id=producto.id)
    
    cantidad = int(request.POST.get("cantidad", 1))
    if cantidad < 1:
        cantidad = 1

    carrito = request.session.get("carrito", {})
    pid_str = str(producto.id)

    if pid_str not in carrito:
        carrito[pid_str] = {"cantidad": 0}

    carrito[pid_str]["cantidad"] += cantidad

    if carrito[pid_str]["cantidad"] > producto.stock:
        carrito[pid_str]["cantidad"] = producto.stock
        messages.warning(
            request,
            f"Se ajustó la cantidad de {producto.nombre} al stock disponible ({producto.stock})."
        )

    request.session["carrito"] = carrito
    request.session.modified = True
    messages.success(
        request,
        f"{producto.nombre} añadido al carrito ×{carrito[pid_str]['cantidad']}"
    )
    return redirect("ventas:carrito")


# ────────────────────────────────────────────────
# ELIMINAR PRODUCTO DEL CARRITO
# ────────────────────────────────────────────────
def eliminar_carrito(request, producto_id):
    carrito = request.session.get("carrito", {})
    pid_str = str(producto_id)

    if pid_str in carrito:
        nombre = Producto.objects.filter(id=producto_id).values_list('nombre', flat=True).first() or "Producto"
        del carrito[pid_str]
        request.session["carrito"] = carrito
        request.session.modified = True
        messages.success(request, f"{nombre} eliminado del carrito.")

    return redirect("ventas:carrito")

def eliminar_uno(request, producto_id):
    carrito = request.session.get("carrito", {})
    pid_str = str(producto_id)

    if pid_str in carrito:
        if carrito[pid_str]["cantidad"] > 1:
            carrito[pid_str]["cantidad"] -= 1
        else:
            # Si solo queda 1, eliminar el producto completo
            del carrito[pid_str]
        request.session["carrito"] = carrito
        request.session.modified = True

    return redirect("ventas:carrito")



# ────────────────────────────────────────────────
# VER CARRITO
# ────────────────────────────────────────────────
def ver_carrito(request):
    carrito = request.session.get("carrito", {})
    items_carrito = []
    total_carrito = 0
    productos_invalidos = []

    for pid_str, datos in list(carrito.items()):
        try:
            producto = Producto.objects.get(id=int(pid_str), activo=True)
            if producto.stock < 1:
                productos_invalidos.append(producto.nombre)
                del carrito[pid_str]
                continue

            cantidad = min(datos["cantidad"], producto.stock)
            if cantidad != datos["cantidad"]:
                datos["cantidad"] = cantidad
                request.session.modified = True

            subtotal = producto.precio * cantidad
            total_carrito += subtotal

            items_carrito.append({
                "producto": producto,
                "cantidad": cantidad,
                "subtotal": subtotal,
            })

        except Producto.DoesNotExist:
            del carrito[pid_str]
            request.session.modified = True

    if productos_invalidos:
        messages.warning(
            request,
            f"Algunos productos ya no están disponibles: {', '.join(productos_invalidos)}. Fueron removidos."
        )

    if request.session.modified:
        request.session["carrito"] = carrito

    context = {
        "items_carrito": items_carrito,
        "total_carrito": total_carrito,
        "carrito_vacio": len(items_carrito) == 0,
    }
    return render(request, "carrito.html", context)


# ────────────────────────────────────────────────
# FINALIZAR COMPRA
# ────────────────────────────────────────────────
@login_required
def finalizar_compra(request):
    carrito = request.session.get("carrito", {})

    if not carrito:
        messages.info(request, "Tu carrito está vacío.")
        return redirect("ventas:carrito")

    items = []
    total = 0
    productos_no_disponibles = []

    # Validar productos antes de crear el pedido
    for pid_str, datos in carrito.items():
        try:
            producto = Producto.objects.get(id=int(pid_str), activo=True)
            cantidad = min(datos["cantidad"], producto.stock)

            if cantidad < datos["cantidad"]:
                productos_no_disponibles.append(f"{producto.nombre} (solo {producto.stock} disponibles)")

            subtotal = producto.precio * cantidad
            total += subtotal

            items.append({
                "producto": producto,
                "cantidad": cantidad,
                "precio": producto.precio,
            })

        except Producto.DoesNotExist:
            productos_no_disponibles.append(f"Producto ID {pid_str} (no encontrado)")

    if productos_no_disponibles:
        messages.error(request, f"No se puede completar la compra: {', '.join(productos_no_disponibles)}")
        return redirect("ventas:carrito")

    if not items:
        messages.error(request, "No hay productos válidos para comprar.")
        return redirect("ventas:carrito")

    # Crear el pedido
    expiracion = timezone.now() + timedelta(hours=1)
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=total,
        estado="pendiente",
        expiracion=expiracion,
    )

    # Agregar productos al pedido
    for item in items:
        pedido.items.create(
            producto=item["producto"],
            cantidad=item["cantidad"],
            precio=item["precio"],  # Solo este campo corresponde al modelo
        )


    # Preparar mensaje de WhatsApp
    lineas = [f"{item['producto'].nombre} ×{item['cantidad']}" for item in items]
    resumen = " - ".join(lineas)
    mensaje = f"Hola, quiero finalizar mi compra (pedido #{pedido.id}): {resumen}. Total: ${total:,.0f}"
    texto_codificado = quote(mensaje)
    url_whatsapp = f"https://wa.me/573219414687?text={texto_codificado}"

    return redirect(url_whatsapp)