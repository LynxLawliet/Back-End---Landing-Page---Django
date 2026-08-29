"""
URL configuration for core project (versión mínima).

Debe ubicarse en: core/urls_minimal.py
(junto a settings.py, asgi.py, wsgi.py)
"""

from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page
    path('', views.home, name='home'),

    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Panel administrador
    path('menu-administrador/', views.menu_administrador, name='menu_administrador'),
    path('diagnosticos/', views.diagnosticos, name='diagnosticos'),
]
