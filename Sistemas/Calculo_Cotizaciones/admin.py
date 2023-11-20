from django.contrib import admin

from .models import Solicitud_Cotizacion
class solicitud(admin.ModelAdmin):
    class Meta:
        model = Solicitud_Cotizacion
        fields = 'all'
admin.site.register(Solicitud_Cotizacion, solicitud)