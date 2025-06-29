# Generated by Django 5.2.3 on 2025-06-20 22:51

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Examen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=100)),
                ('categoria', models.CharField(max_length=100)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tiempo_procesamiento', models.CharField(max_length=100)),
                ('metodologia', models.TextField()),
                ('preparacion_paciente', models.TextField()),
                ('valores_referencia', models.TextField()),
                ('estado', models.CharField(default='Activo', max_length=20)),
                ('fecha_creacion', models.DateField(default=django.utils.timezone.now)),
            ],
        ),
    ]
