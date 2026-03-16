from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from productos.models import Categoria, Producto
from usuarios.models import Direccion, User
from ventas.models import Pedido


# Decorador que restringe a superusuarios
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


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
    return render(
        request,
        "dashboard/producto_form.html",
        {"form": form, "categorias": categorias, "producto": producto},
    )


@superuser_required
def admin_eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect("dashboard:productos")


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


@superuser_required
def estadisticas_view(request):
    ahora = timezone.now()

    pedidos_confirmados = Pedido.objects.filter(estado="confirmado")
    pedidos_mes = pedidos_confirmados.filter(fecha_creacion__year=ahora.year, fecha_creacion__month=ahora.month)

    ingresos_totales = pedidos_confirmados.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]
    ingresos_mes = pedidos_mes.aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))["total"]

    total_pedidos = Pedido.objects.count()
    total_ventas_realizadas = pedidos_confirmados.count()
    total_productos = Producto.objects.count()
    total_clientes = User.objects.count()

    promedio_venta_por_pedido = (
        ingresos_totales / total_ventas_realizadas if total_ventas_realizadas else Decimal("0.00")
    )

    dias_transcurridos = ahora.day
    promedio_ventas_dia_mes_actual = ingresos_mes / dias_transcurridos if dias_transcurridos else Decimal("0.00")


    productos_mas_vendidos = (
        Producto.objects.annotate(
            unidades_vendidas=Coalesce(
                Sum("pedidoproducto__cantidad", filter=Q(pedidoproducto__pedido__estado="confirmado")),
                0,
            )
        )
        .order_by("-unidades_vendidas", "nombre")[:5]
    )

    productos_menos_vendidos = (
        Producto.objects.annotate(
            unidades_vendidas=Coalesce(
                Sum("pedidoproducto__cantidad", filter=Q(pedidoproducto__pedido__estado="confirmado")),
                0,
            )
        )
        .order_by("unidades_vendidas", "nombre")[:5]
    )

    destacados_mas_vendidos = (
        Producto.objects.filter(destacado=True)
        .annotate(
            unidades_vendidas=Coalesce(
                Sum("pedidoproducto__cantidad", filter=Q(pedidoproducto__pedido__estado="confirmado")),
                0,
            )
        )
        .order_by("-unidades_vendidas", "nombre")[:5]
    )

    return render(
        request,
        "dashboard/estadisticas.html",
        {
            "ingresos_totales": ingresos_totales,
            "ingresos_mes": ingresos_mes,
            "total_productos": total_productos,
            "total_pedidos": total_pedidos,
            "total_ventas_realizadas": total_ventas_realizadas,
            "total_clientes": total_clientes,
            "promedio_venta_por_pedido": promedio_venta_por_pedido,
            "promedio_ventas_dia_mes_actual": promedio_ventas_dia_mes_actual,
            "productos_mas_vendidos": productos_mas_vendidos,
            "productos_menos_vendidos": productos_menos_vendidos,
            "destacados_mas_vendidos": destacados_mas_vendidos,
        },
    )


@superuser_required
def pedidos_view(request):
    pedidos = Pedido.objects.all().order_by("-fecha_creacion")
    return render(request, "dashboard/pedidos.html", {"pedidos": pedidos})


@superuser_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    cliente = pedido.usuario
    direccion = Direccion.objects.filter(usuario=cliente, principal=True).first()
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


@superuser_required
def dashboard_home(request):
    return render(request, "dashboard/dashboard.html")
