from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import CustomAuthenticationForm

def inicio (request):
    return render(request, 'inicio.html')

class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    
@login_required
def home (request):
    return render(request, 'home.html')


