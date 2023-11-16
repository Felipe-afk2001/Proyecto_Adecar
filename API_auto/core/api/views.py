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
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors 
from PIL import Image, ImageDraw
import io

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
            largo_maximo_caja = math.ceil(largo_maximo_caja)
            alto_max_caja  = alto1 + (alto2 * 2)
            alto_max_caja = math.ceil(alto_max_caja)
            area_caja = largo_maximo_caja * alto_max_caja
            area_caja = math.ceil(area_caja)  

                #calculo area de plancha total (sin contar el exedente)
            area_total_plancha = largo_plancha * ancho_plancha
            area_total_plancha = math.ceil(area_total_plancha)  

                #calculo de cantidad de planchas
            dif_largo = largo_plancha / largo_maximo_caja
            dif_largo = int(dif_largo)
            dif_alto = ancho_plancha / alto_max_caja
            dif_alto = int(dif_alto)

            cantidad_plancha = cantidad_caja
            cantidad_plancha = math.ceil(cantidad_plancha)

            if dif_largo >= 2 or dif_alto >= 2:
                caja_x_planchas = dif_alto + dif_largo
                cantidad_plancha = cantidad_caja/caja_x_planchas
                cantidad_plancha = math.ceil(cantidad_plancha)

                #calculo costo de la materia prima
            coste_materia_prima = (cantidad_plancha * precio_plancha)
            coste_materia_prima = math.ceil(coste_materia_prima)  

                #calculo de precio de caja unitaria
            precio_caja = (coste_creacion) 
            precio_caja = math.ceil(precio_caja)  

                #calculo de precio de total de cajas
            precio_total = (precio_caja * cantidad_caja) + coste_materia_prima
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
            alto_max_caja = data.get('alto_maximo_caja')
            area_caja = data.get('area_caja')
            cantidad_caja = data.get('cantidad_cajas', 0)

                #variables plancha
            id_tipo_plancha = data.get('id_tipo_plancha', 0)
            area_total_plancha = data.get('area_total_plancha')
            cantidad_plancha = data.get('cantidad_planchas')

                #varibles costos
            coste_creacion = data.get('coste_creacion', 0)
            coste_materia_prima = data.get('coste_materia_prima')  
            precio_caja = data.get('precio_caja')
            precio_total = data.get('precio_total')
            porcentaje_utilidad = data.get('porcentaje_utilidad')

                #variables fecha 
            fecha_actual = data.get('fecha_solicitud')
            

            # Generar PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=letter)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 25)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(200, 730, f'Santiago de Chile, {fecha_actual}')
            
            # Datos del cliente
            altura_cliente = 700  # Iniciar la altura para los detalles del cliente
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_cliente, f'Cliente: {nombre_cliente}')
            p.drawString(50, altura_cliente - 15, f'Correo: {correo_cliente}')
            p.drawString(50, altura_cliente - 30, f'Rut: {rut_cliente}')
            p.drawString(50, altura_cliente - 45, f'Comentario: {comentario}')

            # Línea de separación
            p.setStrokeColor(colors.black)
            p.line(50, altura_cliente - 60, 550, altura_cliente - 60)

            # Detalles de la cotización
            altura_detalle = altura_cliente - 80  # Iniciar la altura para los detalles de la cotización
            
            # Medidas Solicitadas
            altura_detalle -= 20
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas Solicitadas')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} ")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)}")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_max_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja}')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha}',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: {coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricacion: {coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: {precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: {precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)


            # Cierra el objeto PDF y devuelve la respuesta
            p.showPage()
            p.save()
            return response

        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def crear_correo(request):
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
            alto_max_caja = data.get('alto_maximo_caja')
            area_caja = data.get('area_caja')
            cantidad_caja = data.get('cantidad_cajas', 0)

                #variables plancha
            id_tipo_plancha = data.get('id_tipo_plancha', 0)
            area_total_plancha = data.get('area_total_plancha')
            cantidad_plancha = data.get('cantidad_planchas')

                #varibles costos
            coste_creacion = data.get('coste_creacion', 0)
            coste_materia_prima = data.get('coste_materia_prima')  
            precio_caja = data.get('precio_caja')
            precio_total = data.get('precio_total')
            porcentaje_utilidad = data.get('porcentaje_utilidad')

                #variables fecha 
            fecha_actual = data.get('fecha_solicitud')
            fecha_vencimiento = data.get('fecha_vencimiento')

            # Generar PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=letter)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 25)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(200, 730, f'Santiago de Chile, {fecha_actual}')
            
            # Datos del cliente
            altura_cliente = 700  # Iniciar la altura para los detalles del cliente
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_cliente, f'Cliente: {nombre_cliente}')
            p.drawString(50, altura_cliente - 15, f'Correo: {correo_cliente}')
            p.drawString(50, altura_cliente - 30, f'Rut: {rut_cliente}')
            p.drawString(50, altura_cliente - 45, f'Comentario: {comentario}')

            # Línea de separación
            p.setStrokeColor(colors.black)
            p.line(50, altura_cliente - 60, 550, altura_cliente - 60)

            # Detalles de la cotización
            altura_detalle = altura_cliente - 80  # Iniciar la altura para los detalles de la cotización
            
            # Medidas Solicitadas
            altura_detalle -= 20
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas Solicitadas')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} ")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)}")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_max_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja}')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha}',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: {coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricacion: {coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: {precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: {precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)


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


                #calculo de cantidad de planchas
            dif_largo = largo_plancha / largo_maximo_caja
            dif_largo = int(dif_largo)
            dif_alto = ancho_plancha / alto_max_caja
            dif_alto = int(dif_alto)

            cantidad_plancha = cantidad_caja
            cantidad_plancha = math.ceil(cantidad_plancha)

            if dif_largo >= 2 or dif_alto >= 2:
                caja_x_planchas = dif_alto + dif_largo
                cantidad_plancha = cantidad_caja/caja_x_planchas
                cantidad_plancha = math.ceil(cantidad_plancha)

                #calculo costo de la materia prima
            coste_materia_prima = (cantidad_plancha * precio_plancha)
            coste_materia_prima = math.ceil(coste_materia_prima)  

                #calculo de precio de caja unitaria
            precio_caja = (coste_creacion) * porcentaje_utilidad
            precio_caja = math.ceil(precio_caja)  

                #calculo de precio de total de cajas
            precio_total = (precio_caja * cantidad_caja) + coste_materia_prima
            precio_total = math.ceil(precio_total)

                #calculo fecha de vencimiento
            fecha_actual = timezone.now()
            fecha_vencimiento = fecha_actual + timedelta(days=10)  
            fecha_vencimiento = fecha_vencimiento.strftime('%d-%m-%Y')
            fecha_actual = fecha_actual.strftime('%d-%m-%Y')

            # # Generar imagen de la caja
            # imagen = Image.new('RGB', (1800, 2500), 'white')  # Cambiado para una orientación vertical
            # dibujo = ImageDraw.Draw(imagen)

            # dimensiones = {
            #     'ancho_total': largo1 + largo2 + largo3 + largo4 + 40,  # La suma de los anchos
            #     'alto_total': alto2 + alto1 + alto2,  # La suma de los altos
            #     'ancho_central': largo2,  # El ancho de la parte central de la caja
            #     'alto_central': alto1,   # El alto de la parte central de la caja
            #     'ancho_aleta': largo4,    # El ancho de las aletas laterales de la caja
            #     'alto_aleta': alto2      # El alto de las aletas superiores e inferiores de la caja
            # }

            # # Coordenadas iniciales
            # x_inicial, y_inicial = 50, 50  # Puedes cambiar esto según necesites

            # # Dibuja las líneas externas de la caja
            # dibujo.rectangle([x_inicial, y_inicial, x_inicial + dimensiones['ancho_total'], y_inicial + dimensiones['alto_total']], outline='black')

            # # Dibuja las líneas internas horizontales
            # y_actual = y_inicial + dimensiones['alto_aleta']
            # for _ in range(2):  # Dibuja las dos líneas horizontales
            #     dibujo.line([(x_inicial, y_actual), (x_inicial + dimensiones['ancho_total'], y_actual)], fill='black')
            #     y_actual += dimensiones['alto_central']

            # # Dibuja las líneas internas verticales
            # x_actual = x_inicial + dimensiones['ancho_aleta']
            # for _ in range(4):  # Dibuja las dos líneas verticales
            #     dibujo.line([(x_actual, y_inicial), (x_actual, y_inicial + dimensiones['alto_total'])], fill='black')
            #     x_actual += dimensiones['ancho_central']
            
            # # Ajusta las dimensiones de la imagen al tamaño de la página del PDF
            # ancho_pagina, alto_pagina = letter  # Tamaño de página estándar
            # escala = min(ancho_pagina / dimensiones['ancho_total'], alto_pagina / dimensiones['alto_total'])  # Escala para ajustar la imagen

            # # Generar la imagen en memoria
            # output = io.BytesIO()
            # imagen.save(output, format='PNG')
            # output.seek(0)  # Regresar al comienzo del archivo en memoria

            # Generar PDF
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=letter)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(200, 730, f'Santiago de Chile, {fecha_actual}')

            # Datos del cliente
            altura_cliente = 700  # Iniciar la altura para los detalles del cliente
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_cliente, f'Cliente: {nombre_cliente}')
            p.drawString(50, altura_cliente - 15, f'Correo: {correo_cliente}')
            p.drawString(50, altura_cliente - 30, f'Rut: {rut_cliente}')
            p.drawString(50, altura_cliente - 45, f'Comentario: {comentario}')

            # Línea de separación
            p.setStrokeColor(colors.black)
            p.line(50, altura_cliente - 60, 550, altura_cliente - 60)

            # Detalles de la cotización
            altura_detalle = altura_cliente - 80  # Iniciar la altura para los detalles de la cotización
            
            # Medidas Solicitadas
            altura_detalle -= 20
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas Solicitadas')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} ")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)}")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_max_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja}')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha}',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: {coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricacion: {coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: {precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: {precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)

            #Generar nueva hoja
            # p.showPage()

            # # Añadir la imagen de la caja a la nueva página
            # p.drawImage(output, 50, 25, width=dimensiones['ancho_total'] * escala, height=dimensiones['alto_total'] * escala, mask='auto')

            # Finaliza el PDF
            p.showPage()  # Añade esta línea si necesitas más páginas después
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

            # Cierra el objeto BytesIO
            # output.close()

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