from rest_framework.viewsets import ModelViewSet
from core.models import solicitud_cotizacion
from core.api.serializers import solicitud_cotizacion_serializer

class solicitud_cotizacion_api_view_set(ModelViewSet):
    serializer_class = solicitud_cotizacion_serializer
    queryset = solicitud_cotizacion.objects.all()
