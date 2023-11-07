from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login

from django.http import HttpResponse

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  # Redirige a la vista de inicio después del inicio de sesión
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home (request):
    return render(request, 'home.html')

def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'La cuenta ha sido creada para {username}')
            return redirect('login')  # Puedes cambiar 'login' por la URL de inicio de sesión de tu aplicación
    else:
        form = UserCreationForm()
    return render(request, 'registrar.html', {'form': form})

"""
-----------------------------------------------------------------------------
VISTAS DE COTIZACIÓN MANUAL
-----------------------------------------------------------------------------
"""

def cotizacion_manual (request):
    return render(request, 'cotizacion_manual.html')

def procesar_datos(request):
    if request.method == 'POST':
        largo = float(request.POST.get('largo'))
        ancho = float(request.POST.get('ancho'))
        alto = float(request.POST.get('alto'))
        tipo_carton = request.POST.get('tipo_carton')

        calculo = largo + ancho + alto 

        # nuevo_carton = DimensionesCarton(largo=largo, ancho=ancho, alto=alto, tipo_carton=tipo_carton)
        # nuevo_carton.save()

        return HttpResponse(f"{calculo}, {tipo_carton}Datos listos para procesarlos en la siguiente fase (Falta validar contra la tabla de planchas).")
    else:
        return HttpResponse("Completa el formulario.")