from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test

# Contador del carrito
def carrito_cantidad(request):
    carrito = request.session.get('carrito', {})
    return sum(item['cantidad'] for item in carrito.values())

# Página principal
def home(request):
    productos = Producto.objects.filter(activo=True)
    context = {
        'productos': productos,
        'cart_count': carrito_cantidad(request)
    }
    if request.user.is_authenticated:
        return render(request, 'index_logueado.html', context)
    else:
        return render(request, 'index_visitante.html', context)

# Agregar al carrito
@login_required
def agregar_carrito(request, id):
    p = get_object_or_404(Producto, id=id, activo=True)
    if p.stock <= 0:
        messages.error(request, f"{p.nombre} está agotado")
        return redirect('home')
    
    carrito = request.session.get('carrito', {})
    pid = str(id)
    if pid in carrito:
        if carrito[pid]['cantidad'] < p.stock:
            carrito[pid]['cantidad'] += 1
        else:
            messages.warning(request, "No hay más stock")
    else:
        carrito[pid] = {'precio': p.precio, 'cantidad': 1}
    request.session['carrito'] = carrito
    messages.success(request, "¡Agregado al carrito!")
    return redirect('home')

# Carrito
@login_required
def carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for pid, data in carrito.items():
        producto = get_object_or_404(Producto, id=int(pid))
        subtotal = data['precio'] * data['cantidad']
        items.append({
            'id': pid,
            'nombre': producto.nombre,
            'precio': data['precio'],
            'cantidad': data['cantidad'],
            'subtotal': subtotal,
            'stock': producto.stock
        })
        total += subtotal
    return render(request, 'carrito.html', {
        'carrito': items,
        'total': total,
        'cart_count': carrito_cantidad(request)
    })

# Eliminar del carrito
@login_required
def eliminar_carrito(request, id):
    carrito = request.session.get('carrito', {})
    pid = str(id)
    if pid in carrito:
        del carrito[pid]
        request.session['carrito'] = carrito
    return redirect('carrito')
@login_required
def carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for pid, data in carrito.items():
        producto = get_object_or_404(Producto, id=int(pid))
        subtotal = data['precio'] * data['cantidad']
        items.append({
            'id': pid,
            'nombre': producto.nombre,
            'precio': data['precio'],
            'cantidad': data['cantidad'],
            'subtotal': subtotal,
            'stock': producto.stock,
            'imagen': producto.imagen  # ← NUEVO: enviamos la imagen
        })
        total += subtotal
    return render(request, 'carrito.html', {
        'carrito': items,
        'total': total,
        'cart_count': carrito_cantidad(request)
    })
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})
def es_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(es_admin, login_url='home')
def panel_admin(request):
    productos = Producto.objects.all().order_by('-creado_en')
    return render(request, 'panel_admin.html', {'productos': productos})

