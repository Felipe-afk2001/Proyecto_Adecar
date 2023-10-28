from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  # Redirige a la vista de inicio después del inicio de sesión
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def inicio (request):
    return render(request, 'inicio.html')

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

def cotizacion_manual (request):
    return render(request, 'cotizacion_manual.html')

