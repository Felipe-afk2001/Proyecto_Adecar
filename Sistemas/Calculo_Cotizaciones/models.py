from django.db import models
from django.utils import timezone
import string
import itertools
from django.db.models.signals import post_save
from django.dispatch import receiver

class Tipo_Plancha(models.Model):
    id_tipo_plancha = models.CharField(max_length=100, primary_key=True)
    largo = models.DecimalField(max_digits=10, decimal_places=2)
    ancho = models.DecimalField(max_digits=10, decimal_places=2)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    cod_carton = models.CharField(max_length=5)
    precio_proveedor = models.DecimalField(max_digits=9, decimal_places=0)
    class Meta:
        db_table = 'Tipo_Plancha'

class Tipo_Cliente(models.Model):
    id_tipo_cliente = models.CharField(max_length=100, primary_key=True)
    tipo_cliente = models.CharField(max_length=50)
    descripcion_tipo_cliente = models.CharField(max_length=400)
    class Meta:
        db_table = 'Tipo_Cliente'

class Cliente(models.Model):
    rut_cliente = models.CharField(max_length=100, primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.CharField(max_length=255)
    class Meta:
        db_table = 'Cliente'

class Solicitud_Cotizacion(models.Model):
    id_cotizacion = models.CharField(max_length=100, primary_key=True)
    rut_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    largo = models.DecimalField(max_digits=4, decimal_places=0)
    ancho = models.DecimalField(max_digits=4, decimal_places=0)
    alto = models.DecimalField(max_digits=4, decimal_places=0)
    cantidad_caja = models.DecimalField(max_digits=4, decimal_places=0)
    cod_carton = models.CharField(max_length=5)
    comentario = models.CharField(max_length=400)
    estado = models.CharField(max_length=50, default='Pendiente')
    fecha_cotizacion = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def nombre_cliente(self):
        return self.rut_cliente.nombre

    @property
    def apellido_cliente(self):
        return self.rut_cliente.apellido

    @property
    def correo_cliente(self):
        return self.rut_cliente.correo

    def save(self, *args, **kwargs):
        if not self.id_cotizacion:
            self.id_cotizacion = self.generate_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_id():
        prefix = 'M'
        largest_id = Solicitud_Cotizacion.objects.all().order_by('-id_cotizacion').first()
        if largest_id:
            num = int(largest_id.id_cotizacion.lstrip(prefix)) + 1
        else:
            num = 1
        # Asegúrate de que el número siempre tenga al menos dos dígitos
        return f'{prefix}{num:02}'

    class Meta:
        db_table = 'Solicitud_Cotizacion'

class Detalle_Cotizaciones(models.Model):
    id_detalle_cotizacion = models.CharField(max_length=100, primary_key=True)
    id_solicitud = models.ForeignKey(Solicitud_Cotizacion, on_delete=models.CASCADE)
    rut_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    largo = models.DecimalField(max_digits=4, decimal_places=0)
    ancho = models.DecimalField(max_digits=4, decimal_places=0)
    alto = models.DecimalField(max_digits=4, decimal_places=0)
    comentario = models.CharField(max_length=400)
    cod_estado = models.DecimalField(max_digits=3, decimal_places=0)
    descripcion_estado = models.CharField(max_length=50)
    precio_cotizacion = models.DecimalField(max_digits=9, decimal_places=0)
    excedente = models.DecimalField(max_digits=4, decimal_places=0)
    id_tipo_plancha = models.ForeignKey(Tipo_Plancha, on_delete=models.CASCADE)
    cantidad_plancha = models.DecimalField(max_digits=4, decimal_places=0)
    cantidad_caja = models.DecimalField(max_digits=4, decimal_places=0)
    class Meta:
        db_table = 'Detalle_Cotizaciones'

class Parametro(models.Model):
    id_parametro = models.DecimalField(max_digits=3, decimal_places=0, primary_key=True)
    largo_maximo = models.DecimalField(max_digits=5, decimal_places=0)
    ancho_maximo = models.DecimalField(max_digits=5, decimal_places=0)
    excedente_horizontal = models.DecimalField(max_digits=5,decimal_places=0)
    excedente_vertical = models.DecimalField(max_digits=5,decimal_places=0)
    class Meta:
        db_table = 'Parametro'

class Historial(models.Model):
    id_historial = models.DecimalField(max_digits=3, decimal_places=0, primary_key=True)
    rut_cliente = models.CharField(max_length=12)
    nombre_cliente = models.CharField(max_length=50)
    apellido_cliente = models.CharField(max_length=50)
    fecha_cotizacion = models.DateTimeField()
    estado_cotizacion = models.CharField(max_length=20)
    cantidad_cajas = models.DecimalField(max_digits=10, decimal_places=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=0)
    class Meta:
        db_table = 'Historial'