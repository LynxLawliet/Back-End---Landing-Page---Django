"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
from .views import cerrar_sesion, diagnosticos, home, iniciar_sesion, menu_administrador, registro

def temp_home(request):
    return HttpResponse("<h1>Landing Page - Torque Motor</h1><p>¡La página de inicio está funcionando!</p>")

urlpatterns = [
    path('', temp_home, name='home'),
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='login'),
    path('logout/', cerrar_sesion, name='logout'),
    path('menu-administrador/', menu_administrador, name='menu_administrador'),
    path('menu-administrador/diagnosticos/', diagnosticos, name='diagnosticos'),
    path('admin/', admin.site.urls),
]
