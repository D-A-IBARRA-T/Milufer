from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from productos.models import Categoria, Producto
from usuarios.models import Direccion
from ventas.models import Pedido, PedidoProducto


# Decorador que restringe a superusuarios
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# -------------------------------
# Productos
# -------------------------------
@superuser_required
def productos_view(request):
    productos = Producto.objects.select_related("categoria").all().order_by("-creado")
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

    return render(request, "dashboard/producto_form.html", {"form": form})


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

    return render(request, "dashboard/producto_form.html", {"form": form, "producto": producto})


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
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    pedidos_qs = Pedido.objects.all()
    pedidos_confirmados = pedidos_qs.filter(estado="confirmado")

    total_productos = Producto.objects.count()
    total_pedidos = pedidos_qs.count()
    total_ventas = pedidos_confirmados.count()
    total_clientes = User.objects.count()

    ingresos_totales = pedidos_confirmados.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    ventas_mes = pedidos_confirmados.filter(fecha_creacion__gte=month_start).aggregate(
        total=Coalesce(Sum("total"), Decimal("0.00"))
    )["total"]

    dias_con_ventas = (
        pedidos_confirmados.annotate(dia=TruncDate("fecha_creacion")).values("dia").distinct().count()
    )
    promedio_ventas_dia = ingresos_totales / dias_con_ventas if dias_con_ventas else Decimal("0.00")

    detalle_ventas = (
        PedidoProducto.objects.values("producto__id", "producto__nombre", "producto__destacado")
        .annotate(
            unidades_vendidas=Coalesce(Sum("cantidad"), 0),
            ingresos=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F("cantidad") * F("precio"),
                        output_field=DecimalField(max_digits=12, decimal_places=2),
                    )
                ),
                Decimal("0.00"),
            ),
        )
        .order_by("-unidades_vendidas", "producto__nombre")
    )

    productos_mas_vendidos = list(detalle_ventas[:5])
    productos_menos_vendidos = list(detalle_ventas.order_by("unidades_vendidas", "producto__nombre")[:5])
    destacados_mas_vendidos = list(
        detalle_ventas.filter(producto__destacado=True).order_by("-unidades_vendidas", "producto__nombre")[:5]
    )

    pedidos_recientes = pedidos_qs.select_related("usuario").order_by("-fecha_creacion")[:5]

    return render(
        request,
        "dashboard/estadisticas.html",
        {
            "total_productos": total_productos,
            "total_pedidos": total_pedidos,
            "total_ventas": total_ventas,
            "total_clientes": total_clientes,
            "ingresos_totales": ingresos_totales,
            "ventas_mes": ventas_mes,
            "promedio_ventas_dia": promedio_ventas_dia,
            "dias_con_ventas": dias_con_ventas,
            "productos_mas_vendidos": productos_mas_vendidos,
            "productos_menos_vendidos": productos_menos_vendidos,
            "destacados_mas_vendidos": destacados_mas_vendidos,
            "pedidos_recientes": pedidos_recientes,
        },
    )


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
    cliente = pedido.usuario
    direccion = Direccion.objects.filter(usuario=cliente, principal=True).first() if cliente else None

    return render(
        request,
        "dashboard/detalle_pedido.html",
        {
            "pedido": pedido,
            "cliente": cliente,
            "direccion": direccion,
        },
    )


@superuser_required
def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    for item in pedido.items.all():
        producto = item.producto
        if producto.stock >= item.cantidad:
            producto.stock -= item.cantidad
            producto.save()
        else:
            messages.error(request, f"Stock insuficiente para {producto.nombre}")
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
