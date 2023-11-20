from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, authenticate
from Calculo_Cotizaciones.models import Parametro #Para hacer las validaciones de los parámetros
from django.http import JsonResponse, HttpResponse
from Calculo_Cotizaciones.models import Tipo_Plancha, Cliente, Solicitud_Cotizacion
from django.db import connection
from datetime import datetime
from django.core.paginator import Paginator
import Calculo_Cotizaciones.dash_apps
import requests
import base64
import math
from .forms import ParametroForm, PlanchaForm
import pandas as pd
from io import BytesIO

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Personaliza esta parte según tu modelo de usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirige a la vista de inicio después del inicio de sesión
        else:
            # Maneja el caso en el que la autenticación falla
            return render(request, 'login.html', {'error_message': 'Credenciales inválidas'})

    return render(request, 'login.html')

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

def estados(request, id_solicitud):
    solicitud = get_object_or_404(Solicitud_Cotizacion, id_cotizacion=id_solicitud) 
    if request.method == 'POST':
        solicitud.estado = 'Aceptado'  # Cambia el estado a 'Aceptado'
        solicitud.save()
        messages.success(request, 'La solicitud ha sido aceptada con éxito.')
        return redirect('agradecimiento')
    return render(request, 'compra.html', {'solicitud': solicitud})

def agradecimiento(request):
    return render(request, 'agradecimiento.html')

"""
dashboards
"""
def dashboards(request):
    return render(request, 'dashboard.html')

"""
Historial de cotizaciones
"""
@login_required
def lista_historial(request):
    historial_list = Solicitud_Cotizacion.objects.all()
    paginator = Paginator(historial_list, 10) # Muestra 20 registros por página

    page = request.GET.get('page')
    historial = paginator.get_page(page)

    return render(request, 'historial_de_cotizaciones.html', {'historial': historial})
"""
Descargar historial en excel
"""
@login_required
def descargar_excel_historial(request):
    # Crear un DataFrame con los datos del historial
    data = Solicitud_Cotizacion.objects.all().values()
    df = pd.DataFrame(data)

    # Convertir los datetimes a un formato sin zona horaria
    if 'fecha_cotizacion' in df:
        df['fecha_cotizacion'] = df['fecha_cotizacion'].dt.tz_localize(None)

    # Crear un buffer en memoria para el archivo Excel
    excel_buffer = BytesIO()

    # Usar ExcelWriter para escribir el DataFrame en el buffer
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    # Establecer el puntero del buffer al comienzo
    excel_buffer.seek(0)

    # Crear la respuesta HTTP con el buffer como contenido del archivo
    response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Historial_Cotizaciones_Adecar.xlsx"'

    return response
"""
Mantención de planchas
"""
@login_required
def lista_planchas(request):
    planchas = Tipo_Plancha.objects.all()
    return render(request, 'mantencion_planchas_form.html', {'planchas': planchas})

@login_required
def editar_plancha(request, id):
    plancha = get_object_or_404(Tipo_Plancha, pk=id)
    if request.method == 'POST':
        form = PlanchaForm(request.POST, instance=plancha)
        if form.is_valid():
            form.save()
            return redirect('lista_planchas')
    else:
        form = PlanchaForm(instance=plancha)
    return render(request, 'editar_planchas.html', {'form': form, 'plancha': plancha})

@login_required
def eliminar_plancha(request, id):
    plancha = get_object_or_404(Tipo_Plancha, pk=id)
    plancha.delete()
    return redirect('lista_planchas')

@login_required
def crear_plancha(request):
    if request.method == 'POST':
        form = PlanchaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_planchas')
    else:
        form = PlanchaForm()  
    return render(request, 'crear_planchas.html', {'form': form})

@login_required
def mantencion_planchas_form(request):
    plancha_id = request.GET.get('id_tipo_plancha')
    plancha = None

    if plancha_id:
        try:
            plancha = Tipo_Plancha.objects.get(id_tipo_plancha=plancha_id)
        except Tipo_Plancha.DoesNotExist:
            messages.error(request, "Los datos solicitados no existen")
            return redirect('mantencion_planchas_form')

    if request.method == 'POST':
        form = PlanchaForm(request.POST, instance=plancha)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados con éxito!')
            return redirect('mantencion_planchas_form')
    else:
        form = PlanchaForm(instance=plancha)
    todas_las_planchas = Tipo_Plancha.objects.all()

    return render(request, 'mantencion_planchas_form.html', {'form': form, 'planchas': todas_las_planchas})

