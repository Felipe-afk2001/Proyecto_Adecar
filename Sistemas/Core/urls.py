from django.contrib import admin
from django.urls import path, include
from Calculo_Cotizaciones import views 

urlpatterns = [
    path('',include('Calculo_Cotizaciones.urls')),
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
]
