# banco_sangre/models.py

from django.db import models
from django.contrib.auth import get_user_model
from ordenes.models import Orden
from django.utils import timezone

User = get_user_model()

class Donante(models.Model):
    cui = models.CharField(max_length=50, unique=True)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=200)
    celular = models.CharField(max_length=20, blank=True)
    sexo = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    edad = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido} ({self.cui})"

class MuestraSangre(models.Model):
    correlativo = models.CharField(max_length=50, unique=True)
    tipo_unidad = models.CharField(max_length=50)  # Plasma, Plaquetas, etc.
    tipo_sangre = models.CharField(max_length=5)
    volumen_ml = models.PositiveIntegerField()
    fecha_extraccion = models.DateField()
    fecha_donacion = models.DateField(null=True, blank=True)
    fecha_validacion = models.DateField(null=True, blank=True)
    fecha_caducidad = models.DateField()
    lote = models.CharField(max_length=50, blank=True)
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    localizacion = models.CharField(max_length=100, blank=True)
    condiciones_almacenamiento = models.CharField(max_length=200, blank=True)
    serologias = models.JSONField(default=dict, blank=True)  # HIV, HepB, HepC, etc.
    observaciones = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Disponible', 'Disponible'),
            ('Reservado', 'Reservado'),
            ('Vencido', 'Vencido'),
            ('Descartado', 'Descartado')
        ]
    )
    donante = models.ForeignKey(Donante, on_delete=models.SET_NULL, null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.correlativo} - {self.tipo_unidad} - {self.tipo_sangre}"
    
# banco_sangre/models.py (continuación)

class Entrevista(models.Model):
    correlativo = models.CharField(max_length=50, unique=True)
    cui = models.CharField(max_length=50)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=200)
    celular = models.CharField(max_length=20, blank=True)
    sexo = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    edad = models.PositiveIntegerField()
    doctor = models.CharField(max_length=100)  # Si es FK, enlázalo igual que tu Orden
    donador_de = models.CharField(max_length=100, blank=True)
    fecha = models.DateField()
    fecha_entrega = models.DateField(null=True, blank=True)
    donante = models.ForeignKey(Donante, on_delete=models.CASCADE, related_name='entrevistas')
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='entrevistas')
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entrevista {self.correlativo} - {self.primer_nombre} {self.primer_apellido}"

class UnidadMuestra(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVADO', 'Reservado'),
        ('VENCIDO', 'Vencido'),
    ]

    TIPO_UNIDAD_CHOICES = [
        ('PLASMA', 'Plasma'),
        ('PAQUETE_GLOBULAR', 'Paquete Globular'),
        ('PLAQUETAS', 'Plaquetas'),
        ('CRIO_PRECIPITADO', 'Crio Precipitado'),
    ]

    # El ID por defecto es AutoField
    id = models.BigAutoField(primary_key=True)

    correlativo = models.CharField(max_length=30, unique=True, blank=True)
    donante = models.ForeignKey(Donante, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    tipo_unidad = models.CharField(max_length=50, choices=TIPO_UNIDAD_CHOICES)
    tipo_sangre = models.CharField(max_length=5)
    volumen_ml = models.PositiveIntegerField()
    fecha_extraccion = models.DateField(default=timezone.now)
    fecha_caducidad = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')

    def __str__(self):
        return f"{self.correlativo} - {self.tipo_unidad} ({self.tipo_sangre})"

    @property
    def dias_vigencia(self):
        delta = (self.fecha_caducidad - timezone.now().date()).days
        return delta

    def save(self, *args, **kwargs):
        creating = self._state.adding and not self.pk
        super().save(*args, **kwargs)

        if creating and not self.correlativo:
            prefix = {
                'PLASMA': 'PLM',
                'PAQUETE_GLOBULAR': 'PGB',
                'PLAQUETAS': 'PLQ',
                'CRIO_PRECIPITADO': 'CRP',
            }.get(self.tipo_unidad, 'UNK')

            self.correlativo = f"{prefix}-{self.pk:04d}"
            UnidadMuestra.objects.filter(pk=self.pk).update(correlativo=self.correlativo)

    class Meta:
        ordering = ['-fecha_extraccion']