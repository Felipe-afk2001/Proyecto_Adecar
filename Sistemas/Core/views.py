from django.shortcuts import render

#Definir las vistas de lo que queremos hacer y su lógica.

def main_menu(request):
    return render(request, 'main_menu.html', {})