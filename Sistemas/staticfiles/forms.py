from django import forms
from .models import Parametro, Tipo_Plancha

class CotizacionForm(forms.Form):
    id_cotizacion = forms.IntegerField()
    id_cliente = forms.IntegerField()
    largo = forms.DecimalField(max_digits=10, decimal_places=2)
    ancho = forms.DecimalField(max_digits=10, decimal_places=2)
    alto = forms.DecimalField(max_digits=10, decimal_places=2)
    cantidad_caja = forms.IntegerField()
    cod_carton = forms.CharField(max_length=50)
    comentario = forms.CharField(widget=forms.Textarea)


class ParametroForm(forms.ModelForm):
    class Meta:
        model = Parametro
        fields = ['id_parametro', 'largo_maximo', 'ancho_maximo', 'excedente_horizontal', 'excedente_vertical']
        widgets = {
            'id_parametro': forms.NumberInput(attrs={'placeholder': 'ID Parámetro'}),
            'largo_maximo': forms.NumberInput(attrs={'placeholder': 'Largo Máximo'}),
            'ancho_maximo': forms.NumberInput(attrs={'placeholder': 'Ancho Máximo'}),
            'excedente_horizontal': forms.NumberInput(attrs={'placeholder': 'Excedente Horizontal'}),
            'excedente_vertical': forms.NumberInput(attrs={'placeholder': 'Excedente Vertical'}),        
        }

class PlanchaForm(forms.ModelForm):
    class Meta:
        model = Tipo_Plancha
        fields = ['id_tipo_plancha', 'largo', 'ancho', 'area', 'cod_carton', 'precio_proveedor']
        widgets = {
            'id_tipo_plancha': forms.TextInput(attrs={'placeholder': 'ID Plancha'}),
            'largo': forms.NumberInput(attrs={'placeholder': 'Largo'}),
            'ancho': forms.NumberInput(attrs={'placeholder': 'Ancho'}),
            'area': forms.NumberInput(attrs={'placeholder': 'Área'}), #Agregar acento en el label
            'cod_carton': forms.TextInput(attrs={'placeholder': 'Tipo Carton'}),
            'precio_proveedor': forms.NumberInput(attrs={'placeholder': 'Precio Proveedor'}),
        }