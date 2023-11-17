from django.contrib import admin

from django.contrib import admin
from django import forms
from .models import Usuario

class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
    list_display = ('username', 'email', 'nombre', 'apellidos', 'perfil', 'token', 'es_activo', 'es_staff')
    list_filter = ('perfil', 'es_activo', 'es_staff')
    search_fields = ('username', 'email', 'nombre', 'apellidos')
    ordering = ('username',)

admin.site.register(Usuario, UsuarioAdmin)
# Register your models here.
