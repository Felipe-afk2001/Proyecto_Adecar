from django.contrib import admin
from django.urls import path, include
from Calculo_auto import views as ca_views
from Calculo_Cotizaciones import views as cc_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main_calculo_cotizaciones/', cc_views.home2, name='main_calculo_cotizaciones'),
    path('main_calculo_auto/', ca_views.home1, name='main_calculo_auto'),
]
