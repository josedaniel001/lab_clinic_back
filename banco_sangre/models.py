# banco_sangre/models.py

from django.db import models
from django.contrib.auth import get_user_model
from ordenes.models import Orden
from localizacion.models import Municipio
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
    ocupacion = models.CharField(max_length=100, default='Sin especificar')
    municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True)
    apto_donacion=  models.BooleanField(default=False)
    tiene_entrevista_apro= models.BooleanField(default=False)
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido} ({self.cui})"
    
    @property
    def ciudad(self):
        return self.municipio.nombre if self.municipio else None

class Lote(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    responsable = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Lote {self.codigo}"
 
# banco_sangre/models.py (continuación)

class Entrevista(models.Model):
    correlativo = models.CharField(max_length=50, unique=True)
    cui = models.CharField(max_length=50)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    sexo = models.CharField(max_length=20)
    grupo_etnico = models.CharField(max_length=50, blank=True)
    fecha_nacimiento = models.DateField()
    edad = models.PositiveIntegerField()
    lugar_nacimiento = models.CharField(max_length=100)
    nacionalidad = models.CharField(max_length=50)
    ocupacion = models.CharField(max_length=100)
    comunidad_linguistica = models.CharField(max_length=100, blank=True)
    estado_civil = models.CharField(max_length=50)
    direccion_casa = models.CharField(max_length=200)
    telefono_casa = models.CharField(max_length=20)
    correo = models.EmailField()
    direccion_trabajo = models.CharField(max_length=200, blank=True)
    telefono_trabajo = models.CharField(max_length=20, blank=True)
    tipo_sangre = models.CharField(max_length=5)
    peso = models.FloatField()
    pulso = models.FloatField()
    temperatura = models.FloatField()
    hemoglobina = models.FloatField()
    presion_sistolica = models.FloatField()
    presion_diastolica = models.FloatField()
    hematocrito = models.FloatField()

    respuestas_entrevista = models.JSONField(default=dict)
    respuestas_adicionales_entrevista = models.JSONField(default=dict)
    respuestas_medicas_adicionales = models.JSONField(default=dict)
    respuestas_mujeres = models.JSONField(null=True, blank=True)

    consentimiento_informado = models.BooleanField(default=False)
    nombre_entrevistador = models.CharField(max_length=100)
    firma_donador = models.TextField()
    firma_entrevistador = models.TextField()
    hora_inicio_flebotomia = models.TimeField()
    hora_finalizacion_flebotomia = models.TimeField()
    cantidad_sangre = models.PositiveIntegerField()
    reacciones_adversas = models.BooleanField()
    observaciones_flebotomia = models.TextField(blank=True)
    nombre_flebotomista = models.CharField(max_length=100)
    firma_flebotomista = models.TextField()
    
    fecha = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default="pendiente")
    pdf_entrevista = models.FileField(upload_to='entrevistas/', blank=True, null=True)
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='entrevistas')
    # Relaciones
    donante = models.ForeignKey("Donante", on_delete=models.CASCADE, related_name='entrevistas')    

    def __str__(self):
        return f"Entrevista {self.correlativo} - {self.primer_nombre} {self.primer_apellido}"

class UnidadMuestra(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVADO', 'Reservado'),
        ('VENCIDO', 'Vencido'),
        ('DESCARTADO', 'Descartado'),
        ('TRANSFORMADA', 'Transformada'),
    ]

    TIPO_UNIDAD_CHOICES = [
        ('PLASMA', 'Plasma'),
        ('PAQUETE_GLOBULAR', 'Paquete Globular'),
        ('PLAQUETAS', 'Plaquetas'),
        ('CRIO_PRECIPITADO', 'Crio Precipitado'),
    ]

    id = models.BigAutoField(primary_key=True)

    correlativo = models.CharField(max_length=30, unique=True, blank=True)
    donante = models.ForeignKey('Donante', on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    tipo_unidad = models.CharField(max_length=50, choices=TIPO_UNIDAD_CHOICES)
    tipo_sangre = models.CharField(max_length=5)
    volumen_ml = models.PositiveIntegerField()
    fecha_extraccion = models.DateField(default=timezone.now)
    fecha_donacion = models.DateField(null=True, blank=True)
    fecha_validacion = models.DateField(null=True, blank=True)
    fecha_caducidad = models.DateField()
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    responsable = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    localizacion = models.CharField(max_length=100, blank=True)
    condiciones_almacenamiento = models.CharField(max_length=200, blank=True)
    serologias = models.JSONField(default=dict, blank=True)
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.correlativo} - {self.tipo_unidad} ({self.tipo_sangre})"

    @property
    def dias_vigencia(self):
        delta = (self.fecha_caducidad - timezone.now().date()).days
        return delta

    def save(self, *args, **kwargs):
        if not self.lote:
            lote_codigo = f"LOTE-{self.fecha_extraccion.strftime('%Y%m%d')}"
            lote, created = Lote.objects.get_or_create(
                codigo=lote_codigo,
                defaults={
                    'descripcion': f'Lote creado automáticamente para fecha {self.fecha_extraccion}'
                }
            )
            self.lote = lote

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

