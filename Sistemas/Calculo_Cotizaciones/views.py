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
import requests
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
Seleccionar parámetros
"""
def parametros_excedentes():
    try:
        parametro = Parametro.objects.get(id_parametro=1)
        return parametro.excedente_horizontal, parametro.excedente_vertical
    except Parametro.DoesNotExist:
        # Manejar el caso en que el registro con id=1 no exista
        return None, None

"""
Selección de plancha a utilizar
"""

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

        """
        Porcentajes de venta a cargar en próxima plantilla
        """
        porcentajes = list(range(5, 105, 5))

        """
        Validación de medida contra tabla de parámetros
        """
        parametros = Parametro.objects.first()
        if largo1 > parametros.largo_maximo or ancho1 > parametros.ancho_maximo:
            mensaje_error = "Medidas inválidas. Por favor, vuelva e ingrese otro valor."

        """
        Costo de excedentes
        """
        def calcular_costo_excedentes(excedente_vert, excedente_horiz, costo_plancha, area_plancha, umbral_vertical, umbral_horizontal):
            costo_excedente_vertical = 0
            costo_excedente_horizontal = 0

            # Costo del excedente horizontal
            if excedente_horiz > umbral_horizontal:
                area_excedente_horizontal = excedente_horiz * ancho_plancha
                proporcion_horizontal = area_excedente_horizontal / area_plancha
                costo_excedente_horizontal = costo_plancha * proporcion_horizontal

            # Costo del excedente vertical
            if excedente_vert > umbral_vertical:
                area_excedente_vertical = excedente_vert * ancho_plancha
                proporcion_vertical = area_excedente_vertical / area_plancha
                costo_excedente_vertical = costo_plancha * proporcion_vertical

            return costo_excedente_vertical, costo_excedente_horizontal

        


        """
        Llamada a la API
        """
        coste_materia = plancha_seleccionada.get('precio_proveedor')
        api_calculo(largo, ancho, alto, largo_plancha, ancho_plancha, coste_materia, 100, cantidad)
        precio_unidad = 100

        """
        Llamada costo excedentes
        """
        excedente_horizontal_param, excedente_vertical_param = parametros_excedentes()
        area_plancha_bd = plancha_seleccionada.get('area')
        costo_ex_vertical, costo_ex_horizontal = calcular_costo_excedentes(
            excedente_vert=excedente_vertical, 
            excedente_horiz=excedente_horizontal,
            costo_plancha=coste_materia, 
            area_plancha=area_plancha_bd,
            umbral_vertical=excedente_vertical_param,
            umbral_horizontal=excedente_horizontal_param
        )

        """
        Costo por unidad
        """
        # Asumiendo que total_cajas_por_plancha es el número total de cajas por plancha
        coste_total_plancha = coste_materia - (costo_ex_vertical + costo_ex_horizontal)
        costo_por_unidad = coste_total_plancha / total_cajas_por_plancha

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
                                                          'total_cajas_por_plancha': total_cajas_por_plancha,
                                                          'precio_base':precio_unidad,
                                                          'costo_ex_vertical':round(costo_ex_vertical),
                                                          'costo_ex_horizontal':round(costo_ex_horizontal),
                                                          'costo_por_unidad':round(costo_por_unidad),})

def calculo_de_precio(request):
    return render(request, 'calculo_de_precio.html')

def api_calculo(largo, ancho, alto, largo_plancha, ancho_plancha,coste_materia, porcentaje_utilidad, cantidad):
    """
    Llamada a la api
    """
    # URL de tu API
    url = 'http://localhost:8000/calcular/'
    token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5' #Token debe ser por consulta, está en la bd.

    headers = {
        'Authorization': f'Token {token}'
    }

    # Datos para enviar en la petición POST
    datos_prueba = {
        'largo_caja': largo,
        'ancho_caja': ancho,
        'alto_caja': alto,
        'largo_plancha': largo_plancha,
        'ancho_plancha': ancho_plancha,
        'coste_materia': coste_materia,
        'porcentaje_utilidad': 0, #Usar la del form
        'coste_creacion': 200, #Costo fijo
        'cantidad_caja': cantidad
    }

    # Realizar la petición POST
    respuesta = requests.post(url, json=datos_prueba, headers=headers)

    # Verificar la respuesta
    print(f'Estado de la respuesta: {respuesta.status_code}')
    if respuesta.status_code == 200:
        print("PDF generado exitosamente.")
        # Aquí puedes manejar el PDF, por ejemplo, guardarlo en un archivo
        with open('cotizacion.pdf', 'wb') as f:
            f.write(respuesta.content)
        import webbrowser
        webbrowser.open_new('cotizacion.pdf')
