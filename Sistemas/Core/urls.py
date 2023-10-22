from django.contrib import admin
from django.urls import path, include
from . import views
from Calculo_auto import urls
from Calculo_Cotizaciones import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('', include('Calculo_Cotizaciones.urls')),
    path('', include('Calculo_auto.urls')),
]
