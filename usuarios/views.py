from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Direccion

# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("productos:inicio")  # Redirige al inicio de productos
        else:
            return render(request, "login.html", {"error": "Usuario o contraseña incorrectos"})
    return render(request, "login.html")


# =========================
# REGISTRO
# =========================
def registro_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        direccion = request.POST.get("direccion")

        # Validar contraseñas
        if password1 != password2:
            return render(request, "registro.html", {"error": "Las contraseñas no coinciden"})

        # Validar si usuario ya existe
        if User.objects.filter(username=username).exists():
            return render(request, "registro.html", {"error": "El nombre de usuario ya existe"})

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Crear dirección inicial asociada al usuario
        Direccion.objects.create(
            usuario=user,
            direccion=direccion,
            ciudad="",       # Puedes pedir ciudad en el formulario si quieres
            referencia="",   # Puedes pedir referencia opcional
            principal=True
        )

        # Iniciar sesión automáticamente
        login(request, user)
        return redirect("productos:inicio")

    return render(request, "registro.html")


# =========================
# PERFIL
# =========================
def perfil_view(request):
    if not request.user.is_authenticated:
        return redirect("usuarios:login")

    direcciones = Direccion.objects.filter(usuario=request.user)
    return render(request, "perfil.html", {
        "usuario": request.user,
        "direcciones": direcciones,
    })


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect("productos:inicio")


# =========================
# AGREGAR DIRECCIÓN
# =========================
def agregar_direccion(request):
    if not request.user.is_authenticated:
        return redirect("usuarios:login")

    if request.method == "POST":
        Direccion.objects.create(
            usuario=request.user,
            direccion=request.POST.get("direccion"),
            ciudad=request.POST.get("ciudad", ""),
            referencia=request.POST.get("referencia", ""),
            principal=False
        )
        return redirect("usuarios:perfil")

    return render(request, "direccion_form.html")


# =========================
# ELIMINAR DIRECCIÓN
# =========================
def eliminar_direccion(request, direccion_id):
    if not request.user.is_authenticated:
        return redirect("usuarios:login")

    direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
    direccion.delete()
    return redirect("usuarios:perfil")