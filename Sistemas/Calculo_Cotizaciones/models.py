from django.db import models

class Usuario(models.Model):
    id_usuario = models.CharField(max_length=100)
    nombre_usuario = models.CharField(max_length=20)
    correo = models.CharField(max_length=255)
    nombre_persona = models.CharField(max_length=40)
    contrasenia = models.CharField(max_length=16)
    token = models.CharField()

class Tipo_Plancha(models.Model):
    id_tipo_plancha = models.CharField(max_length=100)
    largo = models.IntegerField(max_length=4)
    ancho = models.IntegerField(max_length=4)
    alto = models.IntegerField(max_length=4)
    area = models.IntegerField(max_length=4)
    cod_carton = models.CharField(max_length=5)
    descripcion_cod_carton = models.CharField(max_length=50)
    precio_proveedor = models.IntegerField(max_length=9)

class Tipo_Cliente(models.Model):
    id_tipo_cliente = models.CharField(max_length=100)
    tipo_cliente = models.CharField(max_length=50)
    descripcion_tipo_cliente = models.CharField(max_length=400)

class Cliente(models.Model):
    id_cliente = models.CharField(max_length=100)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    correo = models.CharField(max_length=255)
    telefono = models.IntegerField(max_length=9)
    id_tipo_cliente = models.ForeignKey(Tipo_Cliente, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=50)
    contrasenia = models.CharField(max_length=16)

class Solicitud_Cotizacion(models.Model):
    id_cotizacion = models.CharField(max_length=100)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    largo = models.IntegerField(max_length=4)
    ancho = models.IntegerField(max_length=4)
    alto = models.IntegerField(max_length=4)
    cantidad_caja = models.IntegerField(max_length=4)
    cod_carton = models.CharField(max_length=5)
    comentario = models.CharField(max_length=400)

class Detalle_Cotizaciones(models.Model):
    id_detalle_cotizacion = models.CharField(max_length=100) #PK
    id_solicitud_cliente = models.ForeignKey(Solicitud_Cotizacion, on_delete=models.CASCADE)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    largo = models.IntegerField(max_length=4)
    ancho = models.IntegerField(max_length=4)
    alto = models.IntegerField(max_length=4)
    comentario = models.CharField(max_length=400)
    cod_estado = models.IntegerField(max_length=3)
    descripcion_estado = models.CharField(max_length=50)
    precio_cotizacion = models.IntegerField(max_length=9)
    excedente = models.IntegerField(max_length=4)
    id_tipo_plancha = models.ForeignKey(Tipo_Plancha, on_delete=models.CASCADE)
    cantidad_plancha = models.IntegerField(max_length=4)
    cantidad_caja = models.IntegerField(max_length=4)
# Create your models here.
