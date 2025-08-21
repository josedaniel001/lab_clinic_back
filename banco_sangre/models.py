# banco_sangre/models.py

from django.db import models
from django.contrib.auth import get_user_model
from ordenes.models import Orden
from localizacion.models import Municipio
from django.utils import timezone
from datetime import timedelta

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
    apto_donacion = models.BooleanField(default=False)
    tiene_entrevista_apro = models.BooleanField(default=False)
    codigo_donante = models.CharField(max_length=20, unique=True, blank=True, null=True)
    historial_codigos = models.JSONField(default=list, blank=True, help_text="Historial de códigos del donante")
    fecha_ultima_donacion = models.DateField(null=True, blank=True, help_text="Fecha de la última donación")
    
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido} ({self.cui})"
    
    def save(self, *args, **kwargs):
        # Generar código único si no existe
        if not self.codigo_donante:
            self.generar_codigo_donante()
        super().save(*args, **kwargs)
    
    def generar_codigo_donante(self):
        """Genera un código único numérico para el donante"""
        import random
        
        # Generar un número aleatorio de 6 dígitos
        while True:
            numero_aleatorio = random.randint(100000, 999999)
            codigo = str(numero_aleatorio)
            
            # Verificar que el código no exista
            if not Donante.objects.filter(codigo_donante=codigo).exists():
                self.codigo_donante = codigo
                break
    
    def generar_nuevo_codigo_para_orden(self):
        """Genera un nuevo código para una nueva orden de resultados"""
        # Guardar el código actual en el historial si existe
        if self.codigo_donante:
            if not self.historial_codigos:
                self.historial_codigos = []
            
            # Agregar el código actual al historial con fecha
            self.historial_codigos.append({
                'codigo': self.codigo_donante,
                'fecha_generacion': timezone.now().isoformat(),
                'fecha_ultimo_uso': timezone.now().isoformat()
            })
        
        # Generar nuevo código
        self.generar_codigo_donante()
        self.save()
        
        return self.codigo_donante
    
    def puede_crear_nueva_orden(self):
        """Verifica si puede crear una nueva orden (6 meses después de la última donación)"""
        if not self.fecha_ultima_donacion:
            return True
        
        fecha_limite = self.fecha_ultima_donacion + timedelta(days=180)  # 6 meses
        return timezone.now().date() >= fecha_limite
    
    def dias_restantes_para_nueva_orden(self):
        """Calcula los días restantes para poder crear una nueva orden"""
        if not self.fecha_ultima_donacion:
            return 0
        
        fecha_limite = self.fecha_ultima_donacion + timedelta(days=180)
        dias_restantes = (fecha_limite - timezone.now().date()).days
        return max(0, dias_restantes)
    
    def actualizar_fecha_ultima_donacion(self, fecha_donacion=None):
        """Actualiza la fecha de la última donación"""
        if fecha_donacion is None:
            fecha_donacion = timezone.now().date()
        
        self.fecha_ultima_donacion = fecha_donacion
        self.save()
    
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
        ('ENTREGADA', 'Entregada'),  # Nuevo estado para unidades entregadas
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
    etiqueta_pdf = models.FileField(upload_to='etiquetas/', blank=True, null=True, help_text="PDF de la etiqueta generada automáticamente")
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.correlativo} - {self.tipo_unidad} ({self.tipo_sangre})"

    @property
    def dias_vigencia(self):
        delta = (self.fecha_caducidad - timezone.now().date()).days
        return delta
    
    def generar_etiqueta_automatica(self):
        """Genera la etiqueta PDF automáticamente al crear la unidad"""
        try:
            from django.template.loader import render_to_string
            from django.conf import settings
            import os
            from sistema.models import ConfiguracionLaboratorio
            
            # Importar configuración segura de WeasyPrint
            try:
                from weasyprint import HTML
                WEASYPRINT_AVAILABLE = True
            except ImportError:
                WEASYPRINT_AVAILABLE = False
                print("⚠️ WeasyPrint no disponible, no se generará etiqueta automática")
                return
            
            # Solo generar si no existe ya
            if self.etiqueta_pdf:
                return
            
            # Obtener configuración del laboratorio
            config = ConfiguracionLaboratorio.objects.first()
            
            # Preparar serologías por defecto si no existen
            serologias = self.serologias or {
                "Syphilis": "No Reactivo",
                "HIV Ab/Ag": "No Reactivo", 
                "Chagas": "No Reactivo",
                "Anti-HBc": "No Reactivo",
                "HBsAg": "No Reactivo",
                "Anti-HCV": "No Reactivo"
            }
            
            # Usar el código del donante en lugar del ID para el código de barras
            codigo_etiqueta = self.correlativo
            if self.donante and self.donante.codigo_donante:
                codigo_etiqueta = self.donante.codigo_donante
            
            # Generar HTML de la etiqueta
            html_string = render_to_string(
                'banco_sangre/etiqueta_uni.html',
                {
                    'unidad': self,
                    'config': config,
                    'serologias': serologias,
                    'codigo_etiqueta': codigo_etiqueta
                }
            )
            
            # Crear directorio si no existe
            output_dir = os.path.join(settings.MEDIA_ROOT, 'etiquetas')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generar nombre de archivo único
            pdf_filename = f'etiqueta_unidad_{self.pk}.pdf'
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            # Generar PDF
            HTML(string=html_string, base_url=None).write_pdf(pdf_path)
            
            # Guardar la ruta del PDF en la unidad
            self.etiqueta_pdf = f'etiquetas/{pdf_filename}'
            UnidadMuestra.objects.filter(pk=self.pk).update(etiqueta_pdf=self.etiqueta_pdf)
            
            print(f"✅ Etiqueta generada automáticamente para unidad {self.correlativo}")
            
        except Exception as e:
            print(f"❌ Error generando etiqueta automática para unidad {self.pk}: {str(e)}")
            # No fallar la creación de la unidad si falla la generación de etiqueta

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
            
            # Actualizar fecha de última donación del donante
            if self.donante:
                self.donante.actualizar_fecha_ultima_donacion(self.fecha_extraccion)
            
            # Generar etiqueta automáticamente después de crear la unidad
            self.generar_etiqueta_automatica()

    class Meta:
        ordering = ['-fecha_extraccion']

