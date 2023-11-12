from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

    
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


