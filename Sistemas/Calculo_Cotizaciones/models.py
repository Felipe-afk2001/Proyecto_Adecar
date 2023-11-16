from django.db import models

# class Usuario(models.Model):
#     id_usuario = models.CharField(max_length=100, primary_key=True)
#     nombre_usuario = models.CharField(max_length=20)
#     correo = models.CharField(max_length=255)
#     nombre_persona = models.CharField(max_length=40)
#     contrasenia = models.CharField(max_length=16)
#     token = models.CharField(max_length=10) # Token de autenticación debe llevar max_length.
#     class Meta:
#         db_table = 'Usuario'
# Este debe ser el usuario admin de django.

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
    telefono = models.DecimalField(max_digits=9, decimal_places=0)
    id_tipo_cliente = models.ForeignKey(Tipo_Cliente, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=50)
    contrasenia = models.CharField(max_length=16)
    class Meta:
        db_table = 'Cliente'

class Solicitud_Cotizacion(models.Model):
    id_cotizacion = models.CharField(max_length=100, primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    largo = models.DecimalField(max_digits=4, decimal_places=0)
    ancho = models.DecimalField(max_digits=4, decimal_places=0)
    alto = models.DecimalField(max_digits=4, decimal_places=0)
    cantidad_caja = models.DecimalField(max_digits=4, decimal_places=0)
    cod_carton = models.CharField(max_length=5)
    comentario = models.CharField(max_length=400)
    class Meta:
        db_table = 'Solicitud_Cotizacion'

class Detalle_Cotizaciones(models.Model):
    id_detalle_cotizacion = models.CharField(max_length=100, primary_key=True)
    id_solicitud = models.ForeignKey(Solicitud_Cotizacion, on_delete=models.CASCADE)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
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