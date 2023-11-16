from django.urls import path, include
from .views import home, creacion_cliente, registrar, dashboards, lista_historial, crear_plancha, login_view, eliminar_plancha, editar_plancha, lista_planchas, mantencion_planchas_form, crear_parametro, mantencion_parametros_form, cotizacion_manual, procesar_datos, calculo_de_precio, editar_parametro, eliminar_parametro, lista_parametros
from django.contrib.auth.views import LogoutView
import Calculo_Cotizaciones.dash_apps


urlpatterns = [
    path('',home, name='home'),
    path('home/', home, name='home'),
    path('registrar/', registrar, name='registrar'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('mantencion_planchas_form/', mantencion_planchas_form, name='mantencion_planchas_form'),
    path('editar_plancha/<str:id>/', editar_plancha, name='editar_plancha'),
    path('eliminar_plancha/<str:id>/', eliminar_plancha, name='eliminar_plancha'),
    path('lista_planchas', lista_planchas, name='lista_planchas'),
    path('crear_plancha/', crear_plancha, name='crear_plancha'),
    path('cotizacion_manual/', cotizacion_manual, name='cotizacion_manual'),
    path('procesar_datos/', procesar_datos, name='procesar_datos'),
    path('calculo_de_precio/', calculo_de_precio, name='calculo_de_precio'),
    path('mantencion_parametros_form/', mantencion_parametros_form, name='mantencion_parametros_form'),
    path('editar_parametro/<int:id>/', editar_parametro, name='editar_parametro'),
    path('eliminar_parametro/<int:id>/', eliminar_parametro, name='eliminar_parametro'),
    path('lista_parametros', lista_parametros, name='lista_parametros'),
    path('crear_parametro', crear_parametro, name='crear_parametro'),
    path('lista_historial', lista_historial, name='lista_historial'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('dashboards/', dashboards, name='dashboards'),
    path('creacion_cliente/', creacion_cliente, name='creacion_cliente'),
    # path('visualiza_pdf/', visualiza_pdf, name='visualiza_pdf'),   
]