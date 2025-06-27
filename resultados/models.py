from django.db import models
from django.utils import timezone
from ordenes.models import DetalleOrden

class Resultado(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
        ('VALIDADO', 'Validado'),
        ('EN PROCESO', 'En Proceso'),
    ]

    resultado = models.OneToOneField(
        DetalleOrden,
        on_delete=models.CASCADE,
        related_name='resultado'
    )
    observaciones = models.TextField(blank=True, null=True)
    validado_por = models.CharField(max_length=100, blank=True, null=True)
    fecha_resultado = models.DateField(default=timezone.now)
    fecha_validacion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(max_length=20, default='normal')

    def __str__(self):
        return f"Ruta archivo C:/Ordenes_Resultados/{self.detalle_orden.examen.nombre}/Orden-{self.detalle_orden.orden.codigo}"

class ResultadoDetalle(models.Model):
    resultado = models.ForeignKey(Resultado, on_delete=models.CASCADE, related_name='valores')
    parametro = models.CharField(max_length=100)
    valor = models.CharField(max_length=50)
    unidad = models.CharField(max_length=20)
    rango_normal = models.CharField(max_length=100)
    estado = models.CharField(max_length=20)  # ej: normal, alto, bajo

    def __str__(self):
        return f"{self.parametro}: {self.valor} {self.unidad}"
