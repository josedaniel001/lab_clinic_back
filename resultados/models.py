from django.db import models
from django.utils import timezone
from datetime import date
from ordenes.models import DetalleOrden

def get_today_date():
    return timezone.now().date()

class CatalogoMotivoDenegacion(models.Model):
    """
    Catálogo de motivos de denegación para donantes no aptos
    """
    TIPO_DENEGACION_CHOICES = [
        ('PERMANENTE', 'Permanente - Nunca podrá donar'),
        ('TEMPORAL', 'Temporal - Puede donar después'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, help_text="Código único del motivo")
    nombre = models.CharField(max_length=200, help_text="Nombre del motivo de denegación")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada del motivo")
    tipo_denegacion = models.CharField(
        max_length=20,
        choices=TIPO_DENEGACION_CHOICES,
        default='TEMPORAL',
        help_text="Tipo de denegación: Permanente o Temporal"
    )
    tiempo_diferimiento_dias = models.IntegerField(
        null=True,
        blank=True,
        help_text="Días de diferimiento para denegaciones temporales (ej: 90, 365)"
    )
    activo = models.BooleanField(default=True, help_text="Indica si este motivo está activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['tipo_denegacion', 'codigo']
        verbose_name = "Motivo de Denegación"
        verbose_name_plural = "Motivos de Denegación"
    
    def __str__(self):
        tipo = "🔴" if self.tipo_denegacion == 'PERMANENTE' else "🟡"
        return f"{tipo} {self.codigo} - {self.nombre}"
    
    @property
    def es_permanente(self):
        """Retorna True si es una denegación permanente"""
        return self.tipo_denegacion == 'PERMANENTE'


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
    fecha_resultado = models.DateField(default=get_today_date)
    fecha_validacion = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    prioridad = models.CharField(max_length=20, default='normal')
    
    # Campos para denegación de donante
    motivo_denegacion = models.ForeignKey(
        CatalogoMotivoDenegacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resultados_denegados',
        help_text="Motivo por el cual se deniega la aptitud del donante"
    )
    observaciones_denegacion = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones adicionales sobre la denegación"
    )

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


class HistorialDenegacion(models.Model):
    """
    Registro histórico de cada vez que se deniega la aptitud de un donante.
    Permite llevar trazabilidad completa de las denegaciones.
    """
    donante = models.ForeignKey(
        'banco_sangre.Donante',
        on_delete=models.CASCADE,
        related_name='historial_denegaciones',
        help_text="Donante que fue denegado"
    )
    resultado = models.ForeignKey(
        Resultado,
        on_delete=models.CASCADE,
        related_name='historial_denegaciones',
        help_text="Resultado que generó la denegación"
    )
    orden = models.ForeignKey(
        'ordenes.Orden',
        on_delete=models.CASCADE,
        related_name='historial_denegaciones',
        help_text="Orden asociada a la denegación"
    )
    motivo_denegacion = models.ForeignKey(
        CatalogoMotivoDenegacion,
        on_delete=models.PROTECT,
        related_name='historial_uso',
        help_text="Motivo por el cual se denegó"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        help_text="Observaciones adicionales de la denegación"
    )
    usuario_deniego = models.CharField(
        max_length=100,
        help_text="Usuario que realizó la denegación"
    )
    fecha_denegacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la denegación"
    )
    
    # Información adicional del momento de la denegación
    resultado_examen = models.CharField(
        max_length=200,
        help_text="Nombre del examen que generó la denegación"
    )
    valores_criticos = models.JSONField(
        default=dict,
        blank=True,
        help_text="Valores críticos que motivaron la denegación"
    )
    
    class Meta:
        ordering = ['-fecha_denegacion']
        verbose_name = "Historial de Denegación"
        verbose_name_plural = "Historial de Denegaciones"
        indexes = [
            models.Index(fields=['donante', '-fecha_denegacion']),
            models.Index(fields=['motivo_denegacion']),
        ]
    
    def __str__(self):
        return f"Denegación {self.donante} - {self.motivo_denegacion.nombre} ({self.fecha_denegacion.strftime('%d/%m/%Y')})"
