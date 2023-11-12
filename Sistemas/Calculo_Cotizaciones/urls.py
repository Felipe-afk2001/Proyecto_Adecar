from django.urls import path, include
from .views import home, registrar, login_view, mantencion_parametros_form, cotizacion_manual, calculo_de_precio_2, procesar_datos, procesar_datos_2, calculo_de_precio, cotizacion_manual_2
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('',home, name='home'),
    path('registrar/', registrar, name='registrar'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cotizacion_manual/', cotizacion_manual, name='cotizacion_manual'),
    path('cotizacion_manual_2/', cotizacion_manual_2, name='cotizacion_manual_2'),
    path('procesar_datos/', procesar_datos, name='procesar_datos'),
    path('procesar_datos_2/', procesar_datos_2, name='procesar_datos_2'),
    path('calculo_de_precio/', calculo_de_precio, name='calculo_de_precio'),
    path('calculo_de_precio_2/', calculo_de_precio_2, name='calculo_de_precio_2'),
    path('mantencion_parametros_form/', mantencion_parametros_form, name='mantencion_parametros_form')
]