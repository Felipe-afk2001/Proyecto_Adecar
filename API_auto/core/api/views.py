from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import math
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def calcular_vista(request):
    try:
        if request.method == 'POST':
            # Obtener datos
            data = request.data

            # Calculos (todos los calculos redondeados)
                #calculo area caja
            largo_maximo_caja = (data.get('largo_caja', 0)+3) + (data.get('ancho_caja', 0)+5) + (data.get('largo_caja', 0)+5) + (data.get('ancho_caja', 0)+3) + 40
            alto_max_caja  = (data.get('alto_caja', 0)+5) + (((data.get('ancho_caja', 0)/2)+3)*2)
            area_caja = largo_maximo_caja * alto_max_caja
            area_caja = math.ceil(area_caja)  

                #calculo area de plancha total (sin contar el exedente)
            area_total_plancha = data.get('largo_plancha', 0) * data.get('ancho_plancha', 0)
            area_total_plancha = math.ceil(area_total_plancha)  

                #calculo exedentes
            exedente_vertical = data.get('ancho_plancha', 0) - largo_maximo_caja
            exedente_horizontal = data.get('largo_plancha', 0) - alto_max_caja

                #obtencion de variable del precio de la plancha 
            precio_plancha = data.get('coste_materia', 0)
            precio_plancha = math.ceil(precio_plancha)  

                #obtencion de variable del porcentaje de utilidad 
            porcentaje_utilidad = data.get('porcentaje_utilidad', 0)

                #obtencion de variable del costo de creacion 
            coste_creacion = data.get('coste_creacion', 0)
            coste_creacion = math.ceil(coste_creacion)  

                #obtencion de variable de cantidad de cajas
            cantidad_caja = data.get('cantidad_caja', 0)

                #calculo de cantidad de planchas
            dif_largo = data.get('largo_plancha', 0) / largo_maximo_caja
            dif_alto = data.get('ancho_plancha', 0) / alto_max_caja

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

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="cotizacion.pdf"'
            # Crear el objeto PDF, usando el objeto HttpResponse como "buffer".
            p = canvas.Canvas(response)

            # Agregar contenido al PDF, por ejemplo:
            # Coordenada inicial y para la primera línea
            y_coordinate = 800

            # Agregar contenido al PDF
            p.drawString(100, y_coordinate, f'Largo total de la caja: {largo_maximo_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'largo_total:  {largo_maximo_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'alto_total: {alto_max_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'precio_plancha: {precio_plancha}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'area_total_plancha: {area_total_plancha}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'area_caja: {area_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'cantidad_cajas: {cantidad_caja}')
            y_coordinate -= 20

            p.drawString(100, y_coordinate, f'cantidad_planchas: {cantidad_plancha}')
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
            p.showPage()
            p.save()

            # Devolver el PDF como respuesta.
            return response

        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)