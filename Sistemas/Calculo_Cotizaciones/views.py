from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from Calculo_Cotizaciones.models import Parametro #Para hacer las validaciones de los parámetros
from django.http import JsonResponse, HttpResponse

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
    mensaje_error = None #inicializador
    if request.method == 'POST':
        largo = float(request.POST.get('largo'))
        ancho = float(request.POST.get('ancho'))
        alto = float(request.POST.get('alto'))
        tipo_carton = request.POST.get('tipo_carton')

        """
        Calcula largo de hoja
        """
        la1=largo+3
        la2=ancho+5
        la3=largo+5
        la4=ancho+3
        la5=40 #Aleta
        largo1=la1+la2+la3+la4+la5
        largo2=la1+la2+la5 #media
        """
        Calcula ancho de hoja
        """
        an1=(ancho/2)+3
        an2=alto+5
        an3=(ancho/2)+3
        ancho1=an1+an2+an3

        """
        Porcentajes de venta a cargar en próxima plantilla
        """
        porcentajes = list(range(5, 105, 5)) # Asegúrate de que el 105 está fuera del rango para incluir el 100

        """
        Validación de medida contra tabla de parámetros
        (Podríamos agregar confirmación ya que se pueden ingresar más parámetros)
        """
        parametros = Parametro.objects.first()
        if largo1 > parametros.largo_maximo or ancho1 > parametros.ancho_maximo:
            mensaje_error = "Medidas inválidas. Por favor, vuelva e ingrese otro valor."
    if mensaje_error:
        return render(request, 'cotizacion_manual.html', {'mensaje_error': mensaje_error})
    else:
        return render(request, 'calculo_de_precio.html',{'largo':largo, 'ancho':ancho, 'alto':alto, 'tipo_carton':tipo_carton, 'porcentajes':porcentajes})

def calculo_de_precio(request):
    return render(request, 'calculo_de_precio.html')
