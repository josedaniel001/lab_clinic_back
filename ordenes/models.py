from django.db import models
from pacientes.models import Paciente
from medicos.models import Medico
from examenes.models import Examen

from django.utils import timezone
from django.core.exceptions import ValidationError

class Orden(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('VALIDADO', 'Validado'),
        ('CANCELADO', 'Cancelado'),
        ('ENTREGADO', 'Entregado'),
        ('EN PROCESO', 'Procesando'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('NORMAL', 'Normal'),        
    ]

    codigo = models.CharField(max_length=20, unique=True)
    paciente = models.ForeignKey(
    Paciente, 
    on_delete=models.CASCADE, 
    related_name="ordenes",
    null=True,  # <- Permite NULL en la DB
    blank=True  # <- Permite dejarlo vacío en formularios/admin
    )
    donante = models.ForeignKey(
       'banco_sangre.Donante', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ordenes"
    )
    medico = models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, related_name="ordenes")
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    examenes = models.ManyToManyField(Examen, through='DetalleOrden', related_name='ordenes')
    prioridad= models.CharField(max_length=40, choices=PRIORIDAD_CHOICES, default='NORMAL')
    genero_entrevista= models.BooleanField(default=False)
    continuar_entrevista= models.BooleanField(default=True)
    def __str__(self):
        return f"{self.codigo} - {self.paciente}"

    @property
    def total_examenes(self):
        return self.detalleorden_set.count()     

    def clean(self):
        # 🚩 Reglas claras:
        if not self.paciente and not self.donante:
            raise ValidationError("La orden debe tener un Paciente o un Donante.")
    
    def save(self, *args, **kwargs):
        creating = self._state.adding and not self.pk
        super().save(*args, **kwargs)
        
        # Si es una nueva orden con donante, generar código de donante automáticamente
        if creating and self.donante:
            self._generar_codigo_donante()
    
    def _generar_codigo_donante(self):
        """
        Genera automáticamente un código de donante para esta orden.
        """
        try:
            from banco_sangre.models import CodigoDonante
            CodigoDonante.generar_nuevo_codigo(self.donante, self)
        except Exception as e:
            # Si hay error, no fallar la creación de la orden
            print(f"⚠️ Error generando código de donante: {e}")
    
    @property
    def codigo_donante(self):
        """
        Retorna el código de donante asociado a esta orden.
        """
        try:
            from banco_sangre.models import CodigoDonante
            codigo_donante = CodigoDonante.objects.filter(orden=self).first()
            return codigo_donante.codigo if codigo_donante else None
        except:
            return None

class DetalleOrden(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('VALIDADO', 'Validado'),
        ('CANCELADO', 'Cancelado'),
        ('ENTREGADO', 'Entregado'),
        ('EN PROCESO', 'Procesando'),
    ]
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    resultado_pdf  = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')

    def __str__(self):
        return f"{self.orden.codigo} - {self.examen.nombre}"
        
