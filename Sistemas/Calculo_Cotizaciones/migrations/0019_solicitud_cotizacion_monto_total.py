# Generated by Django 4.2.6 on 2023-11-16 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Calculo_Cotizaciones', '0018_solicitud_cotizacion_fecha_cotizacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitud_cotizacion',
            name='monto_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
    ]
