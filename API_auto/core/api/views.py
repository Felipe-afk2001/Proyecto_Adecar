from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])

def calcular_vista(request):
    try:
        if request.method == 'POST':
            data = request.data

            area_caja = (2 * (data.get('ancho_caja', 0) * data.get('largo_caja', 0))) + (2 * (data.get('ancho_caja', 0) * data.get('alto_caja', 0))) + (2 * (data.get('alto_caja', 0) * data.get('largo_caja', 0)))
            area_caja = round(area_caja, 0)  # Redondea el resultado a 0 decimales

            area_plancha = data.get('area_plancha', 0)
            area_plancha = round(area_plancha, 0)  # Redondea el resultado a 0 decimales

            excedente = area_plancha - area_caja
            excedente = round(excedente, 0)  # Redondea el resultado a 0 decimales

            precio_plancha = data.get('coste_materia', 0)
            precio_plancha = round(precio_plancha, 0)  # Redondea el resultado a 0 decimales

            coste_materia_prima = (area_caja * precio_plancha) / area_plancha
            coste_materia_prima = round(coste_materia_prima, 0)  # Redondea el resultado a 0 decimales

            porcentaje_utilidad = data.get('porcentaje_utilidad', 0)

            coste_creacion = data.get('coste_creacion', 0)
            coste_creacion = round(coste_creacion, 0)  # Redondea el resultado a 0 decimales

            precio_caja = (coste_creacion + coste_materia_prima) * porcentaje_utilidad
            precio_caja = round(precio_caja, 0)  # Redondea el resultado a 0 decimales

            cantidad_caja = data.get('cantidad_caja', 0)
            cantidad_caja = round(cantidad_caja, 0)  # Redondea el resultado a 0 decimales

            precio_total = precio_caja * cantidad_caja
            precio_total = round(precio_total, 0)  # Redondea el resultado a 0 decimales

            return Response({
                'precio_plancha': precio_plancha,
                'area_plancha': area_plancha,
                'area_caja': area_caja,
                'excedente': excedente,
                'coste_materia_prima': coste_materia_prima,
                'porcentaje_utilidad': porcentaje_utilidad,
                'coste_creacion': coste_creacion,
                'precio_caja': precio_caja,
                'precio_total': precio_total
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)