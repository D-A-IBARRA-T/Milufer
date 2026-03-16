from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = "usuarios"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("registro/", views.registro_view, name="registro"),
    path("perfil/", views.perfil_view, name="perfil"),
    path("direccion/agregar/", views.agregar_direccion, name="agregar_direccion"),
    path("direccion/eliminar/<int:direccion_id>/", views.eliminar_direccion, name="eliminar_direccion"),
    path("logout/", views.logout_view, name="logout"),

    path(
    'recuperar/',
    auth_views.PasswordResetView.as_view(
        template_name="password_reset_form.html",
        email_template_name="password_reset_email.html",
        success_url=reverse_lazy('usuarios:password_reset_done')  # redirección explícita
    ),
    name='password_reset'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name='password_reset_done'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('recuperar/completo/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name='password_reset_complete'),
]