"""
-----------------------------------------------------------------------------
Mantención de parámetros
-----------------------------------------------------------------------------
"""
@login_required
def lista_parametros(request):
    parametros = Parametro.objects.all()
    return render(request, 'mantencion_parametros_form.html', {'parametros': parametros})

@login_required
def editar_parametro(request, id):
    parametro = get_object_or_404(Parametro, pk=id)
    if request.method == 'POST':
        form = ParametroForm(request.POST, instance=parametro)
        if form.is_valid():
            form.save()
            return redirect('lista_parametros')
    else:
        form = ParametroForm(instance=parametro)
    return render(request, 'editar_parametros.html', {'form': form, 'parametro': parametro})

@login_required
def eliminar_parametro(request, id):
    parametro = get_object_or_404(Parametro, pk=id)
    parametro.delete()
    return redirect('lista_parametros')

@login_required
def crear_parametro(request):
    if request.method == 'POST':
        form = ParametroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_parametros')  # O donde quieras redirigir después de crear
    else:
        form = ParametroForm()  # Un formulario vacío para un nuevo registro
    return render(request, 'crear_parametros.html', {'form': form})

@login_required
def mantencion_parametros_form(request):
    parametro_id = request.GET.get('id_parametro')
    parametro = None

    if parametro_id:
        try:
            parametro = Parametro.objects.get(id_parametro=parametro_id)
        except Parametro.DoesNotExist:
            messages.error(request, "Los datos solicitados no existen")
            return redirect('mantencion_parametros_form')

    if request.method == 'POST':
        form = ParametroForm(request.POST, instance=parametro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cambios guardados con éxito!')
            return redirect('mantencion_parametros_form')
    else:
        form = ParametroForm(instance=parametro)
    todos_los_parametros = Parametro.objects.all()

    return render(request, 'mantencion_parametros_form.html', {'form': form, 'parametros': todos_los_parametros})

"""
API Cálculo Manual
"""
def enviar_solicitud_api(largo, ancho, alto, largo_plancha, ancho_plancha, coste_materia, cantidad):
    # URL de tu API
    url = 'http://localhost:8000/calcular_manual/'
    token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5'  # Token de autenticación

    headers = {'Authorization': f'Token {token}'}

    # Datos para enviar en la petición POST
    datos_prueba = {
        'largo_caja': largo,
        'ancho_caja': ancho,
        'alto_caja': alto,
        'largo_plancha': largo_plancha,
        'ancho_plancha': ancho_plancha,
        'coste_materia': coste_materia,
        'coste_creacion': 50,  # Costo fijo
        'cantidad_caja': cantidad,
        # Agregar aquí otros campos necesarios si los tienes, como id_cliente, etc.
    }

    try:
        # Realizar la petición POST
        respuesta = requests.post(url, json=datos_prueba, headers=headers)
        
        if respuesta.status_code == 200:
            return respuesta.json()  # Devolver los datos de la respuesta
        else:
            print(f"Error en la solicitud: {respuesta.status_code}, Respuesta: {respuesta.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error al hacer la solicitud: {e}")
        return None

"""
API PDF Manual
"""
@login_required
def solicitud_pdf(request, id_solicitud):
    try:
        # Obtener datos desde la sesión
        datos_procesar = request.session.get('datos_procesar', {})
        datos_calculo = request.session.get('datos_calculo_precio', {})

        # Validar y calcular los valores necesarios
        try:
            precio_final = int(round(float(datos_calculo.get('precio_final'))))
            cantidad = int(datos_procesar.get('cantidad'))
            area_calculada = round(float(datos_procesar.get('largo_hm', 0)) * float(datos_procesar.get('ancho_hm', 0)), 2)
            precio_total = (precio_final * cantidad)
        except (ValueError, TypeError):
            print("Error en la conversión de los valores.")
            return None

        # Asegurarse de obtener el cliente y su correo
        rut_cliente = datos_procesar.get('rut_cliente', '')
        comentario = datos_procesar.get('comentarios', '')
        try:
            cliente = Cliente.objects.get(rut_cliente=rut_cliente)
            correo_cliente = cliente.correo
            nombre_completo = f'{cliente.nombre} {cliente.apellido}'
        except Cliente.DoesNotExist:
            correo_cliente = ''

        # Datos que se enviarán en la petición a la API
        datos_pdf = {
            'porcentaje_utilidad': datos_calculo.get('porcentaje'),
            'precio_caja': int(round(float(datos_calculo.get('precio_final')))),
            'cantidad_planchas':int(datos_procesar.get('api_cantidad_plancha')),
            'largo_maximo_caja':datos_procesar.get('largo_hm_str'),
            'alto_maximo_caja':datos_procesar.get('ancho_hm_str'),
            'largo_caja':int(datos_procesar.get('largo')),
            'ancho_caja':int(datos_procesar.get('ancho')),
            'alto_caja':int(datos_procesar.get('alto')),
            'area_caja':area_calculada,
            'comentario':comentario,
            'nombre_cliente': nombre_completo,
            'rut_cliente': rut_cliente,
            'correo_cliente': correo_cliente,
            'id_solicitud': id_solicitud,  # ID de la solicitud recién creada
            'alto_max_caja': datos_procesar.get('ancho_hm', ''),
            'area_caja': datos_procesar.get('api_area_caja', ''),
            'cantidad_cajas': datos_procesar.get('cantidad', ''),
            'id_tipo_plancha': datos_procesar.get('tipo_carton', ''),
            'area_total_plancha': datos_procesar.get('api_area_total_plancha', ''),
            'coste_creacion': 50,
            'coste_materia_prima': datos_procesar.get('api_precio_plancha', ''),
            'precio_total': precio_total,
            'fecha_solicitud': datos_procesar.get('api_fecha_solicitud', ''),
        }

        # URL y headers para la petición a la API
        url = 'http://localhost:8000/crear_pdf_manual/'
        token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5'
        headers = {'Authorization': f'Token {token}'}

        # Realizar la petición POST
        respuesta = requests.post(url, json=datos_pdf, headers=headers)
        
        if respuesta.status_code == 200:
            # Instanciar el PDF en una variable
            contenido_pdf = respuesta.content
            return contenido_pdf
        else:
            print(f"Error en la solicitud: {respuesta.status_code}, Respuesta: {respuesta.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error al hacer la solicitud: {e}")
        return None

"""
Generar cotización (Guarda en db)
"""
@login_required
def generar_cotizacion(request):
    if request.method == 'POST':
        
        porcentaje = request.POST.get('porcentaje')
        precio_final = request.POST.get('precio_final')

        datos_calculo_precio = {
            'porcentaje': porcentaje,
            'precio_final': precio_final,
        }

        datos_procesar = request.session.get('datos_procesar', {})
        

        
        cantidad = int(datos_procesar.get('cantidad'))
        precio_total = int(float(precio_final) * cantidad)

        

        request.session['datos_calculo_precio'] = datos_calculo_precio    

        try:
            cliente = Cliente.objects.get(rut_cliente=datos_procesar.get('rut_cliente'))
        except Cliente.DoesNotExist:
            # Manejar el caso en que el cliente no exista
            return HttpResponse("Error: Cliente no encontrado.", status=404)

        # Validar precio_final
        if precio_final is None or precio_final == '':
            return HttpResponse("Error: Precio final no proporcionado.", status=400)

        try:
            precio_final = float(precio_final)
        except ValueError:
            return HttpResponse("Error: Precio final inválido.", status=400)

        nueva_solicitud = Solicitud_Cotizacion(
            rut_cliente=cliente,
            largo=datos_procesar.get('largo'),
            ancho=datos_procesar.get('ancho'),
            alto=datos_procesar.get('alto'),
            fecha_cotizacion=datetime.now(),
            cantidad_caja=datos_procesar.get('cantidad'),
            cod_carton=datos_procesar.get('tipo_carton'),
            comentario=datos_procesar.get('comentario', ''),
            estado='Pendiente',
            monto_total=precio_total
        )
        nueva_solicitud.save()

        # Obtener el ID de la solicitud recién creada
        id_solicitud = nueva_solicitud.id_cotizacion
        request.session['id_solicitud'] = id_solicitud #Pasandola a un session para usar mas adelante.

        # No limpiar la sesión aquí, ya que los datos se utilizarán más adelante
        # request.session.pop('datos_procesar', None)
        # request.session.pop('datos_calculo_precio', None)

        # Redirigir a una página de confirmación o mostrar un mensaje de éxito
        contenido_pdf = solicitud_pdf(request, id_solicitud)

        # Codificar el PDF en base64 y crear una Data URL
        pdf_base64 = base64.b64encode(contenido_pdf).decode()
        data_url = f'data:application/pdf;base64,{pdf_base64}'
        return render(request, 'generar_cotizacion.html', {'solicitud': nueva_solicitud, 'data_url': data_url})
    else:
        # Si no es una solicitud POST, redirigir al formulario
        return redirect('cotizacion_manual')

"""
Enviar cotizacion (Envia correo PDF API a Cliente)
"""
@login_required
def enviar_cotizacion(request):
    # Asegurarse de que solo se procese como una solicitud POST
    if request.method != 'POST':
        return redirect('cotizacion_manual')

    try:
        datos_calculo = request.session.get('datos_calculo_precio', {})
        # Obtener datos desde la sesión
        datos_procesar = request.session.get('datos_procesar', {})
        datos_calculo_precio = request.session.get('datos_calculo_precio', {})
        rut_cliente = datos_procesar.get('rut_cliente', '')
        comentario = datos_procesar.get('comentarios', '')
        precio_final = int(round(float(datos_calculo.get('precio_final'))))
        cantidad = int(datos_procesar.get('cantidad'))
        precio_total = (precio_final * cantidad)

        cliente = Cliente.objects.get(rut_cliente=rut_cliente)
        id_solicitud = request.session.get('id_solicitud')
        Sol_Cot = Solicitud_Cotizacion.objects.get(id_cotizacion=id_solicitud)
        # Preparar los datos para enviar a la API
        fecha_cotizacion = Sol_Cot.fecha_cotizacion.strftime('%Y-%m-%d %H:%M:%S')
        nombre_completo = f'{cliente.nombre} {cliente.apellido}'
        datos_api = {
            'cantidad_planchas':int(datos_procesar.get('api_cantidad_plancha')),
            'largo_caja':int(datos_procesar.get('largo')),
            'ancho_caja':int(datos_procesar.get('ancho')),
            'alto_caja':int(datos_procesar.get('alto')),
            'nombre_cliente': nombre_completo,
            'rut_cliente': rut_cliente,
            'correo_cliente': cliente.correo,
            'id_solicitud': id_solicitud,
            'comentario':comentario,
            'largo_maximo_caja': datos_procesar.get('largo_hm_str', ''),
            'alto_maximo_caja': datos_procesar.get('ancho_hm_str', ''),
            'area_caja': datos_procesar.get('api_area_caja', ''),
            'cantidad_cajas': datos_procesar.get('cantidad', ''),
            'id_tipo_plancha': datos_procesar.get('tipo_carton', ''),
            'area_total_plancha': datos_procesar.get('api_area_total_plancha', ''),
            'coste_creacion': 50,
            'coste_materia_prima': datos_procesar.get('api_precio_plancha', ''),
            'precio_caja': int(round(float(datos_calculo.get('precio_final')))),
            'precio_total': precio_total,
            'porcentaje_utilidad': datos_calculo_precio.get('porcentaje', ''),
            'fecha_solicitud': fecha_cotizacion,
            'fecha_vencimiento': datos_procesar.get('api_fecha_vencimiento','')
        }
        
        # URL y headers para la petición a la API
        url = 'http://localhost:8000/crear_correo/'
        token = '95f397a7bce2f2ffbe6c404caa1994ae991c4ee5'  # Asegúrate de usar tu token real aquí
        headers = {'Authorization': f'Token {token}'}

        # Realizar la petición POST
        respuesta = requests.post(url, json=datos_api, headers=headers)

        if respuesta.status_code == 200:
            # Mostrar una página de confirmación
            return render(request, 'enviar_cotizacion.html', {'mensaje': 'Correo enviado con éxito, redirigiendo...'})
        else:
            # Mostrar un mensaje de error y quedarse en la misma página
            return render(request, 'generar_cotizacion.html', {'mensaje': 'Error al enviar el correo, por favor comuníquese con soporte al cliente'})
    
    except Exception as e:
        # Mostrar un mensaje de error y quedarse en la misma página
        return render(request, 'generar_cotizacion.html', {'mensaje': f"Error al enviar la cotización: {e}, por favor comuníquese con soporte al cliente"})

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
-----------------------------------------------------------------------------
Selección de plancha a utilizar
-----------------------------------------------------------------------------
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
@login_required
def cotizacion_manual (request):
        return render(request, 'cotizacion_manual.html')

@login_required
def calculo_de_precio(request):

    return render(request, 'calculo_de_precio.html')

@login_required
def creacion_cliente(request):
    return render(request, 'creacion_cliente.html')

from django.shortcuts import render, redirect
from .models import Cliente  # Importa el modelo Cliente
from django.core.exceptions import ValidationError

@login_required
def agregar_cliente(request):
    mensaje_error = None
    mensaje_exito = None
    if request.method == 'POST':
        rut_cliente = request.POST.get('rut_cliente')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')

        if Cliente.objects.filter(rut_cliente=rut_cliente).exists():
            mensaje_error = "El RUT ingresado ya existe en la base de datos."
        else:
            try:
                nuevo_cliente = Cliente(rut_cliente=rut_cliente, nombre=nombre, apellido=apellido, correo=correo)
                nuevo_cliente.save()
                mensaje_exito = "Cliente añadido satisfactoriamente, redirigiendo..."
                # Aquí, puedes redirigir o manejar el mensaje de éxito como prefieras
            except Exception as e:
                mensaje_error = f"Error al agregar el cliente: {str(e)}"

    context = {
        'mensaje_error': mensaje_error,
        'mensaje_exito': mensaje_exito
    }
    return render(request, 'creacion_cliente.html', context)



"""
-----------------------------------------------------------------------------
PROCESAR DATOS FORMULARIO MANUAL
-----------------------------------------------------------------------------
"""
@login_required
def procesar_datos(request):
    mensaje_error = None #inicializador
    if request.method == 'POST':
        rut_cliente = request.POST.get('rut_cliente')
        request.session['rut_para_crear'] = rut_cliente
        largo = float(request.POST.get('largo'))
        largostr = request.POST.get('largo')
        ancho = float(request.POST.get('ancho'))
        anchostr = request.POST.get('ancho')
        alto = float(request.POST.get('alto'))
        altostr = request.POST.get('alto')
        cantidad = int(request.POST.get('cantidad_cajas'))
        tipo_carton = request.POST.get('tipo_carton').upper()
        comentarios = request.POST.get('comentarios')

         # Verificar si el cliente ya existe
        try:
            cliente = Cliente.objects.get(rut_cliente=rut_cliente)
            # El cliente existe, logica continúa

            #rut de arriba
            nombre_cliente = cliente.nombre
            apellido_cliente = cliente.apellido
            correo_cliente = cliente.correo
        except Cliente.DoesNotExist:
            # El cliente no existe, redirige a una nueva plantilla para agregar al cliente
            return redirect('creacion_cliente')

        

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
        coste_materia = plancha_seleccionada.get('precio_proveedor')

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
        # Ejemplo de cómo llamar a la función
        resultado_api = enviar_solicitud_api(largo, ancho, alto, plancha_seleccionada.get('largo'),plancha_seleccionada.get('ancho'),plancha_seleccionada.get('precio_proveedor'), cantidad)
        if resultado_api:
            # Suponiendo que resultado_api contiene la respuesta de la API
            api_fecha_solicitud = resultado_api['fecha_solicitud']
            api_fecha_vencimiento = resultado_api['fecha_vencimiento']
            api_id_cliente = resultado_api['id_cliente']
            api_rut_cliente = resultado_api['rut_cliente']
            api_nombre_cliente = resultado_api['nombre_cliente']
            api_correo_cliente = resultado_api['correo_cliente']
            api_id_solicitud = resultado_api['id_solicitud']
            api_comentario = resultado_api['comentario']
            api_largo_maximo_caja = resultado_api['largo_maximo_caja']
            api_ancho_maximo_caja = resultado_api['alto_maximo_caja']
            api_area_caja = resultado_api['area_caja']
            api_id_tipo_plancha = resultado_api['id_tipo_plancha']
            api_cod_carton = resultado_api['cod_carton']
            api_largo_plancha = resultado_api['largo_plancha']
            api_ancho_plancha = resultado_api['ancho_plancha']
            api_area_total_plancha = resultado_api['area_total_plancha']
            api_dif_largo = resultado_api['dif_largo']
            api_dif_alto = resultado_api['dif_alto']
            api_precio_plancha = resultado_api['precio_plancha']
            api_coste_creacion = resultado_api['coste_creacion']
            api_coste_materia_prima = resultado_api['coste_materia_prima']
            api_cantidad_cajas = resultado_api['cantidad_cajas']
            api_cantidad_x_plancha = resultado_api['cantidad_x_plancha']
            api_precio_caja = resultado_api['precio_caja']
            api_precio_total = resultado_api['precio_total']
            api_cantidad_plancha = resultado_api['cantidad_planchas']

            print(resultado_api)
        else:
            print("No se obtuvieron datos de la API.")
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

        """
        Sessions para argumentos de API
        """
        datos_procesar = {
            'comentarios':comentarios,
            'rut_cliente': rut_cliente,
            'api_fecha_solicitud': api_fecha_solicitud,
            'largo': largo,
            'ancho': ancho,
            'alto': alto,
            'largostr': largostr,
            'anchostr': anchostr,
            'altostr': altostr,
            'cantidad': api_cantidad_cajas,
            'tipo_carton': tipo_carton,
            'api_precio_plancha': api_precio_plancha,
            'largo_hm': largo_hm,
            'ancho_hm': ancho_hm,
            'media_hm': media_hm,
            'largo_hm_str': api_largo_maximo_caja,
            'ancho_hm_str': api_ancho_maximo_caja,
            'media_hm_str': media_hm_str,
            'plancha_necesaria': plancha_seleccionada,
            'excedente_vertical': excedente_vertical,
            'excedente_horizontal': excedente_horizontal,
            'total_cajas_por_plancha': total_cajas_por_plancha,
            'costo_ex_vertical': round(costo_ex_vertical),
            'costo_ex_horizontal': round(costo_ex_horizontal),
            'costo_por_unidad': round(api_precio_caja),
            'nombre_cliente': nombre_cliente,
            'apellido_cliente': apellido_cliente,
            'api_area_caja': api_area_caja,
            'api_area_total_plancha': api_area_total_plancha,
            'api_cantidad_plancha': api_cantidad_plancha,
            'api_cantidad_x_plancha': api_cantidad_x_plancha,
            'api_fecha_vencimiento': api_fecha_vencimiento,
        }

        request.session['datos_procesar'] = datos_procesar
    if mensaje_error:
        return render(request, 'cotizacion_manual.html', {'mensaje_error': mensaje_error})
    else:
        return render(request, 'calculo_de_precio.html',{'api_fecha_solicitud':api_fecha_solicitud, #API
                                                         'largo':largo,
                                                          'ancho':ancho,
                                                          'alto':alto,
                                                          'largostr':largostr,
                                                          'anchostr':anchostr,
                                                          'altostr':altostr,
                                                          'cantidad':api_cantidad_cajas, #API
                                                          'tipo_carton':tipo_carton,
                                                          'api_precio_plancha':api_precio_plancha, #API
                                                          'largo_hm':largo_hm,
                                                          'ancho_hm':ancho_hm,
                                                          'media_hm':media_hm,
                                                          'largo_hm_str':api_largo_maximo_caja, #API
                                                          'ancho_hm_str':api_ancho_maximo_caja, #API
                                                          'media_hm_str':media_hm_str,
                                                          'plancha_necesaria':plancha_seleccionada,
                                                          'excedente_vertical':excedente_vertical, #API VER
                                                          'excedente_horizontal':excedente_horizontal, #API VER
                                                          'total_cajas_por_plancha': total_cajas_por_plancha, #APISALE MAL
                                                          'costo_ex_vertical':round(costo_ex_vertical),
                                                          'costo_ex_horizontal':round(costo_ex_horizontal),
                                                          'costo_por_unidad':round(api_precio_caja),
                                                          'nombre_cliente':nombre_cliente,
                                                          'apellido_cliente':apellido_cliente,
                                                          'api_area_caja':api_area_caja, #API
                                                          'api_area_total_plancha':api_area_total_plancha,
                                                          'api_cantidad_plancha': api_cantidad_plancha,
                                                          'api_cantidad_x_plancha': api_cantidad_x_plancha
                                                          })  
