
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Core.settings')
django.setup()

from Calculo_Cotizaciones.models import Cliente
#Traspaso de datos para crear rut_cliente
for cliente in Cliente.objects.all():
    cliente.rut_cliente_temporal = cliente.id_cliente
    cliente.save()
