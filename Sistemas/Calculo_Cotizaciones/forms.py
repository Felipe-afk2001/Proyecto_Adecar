from django import forms

class CotizacionForm(forms.Form):
    id_cotizacion = forms.IntegerField()
    id_cliente = forms.IntegerField()
    largo = forms.DecimalField(max_digits=10, decimal_places=2)
    ancho = forms.DecimalField(max_digits=10, decimal_places=2)
    alto = forms.DecimalField(max_digits=10, decimal_places=2)
    cantidad_caja = forms.IntegerField()
    cod_carton = forms.CharField(max_length=50)
    comentario = forms.CharField(widget=forms.Textarea)