from rest_framework.serializers import ModelSerializer
from core.models import solicitud_cotizacion

class solicitud_cotizacion_serializer(ModelSerializer):
    class Meta:
        model = solicitud_cotizacion
        fields = ['id_cotizacion', 'id_cliente', 'largo', 'ancho', 'alto',
                  'cantidad_caja', 'cod_carton', 'comentario']
        