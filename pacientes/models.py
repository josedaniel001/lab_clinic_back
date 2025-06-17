from django.db import models
from localizacion.models import Municipio
import datetime

class Paciente(models.Model):
    TIPO_DOCUMENTO_CHOICES = (
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('TI', 'Tarjeta de identidad'),
        ('PA', 'Pasaporte'),
    )

    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )

    ESTADO_CIVIL_CHOICES = (
        ('Soltero', 'Soltero'),
        ('Casado', 'Casado'),
        ('Divorciado', 'Divorciado'),
        ('Viudo', 'Viudo'),
    )

    numero_documento = models.CharField(max_length=20, unique=True, default='00000000')
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    nombres = models.CharField(max_length=100, default='Desconocido')
    apellidos = models.CharField(max_length=100, default='Paciente')
    fecha_nacimiento = models.DateField(default=datetime.date(2000, 1, 1))
    telefono = models.CharField(max_length=20, default='0000000000')
    email = models.EmailField(default='sin@email.com')
    direccion = models.TextField(default='Sin dirección')
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default='M')
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, default='Soltero')
    ocupacion = models.CharField(max_length=100, default='Sin especificar')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def ciudad(self):
        return self.municipio.nombre if self.municipio else None
