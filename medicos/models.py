from django.db import models
from localizacion.models import Municipio
import datetime

class Medico(models.Model):
    TIPO_DOCUMENTO_CHOICES = (
        ('CC', 'Cédula de ciudadanía'),
        ('DPI', 'Documento Personal de Identificación' ),
        ('CE', 'Cédula de extranjería'),
        ('TI', 'Tarjeta de identidad'),
        ('PA', 'Pasaporte'),
    )

    GENERO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )

    ESPECIALIDAD_CHOISE = (
        ('GEN', 'Medicina General'),
        ('PED', 'Pediatría'),
        ('GIN', 'Ginecología'),
        ('DER', 'Dermatología'),
        ('CAR', 'Cardiología'),
        ('NEU', 'Neurología'),
        ('NEURO', 'Neumología'),
        ('END', 'Endocrinología'),
        ('OFT', 'Oftalmología'),
        ('OTO', 'Otorrinolaringología'),
        ('TRA', 'Traumatología'),
        ('URO', 'Urología'),
        ('PSI', 'Psiquiatría'),
        ('ODO', 'Odontología'),
        ('REU', 'Reumatología'),
        ('GAS', 'Gastroenterología'),
        ('ONC', 'Oncología'),
        ('HEM', 'Hematología'),
        ('CIR', 'Cirugía General'),
        ('CIRP', 'Cirugía Pediátrica'),
        ('CIRC', 'Cirugía Cardiovascular'),
        ('RAD', 'Radiología'),
        ('INT', 'Medicina Interna'),
        ('FOR', 'Medicina Forense'),
        ('ANE', 'Anestesiología'),
    )

    numero_documento = models.CharField(max_length=20, unique=True, default='000000000')
    tipo_documento = models.CharField(max_length=6, choices=TIPO_DOCUMENTO_CHOICES, default='DPI')
    nombres = models.CharField(max_length=100, default='Desconocido')
    apellidos = models.CharField(max_length=100, default='Paciente')    
    telefono_consultorio = models.CharField(max_length=20, default='0000000000')
    celular= models.CharField(max_length=20, default='0000000000')
    codigo_laboratorio= models.CharField(max_length=20, default='XXXXX0')
    email = models.EmailField(default='sin@email.com')
    direccion_consultorio = models.TextField(default='Sin dirección')
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, default='M')
    especialidad_medica = models.CharField(max_length=50, choices=ESPECIALIDAD_CHOISE, default='GEN')    
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def ciudad(self):
        return self.municipio.nombre if self.municipio else None

