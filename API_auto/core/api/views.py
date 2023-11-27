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
from PIL import Image, ImageDraw, ImageFont
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

                #calculo de precio de total de cajas
            precio_total = (coste_creacion * cantidad_caja) + coste_materia_prima 
            precio_total = math.ceil(precio_total)

                #calculo de precio de caja unitaria
            precio_caja = (precio_total/cantidad_caja) 
            precio_caja = math.ceil(precio_caja)  

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
                'fecha_vencimiento' : fecha_vencimiento,
                'cantidad_x_plancha' : caja_x_planchas
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
                #variables medidas
            largo1 = (data.get('largo_caja', 0)+3)
            largo2 = (data.get('ancho_caja', 0)+5)
            largo3 = (data.get('largo_caja', 0)+5)
            largo4 = (data.get('ancho_caja', 0)+3)
            alto1 = (data.get('alto_caja', 0)+5)
            alto2 = ((data.get('ancho_caja', 0)/2)+3)

                #variables cliente
            nombre_cliente = data.get('nombre_cliente', 0)
            rut_cliente = data.get('rut_cliente', 0)
            correo_cliente = data.get('correo_cliente', 0)

                #varibles solicitud
            id_solicitud = data.get('id_solicitud', 0)
            comentario = data.get('comentario', 0)

                #variables caja
            largo_maximo_caja = data.get('largo_maximo_caja')
            alto_maximo_caja = data.get('alto_maximo_caja')
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
            
                # Funcion para hacer lineas punteadas
            def dibujar_linea_punteada(dibujo, inicio, fin, dash=(5, 3), fill='white'):
                    x1, y1 = inicio
                    x2, y2 = fin
                    dx = x2 - x1
                    dy = y2 - y1
                    distancia = math.sqrt(dx*dx + dy*dy)
                    dash_longitud, espacio_longitud = dash

                    if dx == 0:  # Línea vertical
                        num_dashes = abs(y2 - y1) // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud)
                            y_fin = y_inicio + dash_longitud
                            dibujo.line([(x1, y_inicio), (x1, min(y_fin, y2))], fill=fill)
                    else:  # Línea no vertical
                        num_dashes = distancia // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            x_inicio = x1 + i * (dash_longitud + espacio_longitud) * dx / distancia
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud) * dy / distancia
                            x_fin = x_inicio + dash_longitud * dx / distancia
                            y_fin = y_inicio + dash_longitud * dy / distancia
                            dibujo.line([(x_inicio, y_inicio), (x_fin, y_fin)], fill=fill)           
            
            def crear_diseno_caja(dimensiones, nombre_archivo):
            # Crea una nueva imagen con fondo blanco con orientación horizontal

                imagen = Image.new('RGB', (dimensiones['ancho_imagen'], dimensiones['alto_imagen']), 'white')
                dibujo = ImageDraw.Draw(imagen)

                # Coordenadas iniciales
                x_inicial, y_inicial = 50, 50  # Puede que necesites ajustar esto

                # Dibuja las líneas externas de la caja
                dibujo.rectangle([x_inicial, y_inicial, x_inicial + dimensiones['ancho_total'], y_inicial + dimensiones['alto_total']], outline='black')

                # Variables de líneas horizontales
                l1 = y_inicial + dimensiones['largo1']
                l2 = l1 + dimensiones['largo2']
                l3 = l2 + dimensiones['largo3']
                l4 = l3 + dimensiones['largo4']
                
                # Variables de líneas verticales
                a1 = x_inicial + dimensiones['alto1']
                a2 = a1 + dimensiones['alto2']
                
                # Dibuja las líneas verticales internas
                for l in [l1, l2, l3, l4]:
                    dibujo.line([(l, y_inicial), (l, y_inicial + dimensiones['alto_total'])], fill='black')
                
                # Dibuja las líneas horizontales internas
                for a in [a1, a2]:
                    dibujo.line([(x_inicial, a), (x_inicial + dimensiones['ancho_total'], a)], fill='black')


                # Uso de la función
                dibujar_linea_punteada(dibujo, (l1, y_inicial), (l1, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial), (l2, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial), (l3, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                

                    # Especifica la fuente y el tamaño
                try:
                    fuente = ImageFont.truetype("arial.ttf", 20)  # Cambia 20 al tamaño que desees
                except IOError:
                    fuente = ImageFont.load_default()

                # Variables texto
                vt1 = (dimensiones['largo1'] + (x_inicial + dimensiones['largo2'])/2) - 20
                vt2 = (dimensiones['largo1'] + dimensiones['largo2'] + (x_inicial + dimensiones['largo3'])/2) - 20
                vt3 = (dimensiones['largo1'] + dimensiones['largo2'] + dimensiones['largo3'] + (x_inicial + dimensiones['largo4'])/2) - 20
                vt4 = (dimensiones['alto1'] + (y_inicial + dimensiones['alto2']/2))
                vt5 = (dimensiones['alto1'] + dimensiones['alto2'] + (y_inicial + dimensiones['alto1']/2))

                textos = [
                    # (x, y, texto)
                    (((x_inicial+dimensiones['largo1'])/2)-20, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt4,f"{int(dimensiones['alto2'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt4,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto2'])}"),
                    (vt2, vt4,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto2'])}"),
                    (vt3, vt4,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto2'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt5,f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt5,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, vt5,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, vt5,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                ]
                
                for x, y, texto in textos:
                    dibujo.text((x, y), texto, fill='black', font=fuente)
                
                # Guarda la imagen
                imagen.save(nombre_archivo)
                
                # Recorte de la imagen si es necesario
                largo_final = x_inicial + dimensiones['ancho_total'] + 50
                alto_final = y_inicial + dimensiones['alto_total'] + 50

                if largo_final < dimensiones['ancho_imagen'] or alto_final < dimensiones['alto_imagen']:
                    recorte = (0, 0, largo_final, alto_final)
                    imagen = imagen.crop(recorte)

                # Guarda la imagen
                imagen.save(nombre_archivo)

            dimensiones_caja = {
                    'ancho_total': largo_maximo_caja,  # La suma de los anchos
                    'alto_total': alto_maximo_caja,  # La suma de los altos
                    'largo1': largo1,
                    'largo2': largo2,
                    'largo3': largo3,
                    'largo4': largo4,
                    'alto1': alto2,
                    'alto2': alto1,
                    'ancho_imagen': 2500,
                    'alto_imagen': 1800
                }
            
            dibujo = 'diseno_caja.png'
            crear_diseno_caja(dimensiones_caja, dibujo)

            # Generar PDF
            pagesize=letter
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=pagesize)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 25)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(320, 730, f'Santiago de Chile, {fecha_actual}')
            
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
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} mm")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)} mm")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja} mm²')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha} mm²',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja} unidades',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: ${coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}%',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricación: ${coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: ${precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: ${precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)

            # Añadir una nueva página al PDF
            p.showPage()

            # Calcular el tamaño de la imagen para escalar
            imagen = Image.open(dibujo)
            ancho_imagen, alto_imagen = imagen.size
            if ancho_imagen > 1500 or alto_imagen > 850:
                escala = min((pagesize[0] - 200) / ancho_imagen, (pagesize[1] - 200) / alto_imagen)
            else:
                escala = min((pagesize[0] - 100) / ancho_imagen, (pagesize[1] - 100) / alto_imagen)
            ancho_escalado = ancho_imagen * escala
            alto_escalado = alto_imagen * escala

            # Variable de posicion eje y
            altura_imagen2 =pagesize[1] - 80

            # Texto de como cortar la imagen
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_imagen2, 'Instrucciones para Armar la Caja')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pasos a Seguir:')
            altura_imagen2 -=20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_imagen2, 'Recorta: Corta a lo largo de los bordes externos sólidos del dibujo.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Corta las lineas punteadas del dibujo hasta que llegues a las lineas enteras.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Dobla: Haz un pliegue a lo largo de todas las líneas interiores sólidas.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pega: Aplica pegamento en el rectangulo mas pequeño y únelo con el lado de')
            altura_imagen2 -=15
            p.drawString(50, altura_imagen2, 'la caja del otro extremo para formar la caja.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Arma: Comienza por el fondo de la caja y finaliza con la tapa.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, '¡Tu caja está lista!')
            altura_imagen2 -=30

           # Hacer lineas punteadas en pdf
            p.setDash([5, 3])
            p.line(25, altura_imagen2, 580, altura_imagen2)

            # Insertar la imagen escalada en la nueva página
            p.drawImage(dibujo, 50, (altura_imagen2 - alto_escalado - 50), width=ancho_escalado, height=alto_escalado)

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
            #variables medidas
            largo1 = (data.get('largo_caja', 0)+3)
            largo2 = (data.get('ancho_caja', 0)+5)
            largo3 = (data.get('largo_caja', 0)+5)
            largo4 = (data.get('ancho_caja', 0)+3)
            alto1 = (data.get('alto_caja', 0)+5)
            alto2 = ((data.get('ancho_caja', 0)/2)+3)

                #variables cliente
            nombre_cliente = data.get('nombre_cliente', 0)
            rut_cliente = data.get('rut_cliente', 0)
            correo_cliente = data.get('correo_cliente', 0)

                #varibles solicitud
            id_solicitud = data.get('id_solicitud', 0)
            comentario = data.get('comentario', 0)

                #variables caja
            largo_maximo_caja = data.get('largo_maximo_caja')
            alto_maximo_caja = data.get('alto_maximo_caja')
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

            def dibujar_linea_punteada(dibujo, inicio, fin, dash=(5, 3), fill='white'):
                    x1, y1 = inicio
                    x2, y2 = fin
                    dx = x2 - x1
                    dy = y2 - y1
                    distancia = math.sqrt(dx*dx + dy*dy)
                    dash_longitud, espacio_longitud = dash

                    if dx == 0:  # Línea vertical
                        num_dashes = abs(y2 - y1) // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud)
                            y_fin = y_inicio + dash_longitud
                            dibujo.line([(x1, y_inicio), (x1, min(y_fin, y2))], fill=fill)
                    else:  # Línea no vertical
                        num_dashes = distancia // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            x_inicio = x1 + i * (dash_longitud + espacio_longitud) * dx / distancia
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud) * dy / distancia
                            x_fin = x_inicio + dash_longitud * dx / distancia
                            y_fin = y_inicio + dash_longitud * dy / distancia
                            dibujo.line([(x_inicio, y_inicio), (x_fin, y_fin)], fill=fill)           
            
            def crear_diseno_caja(dimensiones, nombre_archivo):
            # Crea una nueva imagen con fondo blanco con orientación horizontal

                imagen = Image.new('RGB', (dimensiones['ancho_imagen'], dimensiones['alto_imagen']), 'white')
                dibujo = ImageDraw.Draw(imagen)

                # Coordenadas iniciales
                x_inicial, y_inicial = 50, 50  # Puede que necesites ajustar esto

                # Dibuja las líneas externas de la caja
                dibujo.rectangle([x_inicial, y_inicial, x_inicial + dimensiones['ancho_total'], y_inicial + dimensiones['alto_total']], outline='black')

                # Variables de líneas horizontales
                l1 = y_inicial + dimensiones['largo1']
                l2 = l1 + dimensiones['largo2']
                l3 = l2 + dimensiones['largo3']
                l4 = l3 + dimensiones['largo4']
                
                # Variables de líneas verticales
                a1 = x_inicial + dimensiones['alto1']
                a2 = a1 + dimensiones['alto2']
                
                # Dibuja las líneas verticales internas
                for l in [l1, l2, l3, l4]:
                    dibujo.line([(l, y_inicial), (l, y_inicial + dimensiones['alto_total'])], fill='black')
                
                # Dibuja las líneas horizontales internas
                for a in [a1, a2]:
                    dibujo.line([(x_inicial, a), (x_inicial + dimensiones['ancho_total'], a)], fill='black')


                # Uso de la función
                dibujar_linea_punteada(dibujo, (l1, y_inicial), (l1, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial), (l2, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial), (l3, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                

                    # Especifica la fuente y el tamaño
                try:
                    fuente = ImageFont.truetype("arial.ttf", 20)  # Cambia 20 al tamaño que desees
                except IOError:
                    fuente = ImageFont.load_default()

                # Variables texto
                vt1 = (dimensiones['largo1'] + (x_inicial + dimensiones['largo2'])/2) - 20
                vt2 = (dimensiones['largo1'] + dimensiones['largo2'] + (x_inicial + dimensiones['largo3'])/2) - 20
                vt3 = (dimensiones['largo1'] + dimensiones['largo2'] + dimensiones['largo3'] + (x_inicial + dimensiones['largo4'])/2) - 20
                vt4 = (dimensiones['alto1'] + (y_inicial + dimensiones['alto2']/2))
                vt5 = (dimensiones['alto1'] + dimensiones['alto2'] + (y_inicial + dimensiones['alto1']/2))

                textos = [
                    # (x, y, texto)
                    (((x_inicial+dimensiones['largo1'])/2)-20, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt4,f"{int(dimensiones['alto2'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt4,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto2'])}"),
                    (vt2, vt4,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto2'])}"),
                    (vt3, vt4,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto2'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt5,f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt5,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, vt5,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, vt5,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                ]
                
                for x, y, texto in textos:
                    dibujo.text((x, y), texto, fill='black', font=fuente)
                
                # Guarda la imagen
                imagen.save(nombre_archivo)
                
                # Recorte de la imagen si es necesario
                largo_final = x_inicial + dimensiones['ancho_total'] + 50
                alto_final = y_inicial + dimensiones['alto_total'] + 50

                if largo_final < dimensiones['ancho_imagen'] or alto_final < dimensiones['alto_imagen']:
                    recorte = (0, 0, largo_final, alto_final)
                    imagen = imagen.crop(recorte)

                # Guarda la imagen
                imagen.save(nombre_archivo)

            dimensiones_caja = {
                    'ancho_total': largo_maximo_caja,  # La suma de los anchos
                    'alto_total': alto_maximo_caja,  # La suma de los altos
                    'largo1': largo1,
                    'largo2': largo2,
                    'largo3': largo3,
                    'largo4': largo4,
                    'alto1': alto2,
                    'alto2': alto1,
                    'ancho_imagen': 2500,
                    'alto_imagen': 1800
                }
            
            dibujo = 'diseno_caja.png'
            crear_diseno_caja(dimensiones_caja, dibujo)

            # Generar PDF
            pagesize=letter
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=pagesize)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 25)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(320, 730, f'Santiago de Chile, {fecha_actual}')
            
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
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} mm")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)} mm")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja} mm²')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha} mm²',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja} unidades',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: ${coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}%',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricación: ${coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: ${precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: ${precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)

            # Añadir una nueva página al PDF
            p.showPage()

            # Calcular el tamaño de la imagen para escalar
            imagen = Image.open(dibujo)
            ancho_imagen, alto_imagen = imagen.size
            if ancho_imagen > 1500 or alto_imagen > 850:
                escala = min((pagesize[0] - 200) / ancho_imagen, (pagesize[1] - 200) / alto_imagen)
            else:
                escala = min((pagesize[0] - 100) / ancho_imagen, (pagesize[1] - 100) / alto_imagen)
            ancho_escalado = ancho_imagen * escala
            alto_escalado = alto_imagen * escala

            # Variable de posicion eje y
            altura_imagen2 =pagesize[1] - 80

            # Texto de como cortar la imagen
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_imagen2, 'Instrucciones para Armar la Caja')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pasos a Seguir:')
            altura_imagen2 -=20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_imagen2, 'Recorta: Corta a lo largo de los bordes externos sólidos del dibujo.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Corta las lineas punteadas del dibujo hasta que llegues a las lineas enteras.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Dobla: Haz un pliegue a lo largo de todas las líneas interiores sólidas.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pega: Aplica pegamento en el rectangulo mas pequeño y únelo con el lado de')
            altura_imagen2 -=15
            p.drawString(50, altura_imagen2, 'la caja del otro extremo para formar la caja.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Arma: Comienza por el fondo de la caja y finaliza con la tapa.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, '¡Tu caja está lista!')
            altura_imagen2 -=30

           # Hacer lineas punteadas en pdf
            p.setDash([5, 3])
            p.line(25, altura_imagen2, 580, altura_imagen2)

            # Insertar la imagen escalada en la nueva página
            p.drawImage(dibujo, 50, (altura_imagen2 - alto_escalado - 50), width=ancho_escalado, height=alto_escalado)

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
                        Puedes hacer esto a travez de nuestra pagina http://127.0.0.1:8001/compra/{id_solicitud}
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
            alto_maximo_caja  = alto1 + (alto2 * 2)
            area_caja = largo_maximo_caja * alto_maximo_caja
            area_caja = math.ceil(area_caja)  

                #calculo area de plancha total (sin contar el exedente)
            area_total_plancha = largo_plancha * ancho_plancha
            area_total_plancha = math.ceil(area_total_plancha)  


                #calculo de cantidad de planchas
            dif_largo = largo_plancha / largo_maximo_caja
            dif_largo = int(dif_largo)
            dif_alto = ancho_plancha / alto_maximo_caja
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

                #calculo de precio de total de cajas
            precio_total = (coste_creacion * cantidad_caja) + coste_materia_prima 
            precio_total = math.ceil(precio_total)

                #calculo de precio de caja unitaria
            precio_caja = (precio_total/cantidad_caja) 
            precio_caja = math.ceil(precio_caja)  

                #calculo fecha de vencimiento
            fecha_actual = timezone.now()
            fecha_vencimiento = fecha_actual + timedelta(days=10)  
            fecha_vencimiento = fecha_vencimiento.strftime('%d-%m-%Y')
            fecha_actual = fecha_actual.strftime('%d-%m-%Y')


            def dibujar_linea_punteada(dibujo, inicio, fin, dash=(5, 3), fill='white'):
                    x1, y1 = inicio
                    x2, y2 = fin
                    dx = x2 - x1
                    dy = y2 - y1
                    distancia = math.sqrt(dx*dx + dy*dy)
                    dash_longitud, espacio_longitud = dash

                    if dx == 0:  # Línea vertical
                        num_dashes = abs(y2 - y1) // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud)
                            y_fin = y_inicio + dash_longitud
                            dibujo.line([(x1, y_inicio), (x1, min(y_fin, y2))], fill=fill)
                    else:  # Línea no vertical
                        num_dashes = distancia // (dash_longitud + espacio_longitud)
                        for i in range(int(num_dashes)):
                            x_inicio = x1 + i * (dash_longitud + espacio_longitud) * dx / distancia
                            y_inicio = y1 + i * (dash_longitud + espacio_longitud) * dy / distancia
                            x_fin = x_inicio + dash_longitud * dx / distancia
                            y_fin = y_inicio + dash_longitud * dy / distancia
                            dibujo.line([(x_inicio, y_inicio), (x_fin, y_fin)], fill=fill)           
            
            def crear_diseno_caja(dimensiones, nombre_archivo):
            # Crea una nueva imagen con fondo blanco con orientación horizontal

                imagen = Image.new('RGB', (dimensiones['ancho_imagen'], dimensiones['alto_imagen']), 'white')
                dibujo = ImageDraw.Draw(imagen)

                # Coordenadas iniciales
                x_inicial, y_inicial = 50, 50  # Puede que necesites ajustar esto

                # Dibuja las líneas externas de la caja
                dibujo.rectangle([x_inicial, y_inicial, x_inicial + dimensiones['ancho_total'], y_inicial + dimensiones['alto_total']], outline='black')

                # Variables de líneas horizontales
                l1 = y_inicial + dimensiones['largo1']
                l2 = l1 + dimensiones['largo2']
                l3 = l2 + dimensiones['largo3']
                l4 = l3 + dimensiones['largo4']
                
                # Variables de líneas verticales
                a1 = x_inicial + dimensiones['alto1']
                a2 = a1 + dimensiones['alto2']
                
                # Dibuja las líneas verticales internas
                for l in [l1, l2, l3, l4]:
                    dibujo.line([(l, y_inicial), (l, y_inicial + dimensiones['alto_total'])], fill='black')
                
                # Dibuja las líneas horizontales internas
                for a in [a1, a2]:
                    dibujo.line([(x_inicial, a), (x_inicial + dimensiones['ancho_total'], a)], fill='black')


                # Uso de la función
                dibujar_linea_punteada(dibujo, (l1, y_inicial), (l1, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial), (l2, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial), (l3, y_inicial + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l1, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l2, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                dibujar_linea_punteada(dibujo, (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2']), (l3, y_inicial + dimensiones['alto1'] + dimensiones['alto2'] + dimensiones['alto1']), dash=(2, 5), fill='white')
                

                    # Especifica la fuente y el tamaño
                try:
                    fuente = ImageFont.truetype("arial.ttf", 20)  # Cambia 20 al tamaño que desees
                except IOError:
                    fuente = ImageFont.load_default()

                # Variables texto
                vt1 = (dimensiones['largo1'] + (x_inicial + dimensiones['largo2'])/2) - 20
                vt2 = (dimensiones['largo1'] + dimensiones['largo2'] + (x_inicial + dimensiones['largo3'])/2) - 20
                vt3 = (dimensiones['largo1'] + dimensiones['largo2'] + dimensiones['largo3'] + (x_inicial + dimensiones['largo4'])/2) - 20
                vt4 = (dimensiones['alto1'] + (y_inicial + dimensiones['alto2']/2))
                vt5 = (dimensiones['alto1'] + dimensiones['alto2'] + (y_inicial + dimensiones['alto1']/2))

                textos = [
                    # (x, y, texto)
                    (((x_inicial+dimensiones['largo1'])/2)-20, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, (y_inicial + dimensiones['alto1']/2),f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt4,f"{int(dimensiones['alto2'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt4,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto2'])}"),
                    (vt2, vt4,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto2'])}"),
                    (vt3, vt4,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto2'])}"),
                    (((x_inicial+dimensiones['largo1'])/2)-20, vt5,f"{int(dimensiones['largo1'])}x{int(dimensiones['alto1'])}"),
                    (vt1, vt5,f"{int(dimensiones['largo2'])}x{int(dimensiones['alto1'])}"),
                    (vt2, vt5,f"{int(dimensiones['largo3'])}x{int(dimensiones['alto1'])}"),
                    (vt3, vt5,f"{int(dimensiones['largo4'])}x{int(dimensiones['alto1'])}"),
                ]
                
                for x, y, texto in textos:
                    dibujo.text((x, y), texto, fill='black', font=fuente)
                
                # Guarda la imagen
                imagen.save(nombre_archivo)
                
                # Recorte de la imagen si es necesario
                largo_final = x_inicial + dimensiones['ancho_total'] + 50
                alto_final = y_inicial + dimensiones['alto_total'] + 50

                if largo_final < dimensiones['ancho_imagen'] or alto_final < dimensiones['alto_imagen']:
                    recorte = (0, 0, largo_final, alto_final)
                    imagen = imagen.crop(recorte)

                # Guarda la imagen
                imagen.save(nombre_archivo)

            dimensiones_caja = {
                    'ancho_total': largo_maximo_caja,  # La suma de los anchos
                    'alto_total': alto_maximo_caja,  # La suma de los altos
                    'largo1': largo1,
                    'largo2': largo2,
                    'largo3': largo3,
                    'largo4': largo4,
                    'alto1': alto2,
                    'alto2': alto1,
                    'ancho_imagen': 2500,
                    'alto_imagen': 1800
                }
            
            dibujo = 'diseno_caja.png'
            crear_diseno_caja(dimensiones_caja, dibujo)

            # Generar PDF
            pagesize=letter
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{id_solicitud}.pdf"'
            p = canvas.Canvas(response, pagesize=pagesize)

            # Configuraciones de estilo
            p.setFont("Helvetica-Bold", 25)
            p.drawString(50, 750, "Adecar")  # Logo o nombre de la empresa
            p.setFont("Helvetica", 16)
            p.drawString(50, 730, f'Cotización N° {id_solicitud}')
            p.drawString(320, 730, f'Santiago de Chile, {fecha_actual}')
            
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
            p.drawString(50, altura_detalle, f'Largo Caja: {data.get("largo_caja", 0)} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Ancho Caja: {data.get('ancho_caja', 0)} mm")
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f"Alto Caja: {data.get('alto_caja', 0)} mm")
            altura_detalle -= 30
            
            # Medidas en Plano
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Medidas en Plano')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Largo total de la caja: {largo_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Alto total de la caja: {alto_maximo_caja} mm')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la caja: {area_caja} mm²')
            altura_detalle -= 30

            # Plancha Utilizada
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Plancha Utilizada')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Tipo de plancha: {id_tipo_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Area total de la plancha: {area_total_plancha} mm²',)
            altura_detalle -= 30

            # Costos
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Costos')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Cantidad de cajas solicitadas: {cantidad_caja} unidades',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Cantidad de planchas necesitadas: {cantidad_plancha}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costos por la cantidad de planchas: ${coste_materia_prima}',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Porcentaje de venta: {porcentaje_utilidad}%',)
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Costo de fabricación: ${coste_creacion}',)
            altura_detalle -= 30

            # Precios Finales
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_detalle, 'Precios Finales')
            altura_detalle -= 20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_detalle, f'Precio Unitario por Caja: ${precio_caja}')
            altura_detalle -= 15
            p.drawString(50, altura_detalle, f'Precio Total por Cajas: ${precio_total}')
            altura_detalle -= 25

            #linea final
            p.setStrokeColor(colors.black)
            p.line(50, altura_detalle - 10, 550, altura_detalle - 10)

            # Añadir una nueva página al PDF
            p.showPage()

            # Calcular el tamaño de la imagen para escalar
            imagen = Image.open(dibujo)
            ancho_imagen, alto_imagen = imagen.size
            if ancho_imagen > 1500 or alto_imagen > 850:
                escala = min((pagesize[0] - 200) / ancho_imagen, (pagesize[1] - 200) / alto_imagen)
            else:
                escala = min((pagesize[0] - 100) / ancho_imagen, (pagesize[1] - 100) / alto_imagen)
            ancho_escalado = ancho_imagen * escala
            alto_escalado = alto_imagen * escala

            # Variable de posicion eje y
            altura_imagen2 =pagesize[1] - 80

            # Texto de como cortar la imagen
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, altura_imagen2, 'Instrucciones para Armar la Caja')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pasos a Seguir:')
            altura_imagen2 -=20
            p.setFont("Helvetica", 12)
            p.drawString(50, altura_imagen2, 'Recorta: Corta a lo largo de los bordes externos sólidos del dibujo.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Corta las lineas punteadas del dibujo hasta que llegues a las lineas enteras.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Dobla: Haz un pliegue a lo largo de todas las líneas interiores sólidas.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Pega: Aplica pegamento en el rectangulo mas pequeño y únelo con el lado de')
            altura_imagen2 -=15
            p.drawString(50, altura_imagen2, 'la caja del otro extremo para formar la caja.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, 'Arma: Comienza por el fondo de la caja y finaliza con la tapa.')
            altura_imagen2 -=20
            p.drawString(50, altura_imagen2, '¡Tu caja está lista!')
            altura_imagen2 -=30

           # Hacer lineas punteadas en pdf
            p.setDash([5, 3])
            p.line(25, altura_imagen2, 580, altura_imagen2)

            # Insertar la imagen escalada en la nueva página
            p.drawImage(dibujo, 50, (altura_imagen2 - alto_escalado - 50), width=ancho_escalado, height=alto_escalado)

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
                        Puedes hacer esto a travez de nuestra pagina http://127.0.0.1:8001/compra/{id_solicitud}
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
