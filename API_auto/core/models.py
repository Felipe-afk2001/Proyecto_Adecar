from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class solicitud_cotizacion(models.Model):
    id_cotizacion = models.IntegerField(primary_key=True)
    id_cliente = models.IntegerField()
    largo = models.DecimalField(max_digits=4, decimal_places=0)
    ancho = models.DecimalField(max_digits=4, decimal_places=0)
    alto = models.DecimalField(max_digits=4, decimal_places=0)
    cantidad_caja = models.DecimalField(max_digits=4, decimal_places=0)
    cod_carton = models.CharField(max_length=5)
    comentario = models.CharField(max_length=400)

    def __str__(self):
        return self.id_cotizacion
    
class detalle_cotizacion(models.Model):
    id_detalle_cotizacion = models.IntegerField(primary_key=True, unique=True)
    id_solicitud_cotizacion = models.IntegerField(unique=True)
    id_cliente = models.IntegerField(unique=True)
    largo_caja = models.IntegerField()
    ancho_caja = models.IntegerField()
    alto_caja = models.IntegerField()
    area_caja = models.IntegerField()
    area_plancha = models.IntegerField()
    cant_materia_prima = models.IntegerField()
    coste_materia = models.IntegerField()
    coste_creacion = models.IntegerField()
    precio_caja = models.IntegerField()
    cantidad_caja = models.IntegerField()
    precio_total = models.IntegerField()
    comentario = models.CharField(max_length=400)
    cod_estado = models.CharField(max_length=5)
    porcentaje_utilidad = models.DecimalField(max_digits=4, decimal_places=0)
    excedente = models.IntegerField()
    id_tipo_plancha = models.IntegerField()
    cantidad_plancha = models.IntegerField()
    precio_plancha = models.IntegerField()
    

    def __str__(self):
        return self.id_detalle_cotizacion
    
class UsuarioManager(BaseUserManager):
    def create_user(self, email, username, nombre, apellidos, password=None):
        if not email:
            raise ValueError('El Email es obligatorio')
        usuario = self.model(
            username=username,
            email=self.normalize_email(email),
            nombre=nombre,
            apellidos=apellidos,
        )
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, username, nombre, apellidos, password):
        usuario = self.create_user(
            email=email,
            username=username,
            nombre=nombre,
            apellidos=apellidos,
            password=password,
        )
        usuario.es_staff = True
        usuario.save(using=self._db)
        return usuario

class Usuario(AbstractBaseUser):
    username = models.CharField('nombre de usuario', unique=True, max_length=100)
    email = models.EmailField('correo electronico', unique=True, max_length=258)
    nombre = models.CharField('nombre', max_length=30)
    apellidos = models.CharField('apellidos', max_length=30)
    es_activo = models.BooleanField(default=True)
    es_staff = models.BooleanField(default=False)

    token_safe = models.OneToOneField(Token, on_delete=models.CASCADE, blank=True, null=True)


    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellidos']

    def __str__(self):
        return f'{self.nombre}, {self.apellidos}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.es_staff
    
@receiver(post_save, sender=Usuario)
def crear_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        token, created = Token.objects.get_or_create(user=instance)
        instance.auth_token = token
        instance.save()


