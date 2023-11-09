from django.urls import path, include
<<<<<<< HEAD
from .views import home, registrar, login_view, cotizacion_manual
=======
from .views import home, registrar, login_view, cotizacion_manual, procesar_datos, calculo_de_precio
>>>>>>> main
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('',home, name='home'),
    path('registrar/', registrar, name='registrar'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('cotizacion_manual/', cotizacion_manual, name='cotizacion_manual'),
    path('procesar_datos/', procesar_datos, name='procesar_datos'),
    path('calculo_de_precio/', calculo_de_precio, name='calculo_de_precio'),
]