# joyeria/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from .models import PerfilUsuario

# Create your views here.


def register_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        telefono = request.POST.get("telefono")
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        # Validación: ¿ya existe el usuario?
        if User.objects.filter(username=correo).exists():
            messages.error(request, "Ya existe una cuenta con ese correo electrónico.")
            return render(request, "registro.html")

        # Crear usuario
        user = User.objects.create_user(
            username=correo,
            email=correo,
            password=password,
            first_name=nombre
        )

        # Crear perfil
        perfil = PerfilUsuario.objects.create(
            usuario=user,
            nombre=nombre,
            telefono=telefono
        )

        # Autenticar e iniciar sesión
        user = authenticate(request, username=correo, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect("home")  # Cambia "home" por tu vista principal
        else:
            messages.error(request, "Hubo un error al iniciar sesión.")
            return render(request, "registro.html")

    return render(request, "registro.html")



