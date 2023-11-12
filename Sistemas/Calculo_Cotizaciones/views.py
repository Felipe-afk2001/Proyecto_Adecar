from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from Calculo_Cotizaciones.models import Parametro #Para hacer las validaciones de los parámetros
from django.http import JsonResponse, HttpResponse
from Calculo_Cotizaciones.models import Tipo_Plancha
from django.db import connection
import math

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  # Redirige a la vista de inicio después del inicio de sesión
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home (request):
    return render(request, 'home.html')

def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'La cuenta ha sido creada para {username}')
            return redirect('login')  # Puedes cambiar 'login' por la URL de inicio de sesión de tu aplicación
    else:
        form = UserCreationForm()
    return render(request, 'registrar.html', {'form': form})


"""
Selección de plancha a utilizar
"""

# def seleccionar_plancha(largo_hm, media_hm, ancho_hm, tipo_carton):
#     # Consulta SQL para plancha que acomode hoja madre más al menos una mitad
#     sql_maximizada = """
#     SELECT * FROM Tipo_Plancha
#     WHERE largo >= %s AND largo >= %s AND ancho >= %s AND cod_carton = %s
#     ORDER BY largo, ancho
#     LIMIT 1
#     """
#     # Consulta SQL para plancha que acomode solo la hoja madre
#     sql_solo_hm = """
#     SELECT * FROM Tipo_Plancha
#     WHERE largo >= %s AND ancho >= %s AND cod_carton = %s
#     ORDER BY largo, ancho
#     LIMIT 1
#     """

#     # Ejecuta la consulta para plancha maximizada
#     with connection.cursor() as cursor:
#         cursor.execute(sql_maximizada, [largo_hm + media_hm, largo_hm, ancho_hm, tipo_carton])
#         result = cursor.fetchone()

#         # Si no se encuentra una plancha maximizada, busca una para solo la hoja madre
#         if not result:
#             cursor.execute(sql_solo_hm, [largo_hm, ancho_hm, tipo_carton])
#             result = cursor.fetchone()

#     # Si hay un resultado, convertirlo en un diccionario
#     if result:
#         field_names = [col[0] for col in cursor.description]
#         plancha_seleccionada = dict(zip(field_names, result))
#         return plancha_seleccionada
#     else:
#         return None

def calcular_cajas_por_plancha(largo_hm, media_hm, ancho_hm, tipo_carton):
    # Escribe la consulta SQL para encontrar la plancha más adecuada
    sql = """
    SELECT *, 
           (FLOOR(largo / %s) * FLOOR(ancho / %s)) AS cajas_enteras,  -- Cajas enteras
           FLOOR((largo %% %s) / %s) AS mitades_adicionales  -- Mitades adicionales
    FROM Tipo_Plancha
    WHERE cod_carton = %s
    ORDER BY cajas_enteras DESC, mitades_adicionales DESC, largo, ancho
    LIMIT 1
    """

    # Ejecuta la consulta
    with connection.cursor() as cursor:
        cursor.execute(sql, [largo_hm, ancho_hm, largo_hm, media_hm, tipo_carton])
        result = cursor.fetchone()

    # Si hay un resultado, convertirlo en un diccionario y calcular el total de cajas
    if result:
        field_names = [col[0] for col in cursor.description]
        plancha_seleccionada = dict(zip(field_names, result))
        total_cajas = plancha_seleccionada['cajas_enteras'] + (plancha_seleccionada['mitades_adicionales'] if 'mitades_adicionales' in plancha_seleccionada else 0)
        return plancha_seleccionada, total_cajas
    else:
        return None, 0


"""
-----------------------------------------------------------------------------
VISTAS DE COTIZACIÓN MANUAL
-----------------------------------------------------------------------------
"""

def cotizacion_manual (request):
    return render(request, 'cotizacion_manual.html')

