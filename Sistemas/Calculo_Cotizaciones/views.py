from django.shortcuts import render

def home2 (request):
    return render(request, 'main_calculo_cotizaciones.html')
