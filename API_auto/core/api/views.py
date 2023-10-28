from rest_framework.viewsets import ModelViewSet
from core.models import solicitud_cotizacion
from core.api.serializers import solicitud_cotizacion_serializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

def calculo_post(request):
        # Obtener los datos del cuerpo de la solicitud POST
        data = request.data

        # Aquí puedes realizar tus cálculos con los datos
        resultado = data['largo'] + data['ancho']  # Ejemplo de cálculo

        # Puedes guardar el resultado en la base de datos si es necesario
        # Ejemplo: nuevo_objeto = TuModelo(campo_resultado=resultado)
        # nuevo_objeto.save()

        # Puedes devolver el resultado como respuesta
        return Response({'resultado': resultado}, status=status.HTTP_201_CREATED)

class solicitud_cotizacion_api_view_set(ModelViewSet):
    serializer_class = solicitud_cotizacion_serializer
    queryset = solicitud_cotizacion.objects.all()

@api_view(['POST'])
def calcular_vista(request):
    # Verifica si la solicitud es de tipo POST
    if request.method == 'POST':
        # Obtén los datos del cuerpo de la solicitud POST
        data = request.data

        # Realiza el cálculo (por ejemplo, suma dos valores)
        resultado = data.get('largo', 0) + data.get('ancho', 0)

        # Puedes realizar cálculos más complejos según tus necesidades

        # Devuelve el resultado en una respuesta JSON
        return Response({'resultado': resultado}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