def procesar_datos(request):
    mensaje_error = None #inicializador
    if request.method == 'POST':
        largo = float(request.POST.get('largo'))
        largostr = request.POST.get('largo')
        ancho = float(request.POST.get('ancho'))
        anchostr = request.POST.get('ancho')
        alto = float(request.POST.get('alto'))
        altostr = request.POST.get('alto')
        cantidad = int(request.POST.get('cantidad_cajas'))
        tipo_carton = request.POST.get('tipo_carton').upper()

        """
        Calcula largo de hoja
        """
        la1=largo+3
        la2=ancho+5
        la3=largo+5
        la4=ancho+3
        la5=40 #Aleta
        largo1=la1+la2+la3+la4+la5
        largo2=la1+la2+la5 #media
        """
        Calcula ancho de hoja
        """
        an1=(ancho/2)+3
        an2=alto+5
        an3=(ancho/2)+3
        ancho1=an1+an2+an3

        """
        Calcula hoja madre
        """
        largo_hm = largo1
        ancho_hm = ancho1
        media_hm = largo2

        # Verifica los tipos de datos
        print("Tipo de largo_hm:", type(largo_hm))
        print("Tipo de ancho_hm:", type(ancho_hm))
        print("Tipo de tipo_carton:", type(tipo_carton))

        largo_hm_str = str(math.trunc(largo_hm))
        ancho_hm_str = str(math.trunc(ancho_hm))
        media_hm_str = str(math.trunc(media_hm))

        """
        Seleccionar plancha
        """
        # plancha_necesaria = seleccionar_plancha(largo_hm, media_hm, ancho_hm, tipo_carton)

        plancha_seleccionada, total_cajas_por_plancha = calcular_cajas_por_plancha(largo_hm, media_hm, ancho_hm, tipo_carton)
        print(total_cajas_por_plancha)

        

        """
        Excedentes de plancha
        """
        largo_plancha = plancha_seleccionada.get('largo')
        ancho_plancha = plancha_seleccionada.get('ancho')

        # Calcula cuántas cajas caben en el ancho de la plancha (solo enteras)
        cajas_en_ancho = ancho_plancha // ancho_hm

        # Calcula cuántas cajas caben en el largo de la plancha (enteras y mitades)
        cajas_enteras_en_largo = largo_plancha // largo_hm
        espacio_restante = largo_plancha % largo_hm
        cajas_en_largo = cajas_enteras_en_largo
        if espacio_restante >= media_hm:
            cajas_en_largo += 0.5  # Añade media caja si hay espacio

        # Calcula el espacio total ocupado por las cajas en el largo y ancho
        espacio_ocupado_en_ancho = cajas_en_ancho * ancho_hm
        espacio_ocupado_en_largo = (cajas_enteras_en_largo * largo_hm) + (media_hm if espacio_restante >= media_hm else 0)
        excedente_horizontal = ancho_plancha - espacio_ocupado_en_ancho
        excedente_vertical = largo_plancha - espacio_ocupado_en_largo

        # """
        # Cálculo de cajas por plancha
        # """
        # largo_plancha = plancha_seleccionada.get('largo')
        # ancho_plancha = plancha_seleccionada.get('ancho')

        # # Calcula cuántas cajas caben en el ancho de la plancha (solo enteras)
        # cajas_en_ancho = ancho_plancha // ancho_hm

        #  # Calcula cuántas cajas caben en el largo de la plancha (enteras y mitades)
        # cajas_enteras_en_largo = largo_plancha // largo_hm
        # espacio_restante = largo_plancha % largo_hm
        # cajas_en_largo = cajas_enteras_en_largo
        # if espacio_restante >= largo_hm / 2:
        #     cajas_en_largo += 0.5  # Añade media caja si hay espacio
        
        # # Calcula el total de cajas que caben en una plancha
        # total_cajas_por_plancha = cajas_en_ancho + cajas_en_largo

        # if cajas_en_ancho == 1 and cajas_en_largo == 1:
        #     total_cajas_por_plancha = 1

        """
        Porcentajes de venta a cargar en próxima plantilla
        """
        porcentajes = list(range(5, 105, 5)) 

        """
        Validación de medida contra tabla de parámetros
        (Podríamos agregar confirmación ya que se pueden ingresar más parámetros)
        """
        parametros = Parametro.objects.first()
        if largo1 > parametros.largo_maximo or ancho1 > parametros.ancho_maximo:
            mensaje_error = "Medidas inválidas. Por favor, vuelva e ingrese otro valor."
    if mensaje_error:
        return render(request, 'cotizacion_manual.html', {'mensaje_error': mensaje_error})
    else:
        return render(request, 'calculo_de_precio.html',{'largo':largo,
                                                          'ancho':ancho,
                                                          'alto':alto,
                                                          'cantidad':cantidad,
                                                          'tipo_carton':tipo_carton,
                                                          'porcentajes':porcentajes,
                                                          'largostr':largostr,
                                                          'anchostr':anchostr,
                                                          'altostr':altostr,
                                                          'largo_hm':largo_hm,
                                                          'ancho_hm':ancho_hm,
                                                          'media_hm':media_hm,
                                                          'largo_hm_str':largo_hm_str,
                                                          'ancho_hm_str':ancho_hm_str,
                                                          'media_hm_str':media_hm_str,
                                                          'plancha_necesaria':plancha_seleccionada,
                                                          'excedente_vertical':excedente_vertical,
                                                          'excedente_horizontal':excedente_horizontal,
                                                          'total_cajas_por_plancha': total_cajas_por_plancha,})

def calculo_de_precio(request):
    return render(request, 'calculo_de_precio.html')
