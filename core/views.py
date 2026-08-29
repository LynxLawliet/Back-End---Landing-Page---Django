import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.contrib.admin.views.decorators import staff_member_required


def guardar_registro(datos):
    datos['created_at'] = datetime.now(timezone.utc).isoformat()
    ruta = Path(settings.BASE_DIR) / 'landingpage_data.json'
    registros = []

    if ruta.exists():
        try:
            with ruta.open('r', encoding='utf-8') as archivo:
                registros = json.load(archivo)
            if not isinstance(registros, list):
                registros = [registros]
        except (json.JSONDecodeError, OSError):
            registros = []

    registros.append(datos)
    with NamedTemporaryFile(
        mode='w', encoding='utf-8', dir=ruta.parent, delete=False
    ) as archivo_temporal:
        json.dump(registros, archivo_temporal, ensure_ascii=False, indent=2)
        archivo_temporal.flush()
        os.fsync(archivo_temporal.fileno())
        ruta_temporal = Path(archivo_temporal.name)
    ruta_temporal.replace(ruta)


def cargar_registros():
    ruta = Path(settings.BASE_DIR) / 'landingpage_data.json'
    if not ruta.exists():
        return []
    try:
        with ruta.open('r', encoding='utf-8') as archivo:
            registros = json.load(archivo)
        return registros if isinstance(registros, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def guardar_registros(registros):
    ruta = Path(settings.BASE_DIR) / 'landingpage_data.json'
    with NamedTemporaryFile(
        mode='w', encoding='utf-8', dir=ruta.parent, delete=False
    ) as archivo_temporal:
        json.dump(registros, archivo_temporal, ensure_ascii=False, indent=2)
        archivo_temporal.flush()
        os.fsync(archivo_temporal.fileno())
        ruta_temporal = Path(archivo_temporal.name)
    ruta_temporal.replace(ruta)


def home(request):
    mensaje = None

    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'cita')
        campos = ('nombre', 'telefono', 'fecha', 'servicio', 'descripcion')
        if tipo == 'diagnostico':
            campos = ('nombre', 'vehiculo', 'problema')
        datos = {campo: request.POST.get(campo, '').strip()[:500] for campo in campos}

        if all(datos.values()):
            datos['tipo'] = tipo
            guardar_registro(datos)

            mensaje = 'Tu solicitud fue registrada correctamente.'
        else:
            mensaje = 'Completa todos los campos para enviar la solicitud.'

    return render(request, 'index.html', {
        'mensaje': mensaje,
        'contenido': cargar_contenido(),
    })


def registro(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    username = request.POST.get('username', '').strip()[:150]
    email = request.POST.get('email', '').strip()[:254]
    password = request.POST.get('password', '')
    password_confirmation = request.POST.get('password_confirmation', '')

    try:
        validate_email(email)
        validate_password(password, user=User(username=username, email=email))
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        if not username or not password:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
        elif password != password_confirmation:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ese nombre de usuario ya está registrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('home')

    return redirect('home')


def iniciar_sesion(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    username = request.POST.get('username', '').strip()[:150]
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, 'Sesión iniciada correctamente.')
    else:
        messages.error(request, 'Usuario o contraseña incorrectos.')

    return redirect('home')


def cerrar_sesion(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('home')


CONTENIDO_POR_DEFECTO = {
    'eyebrow': 'Mecánica automotriz profesional',
    'titulo': 'Tu vehículo, en manos expertas.',
    'descripcion': 'Diagnóstico preciso, mantenimiento preventivo y reparación integral para mantener tu auto seguro, eficiente y listo para cada recorrido.',
    'telefono': '+52 (55) 1234-5678',
    'correo': 'contacto@torkemotor.com',
    'direccion': 'Av. Industrial 245, Centro',
}


def cargar_contenido():
    ruta = Path(settings.BASE_DIR) / 'landingpage_content.json'
    contenido = CONTENIDO_POR_DEFECTO.copy()
    if ruta.exists():
        try:
            with ruta.open('r', encoding='utf-8') as archivo:
                guardado = json.load(archivo)
            if isinstance(guardado, dict):
                contenido.update({clave: str(valor)[:500] for clave, valor in guardado.items()})
        except (json.JSONDecodeError, OSError):
            pass
    return contenido


@staff_member_required(login_url='/')
def menu_administrador(request):
    contenido = cargar_contenido()
    if request.method == 'POST':
        campos = tuple(CONTENIDO_POR_DEFECTO)
        actualizado = {
            campo: request.POST.get(campo, '').strip()[:500]
            for campo in campos
        }
        if all(actualizado.values()):
            ruta = Path(settings.BASE_DIR) / 'landingpage_content.json'
            with NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=ruta.parent, delete=False
            ) as archivo_temporal:
                json.dump(actualizado, archivo_temporal, ensure_ascii=False, indent=2)
                archivo_temporal.flush()
                os.fsync(archivo_temporal.fileno())
                ruta_temporal = Path(archivo_temporal.name)
            ruta_temporal.replace(ruta)
            messages.success(request, 'Contenido actualizado correctamente.')
            return redirect('menu_administrador')
        messages.error(request, 'Todos los campos son obligatorios.')
        contenido = actualizado

    return render(request, 'admin_menu.html', {'contenido': contenido})


@staff_member_required(login_url='/')
def diagnosticos(request):
    registros = cargar_registros()
    solicitudes = [
        (indice, registro)
        for indice, registro in enumerate(registros)
        if registro.get('tipo') == 'diagnostico'
    ]

    if request.method == 'POST':
        try:
            indice = int(request.POST.get('indice', ''))
        except ValueError:
            indice = -1
        resultado = request.POST.get('resultado', '').strip()[:1000]
        estado = request.POST.get('estado', 'Pendiente').strip()[:50]

        if indice < 0 or indice >= len(registros) or registros[indice].get('tipo') != 'diagnostico':
            messages.error(request, 'La solicitud de diagnóstico no es válida.')
        elif not resultado:
            messages.error(request, 'Escribe el resultado del diagnóstico.')
        else:
            registros[indice]['resultado'] = resultado
            registros[indice]['estado'] = estado or 'Pendiente'
            registros[indice]['updated_at'] = datetime.now(timezone.utc).isoformat()
            guardar_registros(registros)
            messages.success(request, 'Diagnóstico actualizado correctamente.')
        return redirect('diagnosticos')

    return render(request, 'diagnosticos.html', {'solicitudes': solicitudes})
