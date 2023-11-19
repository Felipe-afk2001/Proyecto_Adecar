from django.contrib import admin

from django.contrib import admin
from django import forms
from .models import Solicitud_Cotizacion

class solicitud(admin.ModelAdmin):
    class Meta:
        model = Solicitud_Cotizacion
        fields = '__all__'
admin.site.register(Solicitud_Cotizacion, solicitud)
