from django.db import models
from django.utils import timezone

class Examen(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tiempo_procesamiento = models.CharField(max_length=100)
    metodologia = models.TextField()
    preparacion_paciente = models.TextField()
    valores_referencia = models.TextField()
    estado = models.CharField(max_length=20, default="Activo")
    fecha_creacion = models.DateField(default=timezone.now().date())

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
