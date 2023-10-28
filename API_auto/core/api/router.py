from rest_framework.routers import DefaultRouter
from core.api.views import solicitud_cotizacion_api_view_set

router_solicitud = DefaultRouter()

router_solicitud.register(prefix='solicitud', basename='solicitud',viewset= solicitud_cotizacion_api_view_set)