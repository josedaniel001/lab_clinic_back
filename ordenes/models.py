from django.db import models
from pacientes.models import Paciente
from medicos.models import Medico
from examenes.models import Examen
from django.utils import timezone

class Orden(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('VALIDADO', 'Validado'),
        ('CANCELADO', 'Cancelado'),
        ('ENTREGADO', 'Entregado'),
        ('EN PROCESO', 'Procesando'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="ordenes")
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, related_name="ordenes")
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    examenes = models.ManyToManyField(Examen, through='DetalleOrden', related_name='ordenes')

    def __str__(self):
        return f"{self.codigo} - {self.paciente}"

    @property
    def total_examenes(self):
        return self.detalleorden_set.count()

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    resultado_pdf  = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, default='Pendiente')

    def __str__(self):
        return f"{self.orden.codigo} - {self.examen.nombre}"
