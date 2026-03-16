from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto, Categoria
from usuarios.models import User
from ventas.models import Pedido, PedidoProducto
from django.db.models import Sum, F, ExpressionWrapper, DecimalField, Avg, Count
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django import forms
from django.contrib import messages
from usuarios.models import Direccion

# Decorador que restringe a superusuarios
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

# -------------------------------
# Productos
# -------------------------------
@superuser_required
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, "dashboard/productos.html", {"productos": productos})

@superuser_required
def admin_agregar_producto(request):
    from .forms import ProductoForm
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("dashboard:productos")
    else:
        form = ProductoForm()
    categorias = Categoria.objects.all()
    return render(request, "dashboard/producto_form.html", {"form": form, "categorias": categorias})

@superuser_required
def admin_editar_producto(request, producto_id):
    from .forms import ProductoForm
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect("dashboard:productos")
    else:
        form = ProductoForm(instance=producto)
    categorias = Categoria.objects.all()
    return render(request, "dashboard/producto_form.html", {"form": form, "categorias": categorias, "producto": producto})

@superuser_required
def admin_eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect("dashboard:productos")

# -------------------------------
# Clientes
# -------------------------------
class ClienteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active"]

@superuser_required
def clientes_view(request):
    clientes = User.objects.all().order_by("-date_joined")
    return render(request, "dashboard/clientes.html", {"clientes": clientes})

@superuser_required
def admin_detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(User, id=cliente_id)
    return render(request, "dashboard/detalle_cliente.html", {"cliente": cliente})

@superuser_required
def admin_editar_cliente(request, cliente_id):
    cliente = get_object_or_404(User, id=cliente_id)
    if request.method == "POST":
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect("dashboard:clientes")
    else:
        form = ClienteForm(instance=cliente)
    return render(request, "dashboard/editar_cliente.html", {"form": form, "cliente": cliente})

# -------------------------------
# Estadísticas completas
# -------------------------------
@superuser_required
def estadisticas_view(request):
    hoy = timezone.now().date()
    mes = timezone.now().month
    anio = timezone.now().year

    # Ventas
    ventas_totales = Pedido.objects.aggregate(Sum("total"))["total__sum"] or 0
    total_pedidos = Pedido.objects.count()
    ticket_medio = ventas_totales / total_pedidos if total_pedidos > 0 else 0
    ventas_mes = Pedido.objects.filter(fecha_creacion__month=mes).aggregate(Sum("total"))["total__sum"] or 0
    ventas_anio = Pedido.objects.filter(fecha_creacion__year=anio).aggregate(Sum("total"))["total__sum"] or 0

    productos_top = (
        Producto.objects.annotate(
            unidades_vendidas=Sum("pedidoproducto__cantidad"),
            ingresos=Sum(
                ExpressionWrapper(
                    F("pedidoproducto__cantidad") * F("pedidoproducto__precio"),
                    output_field=DecimalField()
                )
            ),
        )
        .filter(unidades_vendidas__gt=0)
        .order_by("-unidades_vendidas")[:5]
    )

    pedidos_recientes = Pedido.objects.order_by("-fecha_creacion")[:5]

    # Clientes
    total_clientes = User.objects.count()
    clientes_mes = User.objects.filter(date_joined__month=mes).count()
    clientes_recurrentes = User.objects.annotate(num_pedidos=Count("pedido")).filter(num_pedidos__gt=1).count()
    clientes_nuevos = User.objects.annotate(num_pedidos=Count("pedido")).filter(num_pedidos=1).count()

    # Inventario
    productos_totales = Producto.objects.count()
    productos_activos = Producto.objects.filter(activo=True).count()
    productos_inactivos = Producto.objects.filter(activo=False).count()
    productos_agotados = Producto.objects.filter(stock=0).count()
    productos_bajo_stock = Producto.objects.filter(stock__lt=5).count()
    valor_total_inventario = Producto.objects.aggregate(valor=Sum(F("stock") * F("precio")))["valor"] or 0
    stock_por_categoria = Categoria.objects.annotate(total_stock=Sum("productos__stock"))

    # Alertas
    sin_ventas = Producto.objects.filter(pedidoproducto__isnull=True)
    pedidos_pendientes = Pedido.objects.filter(estado="pendiente", expiracion__lt=timezone.now())

    return render(request, "dashboard/estadisticas.html", {
        # Ventas
        "ventas_totales": ventas_totales,
        "ventas_mes": ventas_mes,
        "ventas_anio": ventas_anio,
        "total_pedidos": total_pedidos,
        "ticket_medio": ticket_medio,
        "productos_top": productos_top,
        "pedidos_recientes": pedidos_recientes,
        # Clientes
        "total_clientes": total_clientes,
        "clientes_mes": clientes_mes,
        "clientes_recurrentes": clientes_recurrentes,
        "clientes_nuevos": clientes_nuevos,
        # Inventario
        "productos_totales": productos_totales,
        "productos_activos": productos_activos,
        "productos_inactivos": productos_inactivos,
        "productos_agotados": productos_agotados,
        "productos_bajo_stock": productos_bajo_stock,
        "valor_total_inventario": valor_total_inventario,
        "stock_por_categoria": stock_por_categoria,
        # Alertas
        "sin_ventas": sin_ventas,
        "pedidos_pendientes": pedidos_pendientes,
    })

# -------------------------------
# Pedidos
# -------------------------------
@superuser_required
def pedidos_view(request):
    pedidos = Pedido.objects.all().order_by("-fecha_creacion")
    return render(request, "dashboard/pedidos.html", {"pedidos": pedidos})

@superuser_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    cliente = pedido.usuario  # Suponiendo que tu modelo Pedido tiene 'usuario = ForeignKey(User)'
    
    # Obtener la dirección principal del cliente (si existe)
    direccion = Direccion.objects.filter(usuario=cliente, principal=True).first()
    
    return render(request, "dashboard/detalle_pedido.html", {
        "pedido": pedido,
        "cliente": cliente,
        "direccion": direccion,
    })
@superuser_required
def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    for item in pedido.items.all():
        productos = item.producto
        if productos.stock >= item.cantidad:
            productos.stock -= item.cantidad
            productos.save()
        else:
            messages.error(request, f"Stock insuficiente para {productos.nombre}")
            return redirect("dashboard:pedidos")
    pedido.estado = "confirmado"
    pedido.save()
    return redirect("dashboard:pedidos")

@superuser_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = "cancelado"
    pedido.save()
    return redirect("dashboard:pedidos")

# -------------------------------
# Dashboard principal
# -------------------------------
@superuser_required
def dashboard_home(request):
    return render(request, "dashboard/dashboard.html")
