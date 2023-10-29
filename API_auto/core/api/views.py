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
    except AuthenticationFailed:
        return Response({'error': 'Token no válido o ausente'}, status=status.HTTP_401_UNAUTHORIZED)


