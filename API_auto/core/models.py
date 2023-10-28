from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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

@receiver(post_save, sender= User)
def crear_auth_token(sender, instance= None, created = False, **kwargs):
    if created:
        Token.objects.create(user=instance)

