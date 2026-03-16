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
    # Obtener el carrito desde la sesión del usuario
    carrito = request.session.get("carrito", {})

    # Si el carrito está vacío, avisar y redirigir
    if not carrito:
        messages.info(request, "Tu carrito está vacío.")
        return redirect("ventas:carrito")

    # Variables para acumular productos y total
    items = []
    total = 0
    productos_no_disponibles = []

    # Validar cada producto del carrito
    for pid_str, datos in carrito.items():
        try:
            producto = Producto.objects.get(id=int(pid_str), activo=True)
            cantidad = min(datos["cantidad"], producto.stock)

            # Si no hay suficiente stock, avisar
            if cantidad < datos["cantidad"]:
                productos_no_disponibles.append(
                    f"{producto.nombre} (solo {producto.stock} disponibles)"
                )

            # Calcular subtotal y acumular
            subtotal = producto.precio * cantidad
            total += subtotal

            # Guardar el producto válido en la lista
            items.append({
                "producto": producto,
                "cantidad": cantidad,
                "precio": producto.precio,
            })

        except Producto.DoesNotExist:
            productos_no_disponibles.append(f"Producto ID {pid_str} (no encontrado)")

    # Si hay productos no disponibles, mostrar error y volver al carrito
    if productos_no_disponibles:
        messages.error(request, f"No se puede completar la compra: {', '.join(productos_no_disponibles)}")
        return redirect("ventas:carrito")

    # Si no hay productos válidos, mostrar error
    if not items:
        messages.error(request, "No hay productos válidos para comprar.")
        return redirect("ventas:carrito")

    # Crear el pedido con estado pendiente y fecha de expiración
    expiracion = timezone.now() + timedelta(hours=1)
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=total,
        estado="pendiente",
        expiracion=expiracion,
    )

    # Agregar los productos al pedido
    for item in items:
        pedido.items.create(
            producto=item["producto"],
            cantidad=item["cantidad"],
            precio=item["precio"],
        )

    # Preparar mensaje de WhatsApp con el resumen
    lineas = [f"{item['producto'].nombre} ×{item['cantidad']}" for item in items]
    resumen = " - ".join(lineas)
    mensaje = f"Hola, quiero finalizar mi compra (pedido #{pedido.id}): {resumen}. Total: ${total:,.0f}"
    texto_codificado = quote(mensaje)
    url_whatsapp = f"https://wa.me/573219414687?text={texto_codificado}"

    # 🔴 Vaciar el carrito de la sesión después de finalizar la compra
    if "carrito" in request.session:
        del request.session["carrito"]

    # Redirigir al enlace de WhatsApp
    return redirect(url_whatsapp)
