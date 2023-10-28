from django.db import models

class solicitud_cotizacion(models.Model):
    id_cotizacion = models.IntegerField(primary_key=True)
    id_cliente = models.IntegerField(max_length=int)
    largo = models.DecimalField(max_digits=4, decimal_places=0)
    ancho = models.DecimalField(max_digits=4, decimal_places=0)
    alto = models.DecimalField(max_digits=4, decimal_places=0)
    cantidad_caja = models.DecimalField(max_digits=4, decimal_places=0)
    cod_carton = models.CharField(max_length=5)
    comentario = models.CharField(max_length=400)

    def __str__(self):
        return self.id_cotizacion

