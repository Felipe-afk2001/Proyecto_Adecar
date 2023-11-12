from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import math
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from django.utils import timezone


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def calcular_manual(request):
    try:
        if request.method == 'POST':
            data = request.data

            # Generar variables
                #variables cliente
            id_cliente = data.get('id_cliente', 0)
            nombre_cliente = data.get('nombre_cliente', 0)
            rut_cliente = data.get('rut_cliente', 0)
            correo_cliente = data.get('correo_cliente', 0)

                #varibles solicitud
            id_solicitud = data.get('id_solicitud', 0)
            comentario = data.get('comentario', 0)

                #variables caja
            largo1 = (data.get('largo_caja', 0)+3)
            largo2 = (data.get('ancho_caja', 0)+5)
            largo3 = (data.get('largo_caja', 0)+5)
            largo4 = (data.get('ancho_caja', 0)+3)
            alto1 = (data.get('alto_caja', 0)+5)
            alto2 = ((data.get('ancho_caja', 0)/2)+3)

                #variables plancha
            id_tipo_plancha = data.get('id_tipo_plancha', 0)
            largo_plancha = data.get('largo_plancha', 0)
            ancho_plancha = data.get('ancho_plancha', 0)
            cod_carton = data.get('cod_carton', 0)
            precio_plancha = data.get('coste_materia', 0)
            precio_plancha = math.ceil(precio_plancha)  

                #varibles costos
            coste_creacion = data.get('coste_creacion', 0)
            coste_creacion = math.ceil(coste_creacion)  

                #variables cantidad
            cantidad_caja = data.get('cantidad_caja', 0)

            # Calculos (todos los calculos redondeados)
                #calculo area caja
            largo_maximo_caja = largo1 + largo2 + largo3 + largo4 + 40
            alto_max_caja  = alto1 + (alto2 * 2)
            area_caja = largo_maximo_caja * alto_max_caja
            area_caja = math.ceil(area_caja)  

                #calculo area de plancha total (sin contar el exedente)
            area_total_plancha = largo_plancha * ancho_plancha
            area_total_plancha = math.ceil(area_total_plancha)  

                #calculo exedentes
            exedente_vertical = ancho_plancha - largo_maximo_caja
            exedente_horizontal = largo_plancha - alto_max_caja

                #calculo de cantidad de planchas
            dif_largo = largo_plancha / largo_maximo_caja
            dif_largo = math.ceil(dif_largo)
            dif_alto = ancho_plancha / alto_max_caja
            dif_alto = math.ceil(dif_alto)

            cantidad_plancha = cantidad_caja
            cantidad_plancha = math.ceil(cantidad_plancha)

            if dif_largo >= 2 or dif_alto >= 2:
                cantidad_plancha = dif_alto + dif_largo
                cantidad_plancha = math.ceil(cantidad_plancha)

                #calculo costo de la materia prima
            coste_materia_prima = (cantidad_plancha * precio_plancha)
            coste_materia_prima = math.ceil(coste_materia_prima)  

                #calculo de precio de caja unitaria
            precio_caja = (coste_creacion + coste_materia_prima) 
            precio_caja = math.ceil(precio_caja)  

                #calculo de precio de total de cajas
            precio_total = precio_caja * cantidad_caja
            precio_total = math.ceil(precio_total)

                #calculo fecha de vencimiento
            fecha_actual = timezone.now()
            fecha_vencimiento = fecha_actual + timedelta(days=10)  
            fecha_vencimiento = fecha_vencimiento.strftime('%d-%m-%Y')
            fecha_actual = fecha_actual.strftime('%d-%m-%Y')


            #Respuesta de los datos al sitio original
            return Response({
                'fecha_solicitud' : fecha_actual,
                'id_solicitud' : id_solicitud,
                'id_cliente' : id_cliente,
                'rut_cliente' : rut_cliente,
                'nombre_cliente' : nombre_cliente,
                'correo_cliente' : correo_cliente,
                'largo_maximo_caja' : largo_maximo_caja,
                'alto_maximo_caja' : alto_max_caja,
                'area_caja' : area_caja,
                'id_tipo_plancha' : id_tipo_plancha,
                'cod_carton' : cod_carton,
                'largo_plancha' : largo_plancha,
                'ancho_plancha' : ancho_plancha,
                'area_total_plancha' : area_total_plancha,
                'exedente_horizontal' : exedente_horizontal,
                'exedente_vertical' : exedente_vertical,
                'dif_largo': dif_largo,
                'dif_alto' : dif_alto,
                'precio_plancha' : precio_plancha,
                'coste_creacion' : coste_creacion,
                'coste_materia_prima': coste_materia_prima,
                'cantidad_cajas' : cantidad_caja,
                'cantidad_planchas' : cantidad_plancha,
                'precio_caja' : precio_caja,
                'precio_total' : precio_total,
                'comentario' : comentario,
                'fecha_vencimiento' : fecha_vencimiento
            }, status=status.HTTP_200_OK)
            
        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def crear_pdf_manual(request):
    try:
        if request.method == 'POST':
            data = request.data

            # Generar variables
                #variables cliente
            nombre_cliente = data.get('nombre_cliente', 0)
            rut_cliente = data.get('rut_cliente', 0)
            correo_cliente = data.get('correo_cliente', 0)

                #varibles solicitud
            id_solicitud = data.get('id_solicitud', 0)
            comentario = data.get('comentario', 0)

                #variables caja
            largo_maximo_caja = data.get('largo_maximo_caja')
            alto_max_caja = data.get('alto_max_caja')
            area_caja = data.get('area_caja')
            cantidad_caja = data.get('cantidad_caja', 0)

                #variables plancha
            id_tipo_plancha = data.get('id_tipo_plancha', 0)
            area_total_plancha = data.get('area_total_plancha')
            cantidad_plancha = data.get('cantidad_plancha')

                #varibles costos
            coste_creacion = data.get('coste_creacion', 0)
            coste_materia_prima = data.get('coste_materia_prima')  
            precio_caja = data.get('precio_caja')
            precio_total = data.get('precio_total')
            porcentaje_utilidad = data.get('porcentaje_utilidad')

                #variables fecha 
            fecha_actual = data.get('fecha_actual')
            fecha_vencimiento = data.get('fecha_vencimiento')

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
            # Crear el objeto PDF, usando el objeto HttpResponse como "buffer".
            p = canvas.Canvas(response)

             # Generar PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
            p = canvas.Canvas(response)

            # Agregar contenido al PDF

            margen_top = 950
            margen_titulo = 800
            margen_cliente = 850

            contenido_pdf = [
                'Medidas Solicitadas',
                f"Largo Caja: {data.get('largo_caja', 0)}",
                f"Ancho Caja: {data.get('ancho_caja', 0)} ",
                f"Alto Caja: {data.get('alto_caja', 0)}",
                f'',
                f'Medidas Calculadas',
                f'Largo total de la caja: {largo_maximo_caja}',
                f'Alto total de la caja: {alto_max_caja}',
                f'Area total de la caja: {area_caja}',
                f'',
                f'Detalle Cotizacion'
                f'Tipo de plancha: {id_tipo_plancha}'
                f'Area total de la plancha: {area_total_plancha}',
                f'Cantidad de cajas solicitadas: {cantidad_caja}',
                f'Cantidad de planchas solicitadas: {cantidad_plancha}',
                f'Costos por la cantidad de planchas: {coste_materia_prima}',
                f'Porcentaje de benedicio empresa: {porcentaje_utilidad}',
                f'Costo de creacion de una caja: {coste_creacion}',
                f'Precio Unitario por Caja:{precio_caja}',
                f'Precio Total por Cajas: {precio_total}',
                f'Comentario para la cotizacion : {comentario}'
            ]
            contenido_cliente = [
                'Procesado para',
                f'Cliente: {nombre_cliente}',
                f'Correo: {correo_cliente}',
                f'Rut: {rut_cliente}'
            ]

            p.drawString(80, margen_titulo, f'Cotizacion N° {id_solicitud}')

            p.drawString(20, (margen_titulo), 'Adecar')
            
            for linea in contenido_cliente:
                p.drawString(80, margen_cliente, linea)
                margen_cliente -= 20

            for linea in contenido_pdf:
                p.drawString(100, margen_top, linea)
                margen_top -= 20

            # Cierra el objeto PDF y devuelve la respuesta
            p.showPage()
            p.save()

            # Enviar correo electrónico con el PDF adjunto
            email = EmailMessage(
                f'Cotizacion N° {id_solicitud}', #Asunto
                f'''
                    Estimado {nombre_cliente},

                    Adjunto encontrarás la cotización solicitada. Hemos revisado los detalles y hemos preparado una oferta personalizada 
                    para tu consideración.

                    **Pasos Siguientes:**
                    1. Si estás de acuerdo con la cotización, por favor, confírmanos tu aceptación.
                    2. Para proceder con el pedido, te proporcionaremos detalles sobre el proceso de pago y cualquier información adicional necesaria.
                    3. Si tienes alguna pregunta o necesitas más aclaraciones, no dudes en ponerte en contacto con nosotros.

                    **Fecha de vencimiento de la cotizacion:** {fecha_vencimiento}

                    Agradecemos la oportunidad de servirte y esperamos con interés la posibilidad de colaborar contigo.

                    Quedamos a tu disposición para cualquier consulta.

                    Atentamente,
                    Area Ventas
                    Adecar
                    ''', #Cuerpo
                'cotizacion.adecar@gmail.com',  #Remitente
                [f'{correo_cliente}'],  #Destinatario
            )
            email.attach('cotizacion.pdf', response.content, 'application/pdf')
            email.send()
            return Response({'Exito': 'Correo enviado con PDF'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def calcular_auto(request):
    try:
        if request.method == 'POST':
            # Obtener datos
            data = request.data

            # Generar variables
                #variables cliente
            id_cliente = data.get('id_cliente', 0)
            nombre_cliente = data.get('nombre_cliente', 0)
            rut_cliente = data.get('rut_cliente', 0)
            correo_cliente = data.get('correo_cliente', 0)

                #varibles solicitud
            id_solicitud = data.get('id_solicitud', 0)
            comentario = data.get('comentario', 0)

                #variables caja
            largo1 = (data.get('largo_caja', 0)+3)
            largo2 = (data.get('ancho_caja', 0)+5)
            largo3 = (data.get('largo_caja', 0)+5)
            largo4 = (data.get('ancho_caja', 0)+3)
            alto1 = (data.get('alto_caja', 0)+5)
            alto2 = ((data.get('ancho_caja', 0)/2)+3)

                #variables plancha
            id_tipo_plancha = data.get('id_tipo_plancha', 0)
            largo_plancha = data.get('largo_plancha', 0)
            ancho_plancha = data.get('ancho_plancha', 0)
            cod_carton = data.get('cod_carton', 0)
            precio_plancha = data.get('coste_materia', 0)
            precio_plancha = math.ceil(precio_plancha)  

                #varibles costos
            porcentaje_utilidad = data.get('porcentaje_utilidad', 0)
            coste_creacion = data.get('coste_creacion', 0)
            coste_creacion = math.ceil(coste_creacion)  

                #variables cantidad
            cantidad_caja = data.get('cantidad_caja', 0)


            # Calculos (todos los calculos redondeados)
                #calculo area caja
            largo_maximo_caja = largo1 + largo2 + largo3 + largo4 + 40
            alto_max_caja  = alto1 + (alto2 * 2)
            area_caja = largo_maximo_caja * alto_max_caja
            area_caja = math.ceil(area_caja)  

                #calculo area de plancha total (sin contar el exedente)
            area_total_plancha = largo_plancha * ancho_plancha
            area_total_plancha = math.ceil(area_total_plancha)  

                #calculo exedentes
            exedente_vertical = ancho_plancha - largo_maximo_caja
            exedente_horizontal = largo_plancha - alto_max_caja

                #calculo de cantidad de planchas
            dif_largo = largo_plancha / largo_maximo_caja
            dif_largo = math.ceil(dif_largo)
            dif_alto = ancho_plancha / alto_max_caja
            dif_alto = math.ceil(dif_alto)

            cantidad_plancha = cantidad_caja
            cantidad_plancha = math.ceil(cantidad_plancha)

            if dif_largo >= 2 or dif_alto >= 2:
                cantidad_plancha = dif_alto + dif_largo
                cantidad_plancha = math.ceil(cantidad_plancha)

                #calculo costo de la materia prima
            coste_materia_prima = (cantidad_plancha * precio_plancha)
            coste_materia_prima = math.ceil(coste_materia_prima)  

                #calculo de precio de caja unitaria
            precio_caja = (coste_creacion + coste_materia_prima) * porcentaje_utilidad
            precio_caja = math.ceil(precio_caja)  

                #calculo de precio de total de cajas
            precio_total = precio_caja * cantidad_caja
            precio_total = math.ceil(precio_total)

                #calculo fecha de vencimiento
            fecha_actual = timezone.now()
            fecha_vencimiento = fecha_actual + timedelta(days=10)  
            fecha_vencimiento = fecha_vencimiento.strftime('%d-%m-%Y')
            fecha_actual = fecha_actual.strftime('%d-%m-%Y')

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
            # Crear el objeto PDF, usando el objeto HttpResponse como "buffer".
            p = canvas.Canvas(response)

             # Generar PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
            p = canvas.Canvas(response)

            # Agregar contenido al PDF

            margen_top = 950
            margen_titulo = 800
            margen_cliente = 850

            contenido_pdf = [
                'Medidas Solicitadas',
                f"Largo Caja: {data.get('largo_caja', 0)}",
                f"Ancho Caja: {data.get('ancho_caja', 0)} ",
                f"Alto Caja: {data.get('alto_caja', 0)}",
                f'',
                f'Medidas Calculadas',
                f'Largo total de la caja: {largo_maximo_caja}',
                f'Alto total de la caja: {alto_max_caja}',
                f'Area total de la caja: {area_caja}',
                f'',
                f'Detalle Cotizacion'
                f'Tipo de plancha: {id_tipo_plancha}'
                f'Area total de la plancha: {area_total_plancha}',
                f'Cantidad de cajas solicitadas: {cantidad_caja}',
                f'Cantidad de planchas solicitadas: {cantidad_plancha}',
                f'Costos por la cantidad de planchas: {coste_materia_prima}',
                f'Porcentaje de benedicio empresa: {porcentaje_utilidad}',
                f'Costo de creacion de una caja: {coste_creacion}',
                f'Precio Unitario por Caja:{precio_caja}',
                f'Precio Total por Cajas: {precio_total}'
            ]
            contenido_cliente = [
                'Procesado para',
                f'Cliente: {nombre_cliente}',
                f'Correo: {correo_cliente}',
                f'Rut: {rut_cliente}'
            ]

            p.drawString(80, margen_titulo, f'Cotizacion N° {id_solicitud}')

            p.drawString(20, (margen_titulo), 'Adecar')
            
            for linea in contenido_cliente:
                p.drawString(80, margen_cliente, linea)
                margen_cliente -= 20

            for linea in contenido_pdf:
                p.drawString(100, margen_top, linea)
                margen_top -= 20

            # Cierra el objeto PDF y devuelve la respuesta
            p.showPage()
            p.save()

            # Enviar correo electrónico con el PDF adjunto
            email = EmailMessage(
                f'Cotizacion N° {id_solicitud}', #Asunto
                f'''
                    Estimado {nombre_cliente},

                    Adjunto encontrarás la cotización solicitada. Hemos revisado los detalles y hemos preparado una oferta personalizada 
                    para tu consideración.

                    **Pasos Siguientes:**
                    1. Si estás de acuerdo con la cotización, por favor, confírmanos tu aceptación.
                    2. Para proceder con el pedido, te proporcionaremos detalles sobre el proceso de pago y cualquier información adicional necesaria.
                    3. Si tienes alguna pregunta o necesitas más aclaraciones, no dudes en ponerte en contacto con nosotros.

                    **Fecha de vencimiento de la cotizacion:** {fecha_vencimiento}

                    Agradecemos la oportunidad de servirte y esperamos con interés la posibilidad de colaborar contigo.

                    Quedamos a tu disposición para cualquier consulta.

                    Atentamente,
                    Area Ventas
                    Adecar
                    ''', #Cuerpo
                'cotizacion.adecar@gmail.com',  #Remitente
                [f'{correo_cliente}'],  #Destinatario
            )
            email.attach('cotizacion.pdf', response.content, 'application/pdf')
            email.send()

            #Respuesta de los datos al sitio original
            return Response({
                'fecha_solicitud' : fecha_actual,
                'id_solicitud' : id_solicitud,
                'id_cliente' : id_cliente,
                'rut_cliente' : rut_cliente,
                'nombre_cliente' : nombre_cliente,
                'correo_cliente' : correo_cliente,
                'largo_maximo_caja' : largo_maximo_caja,
                'alto_maximo_caja' : alto_max_caja,
                'area_caja' : area_caja,
                'id_tipo_plancha' : id_tipo_plancha,
                'cod_carton' : cod_carton,
                'largo_plancha' : largo_plancha,
                'ancho_plancha' : ancho_plancha,
                'area_total_plancha' : area_total_plancha,
                'exedente_horizontal' : exedente_horizontal,
                'exedente_vertical' : exedente_vertical,
                'dif_largo': dif_largo,
                'dif_alto' : dif_alto,
                'precio_plancha' : precio_plancha,
                'coste_creacion' : coste_creacion,
                'porcentaje_utilidad' : porcentaje_utilidad,
                'coste_materia_prima': coste_materia_prima,
                'cantidad_cajas' : cantidad_caja,
                'cantidad_planchas' : cantidad_plancha,
                'precio_caja' : precio_caja,
                'precio_total' : precio_total,
                'comentario' : comentario,
                'fecha_vencimiento' : fecha_vencimiento
            }, status=status.HTTP_200_OK)
            
        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)