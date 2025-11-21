"""
URL configuration for milufer_accesorios project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# tu_proyecto/urls.py  (el del proyecto, no el de la app)
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from joyeria import views  # ← tu app

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Al abrir http://127.0.0.1:8000/ → aparece el login directamente
    path('', auth_views.LoginView.as_view(
        template_name='joyeria/login.html'
    ), name='login'),

    # 2. Después de iniciar sesión entra a la tienda real
    path('inicio/', views.index, name='index'),

    # 3. Logout → vuelve al login
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/'
    ), name='logout'),
]