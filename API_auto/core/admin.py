from django.contrib import admin
from core.models import solicitud_cotizacion


@admin.register(solicitud_cotizacion)
class solicitud_cotizacion_admin(admin.ModelAdmin):
    list_display = ['id_cotizacion', 'id_cliente', 'largo', 'ancho', 'alto',
                     'cantidad_caja', 'cod_carton', 'comentario']
