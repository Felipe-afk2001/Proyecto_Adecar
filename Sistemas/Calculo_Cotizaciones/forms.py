from django import forms
from .models import Parametro

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
        fields = ['id_parametro', 'ancho_maximo', 'excedente_horizontal', 'excedente_vertical', 'largo_maximo']
        widgets = {
            'id_parametro': forms.TextInput(attrs={'placeholder': 'ID Parámetro'}),
            'ancho_maximo': forms.TextInput(attrs={'placeholder': 'Ancho Máximo'}),
            'excedente_horizontal': forms.TextInput(attrs={'placeholder': 'Excedente Horizontal'}),
            'excedente_vertical': forms.TextInput(attrs={'placeholder': 'Excedente Vertical'}),
            'largo_maximo': forms.TextInput(attrs={'placeholder': 'Largo Máximo'}),
        }