from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PerfilUsuario
from django.contrib.auth.decorators import user_passes_test
from .models import Producto

def index(request):
    if request.user.is_authenticated:
        return render(request, 'index_logueado.html')
    else:
        return render(request, 'index_visitante.html')

def register_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        if User.objects.filter(username=correo).exists():
            messages.error(request, "Ya existe una cuenta con ese correo.")
            return render(request, "registro.html")

        user = User.objects.create_user(username=correo, email=correo, password=password, first_name=nombre)
        PerfilUsuario.objects.create(usuario=user, nombre=nombre, telefono=telefono)
        user = authenticate(request, username=correo, password=password)
        login(request, user)
        return redirect('home')
    return render(request, "registro.html")

@login_required
def carrito_view(request):
    carrito = request.session.get('carrito', {})
    total = sum(item['precio'] * item['cantidad'] for item in carrito.values())
    return render(request, 'carrito.html', {'carrito': carrito.values(), 'total': total})

@login_required
def agregar_al_carrito(request, producto_id):
    if request.method == "POST":
        carrito = request.session.get('carrito', {})
        if str(producto_id) in carrito:
            carrito[str(producto_id)]['cantidad'] += 1
        else:
            carrito[str(producto_id)] = {
                'id': producto_id,
                'nombre': f"Producto {producto_id}",
                'precio': 25000,
                'cantidad': 1
            }
        request.session['carrito'] = carrito
        return JsonResponse({'status': 'ok', 'total_items': sum(item['cantidad'] for item in carrito.values())})
    return redirect('home')

def es_admin(user):
    return user.is_superuser

@user_passes_test(es_admin, login_url='login')
def panel_admin(request):
    productos = Producto.objects.all()
    return render(request, 'panel_admin.html', {'productos': productos})