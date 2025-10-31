from django.db import models
from django.utils import timezone

class CatalogoUnidadParametro(models.Model):
    """
    Catálogo de unidades de medida para parámetros de laboratorio.
    Permite estandarizar las unidades utilizadas en los resultados.
    """
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Código único de la unidad (ej: GDL, MUL, KUL)"
    )
    nombre = models.CharField(
        max_length=100, 
        help_text="Nombre de la unidad (ej: Gramos por decilitro)"
    )
    simbolo = models.CharField(
        max_length=20, 
        help_text="Símbolo de la unidad (ej: g/dL, M/μL, K/μL)"
    )
    categoria = models.CharField(
        max_length=50,
        help_text="Categoría de la unidad (ej: Hematología, Química, Microbiología)"
    )
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción detallada de la unidad"
    )
    activo = models.BooleanField(
        default=True, 
        help_text="Indica si esta unidad está activa"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['categoria', 'nombre']
        verbose_name = "Unidad de Parámetro"
        verbose_name_plural = "Unidades de Parámetros"
        indexes = [
            models.Index(fields=['categoria']),
            models.Index(fields=['activo']),
        ]
    
    def __str__(self):
        return f"{self.simbolo} - {self.nombre}"