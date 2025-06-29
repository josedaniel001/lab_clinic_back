# Generated by Django 5.2.3 on 2025-06-16 04:24

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('localizacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_documento', models.CharField(default='00000000', max_length=20, unique=True)),
                ('tipo_documento', models.CharField(choices=[('CC', 'Cédula de ciudadanía'), ('CE', 'Cédula de extranjería'), ('TI', 'Tarjeta de identidad'), ('PA', 'Pasaporte')], default='CC', max_length=2)),
                ('nombres', models.CharField(default='Desconocido', max_length=100)),
                ('apellidos', models.CharField(default='Paciente', max_length=100)),
                ('fecha_nacimiento', models.DateField(default=datetime.date(2000, 1, 1))),
                ('telefono', models.CharField(default='0000000000', max_length=20)),
                ('email', models.EmailField(default='sin@email.com', max_length=254)),
                ('direccion', models.TextField(default='Sin dirección')),
                ('genero', models.CharField(choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')], default='M', max_length=1)),
                ('estado_civil', models.CharField(choices=[('Soltero', 'Soltero'), ('Casado', 'Casado'), ('Divorciado', 'Divorciado'), ('Viudo', 'Viudo')], default='Soltero', max_length=20)),
                ('ocupacion', models.CharField(default='Sin especificar', max_length=100)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
                ('municipio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='localizacion.municipio')),
            ],
        ),
    ]
