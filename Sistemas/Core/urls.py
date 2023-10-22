from django.contrib import admin
from django.urls import path, include
from Calculo_auto import views as ca_views
from Calculo_Cotizaciones import views as cc_views

urlpatterns = [
    path('',include('Calculo_Cotizaciones.urls')),
    path('',include('Calculo_auto.urls')),
    path('admin/', admin.site.urls),
    path('', cc_views.inicio, name='inicio'),
    path('accounts/', include('django.contrib.auth.urls')),
]
