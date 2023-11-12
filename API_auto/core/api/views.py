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

def calcular_vista(request):
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

            y_coordinate = 800
            contenido_pdf = [
                f'Largo total de la caja: {largo_maximo_caja}',
                f'largo_total:  {largo_maximo_caja}',
                f'alto_total: {alto_max_caja}',
                f'precio_plancha: {precio_plancha}',
                f'area_total_plancha: {area_total_plancha}',
                f'area_caja: {area_caja}',
                f'cantidad_cajas: {cantidad_caja}',
                f'cantidad_planchas: {cantidad_plancha}',
                f'coste_materia_prima: {coste_materia_prima}',
                f'porcentaje_utilidad: {porcentaje_utilidad}',
                f'coste_creacion: {coste_creacion}',
                f'precio_caja:{precio_caja}',
                f'precio_total: {precio_total}'
            ]

            for linea in contenido_pdf:
                p.drawString(100, y_coordinate, linea)
                y_coordinate -= 20

<<<<<<< HEAD
            p.drawString(100, y_coordinate, f'precio_plancha: {precio_plancha}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'area_total_plancha: {area_total_plancha}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'area_caja: {area_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'cantidad_cajas: {cantidad_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'Cajas por plancha: {cantidad_plancha}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'coste_materia_prima: {coste_materia_prima}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'porcentaje_utilidad: {porcentaje_utilidad}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'coste_creacion: {coste_creacion}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'precio_caja: {precio_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'precio_total: {precio_total}')
            y_coordinate -= 20

            # Cierra el objeto PDF y devuelve la respuesta.
=======
            # Cierra el objeto PDF y devuelve la respuesta
>>>>>>> 68ea86b020ecd93321a0fbc6356e926cf2b85aef
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