class SalidaUnidad(models.Model):
    """Modelo para registrar las salidas de unidades de muestra"""
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('COMPLETADA', 'Completada'),
    ]
    
    # Campos del formulario que mostraste
    receptor = models.CharField(max_length=200, help_text="Nombre del receptor")
    cedula_receptor = models.CharField(max_length=20, help_text="Cédula del receptor")
    medico_solicitante = models.CharField(max_length=200, help_text="Nombre del médico solicitante")
    tecnico_salida = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='salidas_realizadas')
    fecha_salida = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    # Campos adicionales del backend
    correlativo = models.CharField(max_length=50, unique=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='salidas_aprobadas')
    pdf_salida = models.FileField(upload_to='salidas/', blank=True, null=True)
    
    # Campos para firma
    firma_receptor = models.TextField(blank=True)
    firma_tecnico = models.TextField(blank=True)
    
    def __str__(self):
        return f"Salida {self.correlativo} - {self.receptor}"
    
    def save(self, *args, **kwargs):
        if not self.correlativo:
            # Generar correlativo automático
            fecha_actual = timezone.now()
            self.correlativo = f"SAL-{fecha_actual.strftime('%Y%m%d')}-{SalidaUnidad.objects.filter(fecha_creacion__date=fecha_actual.date()).count() + 1:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def total_unidades(self):
        """Total de unidades en esta salida"""
        return self.detalles.count()
    
    @property
    def unidades_por_tipo(self):
        """Agrupar unidades por tipo"""
        from django.db.models import Count
        return self.detalles.values('unidad__tipo_unidad').annotate(
            cantidad=Count('id')
        )

class DetalleSalida(models.Model):
    """Detalle de las unidades incluidas en una salida"""
    
    salida = models.ForeignKey(SalidaUnidad, on_delete=models.CASCADE, related_name='detalles')
    unidad = models.ForeignKey(UnidadMuestra, on_delete=models.CASCADE, related_name='salidas')
    fecha_inclusion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.salida.correlativo} - {self.unidad.correlativo}"
    
    def save(self, *args, **kwargs):
        # Cambiar el estado de la unidad a ENTREGADA
        if self.unidad.estado == 'DISPONIBLE':
            self.unidad.estado = 'ENTREGADA'
            self.unidad.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['salida', 'unidad']

