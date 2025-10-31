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
    denegado_permanente = models.BooleanField(
        default=False,
        help_text="Indica si el donante tiene denegación permanente y nunca podrá donar"
    )
    fecha_denegacion_permanente = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se marcó como denegado permanente"
    )
    motivo_denegacion_permanente = models.TextField(
        blank=True,
        null=True,
        help_text="Motivo de la denegación permanente"
    )
    
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

class CatalogoDescarte(models.Model):
    """
    Catálogo de opciones para descarte de muestras.
    """
    codigo = models.CharField(max_length=10, unique=True, help_text="Código único del motivo de descarte")
    nombre = models.CharField(max_length=100, help_text="Nombre del motivo de descarte")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada del motivo")
    activo = models.BooleanField(default=True, help_text="Indica si esta opción está disponible")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['codigo']
        verbose_name = "Catálogo de Descarte"
        verbose_name_plural = "Catálogos de Descarte"
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class DescarteMuestra(models.Model):
    """
    Registro de descarte de muestras con motivo y validación.
    """
    muestra = models.OneToOneField('UnidadMuestra', on_delete=models.CASCADE, related_name='descarte')
    motivo = models.ForeignKey(CatalogoDescarte, on_delete=models.PROTECT, help_text="Motivo del descarte")
    observaciones = models.TextField(blank=True, help_text="Observaciones adicionales del descarte")
    fecha_descarte = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que realizó el descarte")
    validado = models.BooleanField(default=False, help_text="Indica si el descarte ha sido validado")
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    validador = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='descartes_validados', help_text="Usuario que validó el descarte")
    
    class Meta:
        ordering = ['-fecha_descarte']
        verbose_name = "Descarte de Muestra"
        verbose_name_plural = "Descartes de Muestras"
    
    def __str__(self):
        return f"Descarte {self.muestra.correlativo} - {self.motivo.nombre}"
    
    def save(self, *args, **kwargs):
        if self.validado and not self.fecha_validacion:
            from django.utils import timezone
            self.fecha_validacion = timezone.now()
        super().save(*args, **kwargs)

class CodigoDonante(models.Model):
    """
    Modelo para rastrear todos los códigos que ha tenido un donante.
    Cada vez que se crea una nueva orden de exámenes, se genera un nuevo código.
    """
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del donante para una orden específica")
    donante = models.ForeignKey('Donante', on_delete=models.CASCADE, related_name='codigos_donante')
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='codigos_donante')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True, help_text="Indica si este código está activo para la orden")
    
    class Meta:
        ordering = ['-fecha_creacion']
        unique_together = ['donante', 'orden']  # Un donante solo puede tener un código por orden
    
    def __str__(self):
        return f"{self.codigo} - {self.donante} (Orden: {self.orden.codigo})"
    
    @classmethod
    def generar_nuevo_codigo(cls, donante, orden):
        """
        Genera un nuevo código único para un donante en una orden específica.
        Formato: DON-{DONANTE_ID}-{ORDEN_ID}
        Ejemplo: DON-001-0272
        """
        from django.db import transaction
        import threading
        
        # Usar un lock para evitar duplicados en registros simultáneos
        lock = threading.Lock()
        
        with lock:
            with transaction.atomic():
                # Formato simplificado: DON-{DONANTE_ID}-{ORDEN_ID}
                # Ejemplo: DON-001-0272
                donante_id = str(donante.id).zfill(3)
                orden_id = str(orden.id).zfill(4)  # 4 dígitos para la orden
                
                # Buscar si ya existe un código para este donante en esta orden
                ultimo_codigo = cls.objects.filter(
                    donante=donante,
                    orden=orden
                ).order_by('-fecha_creacion').first()
                
                if ultimo_codigo:
                    # Si ya existe un código para este donante en esta orden, reutilizarlo
                    print(f"ℹ️ Reutilizando código existente: {ultimo_codigo.codigo}")
                    return ultimo_codigo
                
                # Crear el nuevo código (simplificado, sin correlativo adicional)
                nuevo_codigo = f'DON-{donante_id}-{orden_id}'
                
                print(f"✅ Generando nuevo código: {nuevo_codigo}")
                
                # Verificar que no exista (por seguridad)
                if cls.objects.filter(codigo=nuevo_codigo).exists():
                    # Si por alguna razón existe, agregar un sufijo
                    contador = 1
                    while cls.objects.filter(codigo=f'{nuevo_codigo}-{contador}').exists():
                        contador += 1
                    nuevo_codigo = f'{nuevo_codigo}-{contador}'
                    print(f"⚠️ Código duplicado, usando: {nuevo_codigo}")
                
                # Crear el nuevo código de donante
                codigo_donante = cls.objects.create(
                    codigo=nuevo_codigo,
                    donante=donante,
                    orden=orden
                )
                
                return codigo_donante
 
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
        ('EN_DESCARTE', 'En Proceso de Descarte'),
    ]

    TIPO_UNIDAD_CHOICES = [
        ('PLASMA', 'Plasma'),
        ('PAQUETE_GLOBULAR', 'Paquete Globular'),
        ('PLAQUETAS', 'Plaquetas'),
        ('CRIO_PRECIPITADO', 'Crio Precipitado'),
    ]

    # Constantes para tiempos de vida de cada tipo de unidad (en días)
    TIEMPO_VIDA_UNIDAD = {
        'PLASMA': 365,  # Plasma: 1 año
        'PAQUETE_GLOBULAR': 42,  # Paquete Globular: 42 días
        'PLAQUETAS': 5,  # Plaquetas: 5 días
        'CRIO_PRECIPITADO': 365,  # Crio Precipitado: 1 año
    }

    id = models.BigAutoField(primary_key=True)

    correlativo = models.CharField(max_length=50, unique=True, blank=True)  # Aumentado para soportar formato padre/hijo
    donante = models.ForeignKey('Donante', on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades')
    codigo_donante = models.ForeignKey('CodigoDonante', on_delete=models.SET_NULL, null=True, blank=True, related_name='unidades_muestra', help_text="Código del donante asociado a esta muestra")
    
    # Campos para relación padre-hijo en transformaciones
    muestra_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='muestras_hijas', help_text="Muestra original de la cual se transformó esta muestra")
    es_transformacion = models.BooleanField(default=False, help_text="Indica si esta muestra es resultado de una transformación")
    
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
    
    @property
    def codigo_donante_muestra(self):
        """Retorna el código del donante para esta muestra"""
        return self.codigo_donante.codigo if self.codigo_donante else None
    
    @property
    def esta_descartada(self):
        """Indica si la muestra está descartada"""
        return self.estado == 'DESCARTADO' or hasattr(self, 'descarte')
    
    @property
    def motivo_descarte(self):
        """Retorna el motivo del descarte si existe"""
        if hasattr(self, 'descarte'):
            return self.descarte.motivo.nombre
        return None
    
    @property
    def correlativo_padre(self):
        """Retorna el correlativo de la muestra padre si es una transformación"""
        if self.es_transformacion and self.muestra_padre:
            return self.muestra_padre.correlativo
        return None
    
    @property
    def es_muestra_original(self):
        """Indica si esta muestra es original (no es transformación)"""
        return not self.es_transformacion
    
    @property
    def tiene_transformaciones(self):
        """Indica si esta muestra tiene transformaciones"""
        return self.muestras_hijas.exists()
    
    def descartar(self, motivo_id, observaciones='', responsable=None):
        """
        Descarta la muestra con el motivo especificado.
        """
        from django.utils import timezone
        
        if self.estado == 'DESCARTADO':
            raise ValueError("La muestra ya está descartada")
        
        if self.estado not in ['DISPONIBLE', 'RESERVADO']:
            raise ValueError(f"No se puede descartar una muestra en estado {self.estado}")
        
        try:
            motivo = CatalogoDescarte.objects.get(id=motivo_id, activo=True)
        except CatalogoDescarte.DoesNotExist:
            raise ValueError("El motivo de descarte no es válido")
        
        # Crear el registro de descarte
        descarte = DescarteMuestra.objects.create(
            muestra=self,
            motivo=motivo,
            observaciones=observaciones,
            responsable=responsable
        )
        
        # Actualizar el estado de la muestra
        self.estado = 'DESCARTADO'
        self.save(update_fields=['estado'])
        
        return descarte
    
    def validar_descarte(self, validador):
        """
        Valida el descarte de la muestra.
        """
        if not hasattr(self, 'descarte'):
            raise ValueError("La muestra no tiene un descarte registrado")
        
        if self.descarte.validado:
            raise ValueError("El descarte ya está validado")
        
        self.descarte.validado = True
        self.descarte.validador = validador
        self.descarte.save()
        
        return self.descarte
    
    def calcular_fecha_caducidad_transformacion(self, tipo_unidad):
        """
        Calcula la fecha de caducidad para una unidad transformada según su tipo.
        La fecha se calcula desde la fecha de extracción original más el tiempo de vida del nuevo tipo.
        
        Args:
            tipo_unidad (str): Tipo de unidad transformada
            
        Returns:
            datetime.date: Fecha de caducidad calculada
        """
        tiempo_vida = self.TIEMPO_VIDA_UNIDAD.get(tipo_unidad, 42)  # Default 42 días si no se encuentra
        return self.fecha_extraccion + timedelta(days=tiempo_vida)
    
    def transformar(self, nuevo_tipo_unidad, volumen_ml, responsable=None, observaciones='', marcar_como_transformada=True):
        """
        Transforma la muestra creando una nueva muestra hija con el formato de correlativo solicitado.
        Formato: <Correlativo_padre>/0001<ascendente>
        
        Args:
            nuevo_tipo_unidad (str): Tipo de unidad de la muestra transformada
            volumen_ml (int): Volumen en ml de la muestra transformada
            responsable (User, optional): Usuario responsable de la transformación
            observaciones (str, optional): Observaciones adicionales
            marcar_como_transformada (bool): Si es True, marca la muestra padre como TRANSFORMADA.
                                            Útil para transformaciones múltiples donde se marca al final.
            
        Returns:
            UnidadMuestra: La nueva muestra transformada
        """
        from django.db import transaction
        
        if self.estado not in ['DISPONIBLE', 'RESERVADO', 'TRANSFORMADA']:
            raise ValueError(f"No se puede transformar una muestra en estado {self.estado}")
        
        if self.es_transformacion:
            raise ValueError("No se puede transformar una muestra que ya es resultado de una transformación")
        
        with transaction.atomic():
            # Generar correlativo con formato <Correlativo_padre>/0001<ascendente>
            correlativo_hijo = self._generar_correlativo_transformacion()
            
            # Calcular fecha de caducidad según el tipo de unidad transformada
            fecha_caducidad = self.calcular_fecha_caducidad_transformacion(nuevo_tipo_unidad)
            
            # Crear la muestra transformada
            muestra_transformada = UnidadMuestra.objects.create(
                correlativo=correlativo_hijo,
                muestra_padre=self,
                es_transformacion=True,
                donante=self.donante,
                codigo_donante=self.codigo_donante,
                tipo_unidad=nuevo_tipo_unidad,
                tipo_sangre=self.tipo_sangre,
                volumen_ml=volumen_ml,
                fecha_extraccion=self.fecha_extraccion,
                fecha_donacion=self.fecha_donacion,
                fecha_validacion=self.fecha_validacion,
                fecha_caducidad=fecha_caducidad,
                lote=self.lote,
                responsable=responsable,
                localizacion=self.localizacion,
                condiciones_almacenamiento=self.condiciones_almacenamiento,
                serologias=self.serologias.copy() if self.serologias else {},
                observaciones=f"Transformación de {self.correlativo}. {observaciones}".strip(),
                estado='DISPONIBLE'
            )
            
            # Marcar la muestra padre como transformada si se solicita
            if marcar_como_transformada and self.estado != 'TRANSFORMADA':
                self.estado = 'TRANSFORMADA'
                self.save(update_fields=['estado'])
            
            return muestra_transformada
    
    def _generar_correlativo_transformacion(self):
        """
        Genera el correlativo para una muestra transformada con formato:
        <Correlativo_padre>/0001<ascendente>
        
        Ejemplos:
        - PLM-0001/0001
        - PLM-0001/0002
        - PGB-0025/0001
        """
        correlativo_padre = self.correlativo
        
        # Buscar el último número de transformación para esta muestra padre
        ultima_transformacion = UnidadMuestra.objects.filter(
            muestra_padre=self,
            es_transformacion=True
        ).order_by('-correlativo').first()
        
        if ultima_transformacion:
            # Extraer el número del último correlativo hijo
            try:
                # Formato: CORRELATIVO_PADRE/0001
                ultimo_numero_str = ultima_transformacion.correlativo.split('/')[-1]
                ultimo_numero = int(ultimo_numero_str)
                nuevo_numero = ultimo_numero + 1
            except (ValueError, IndexError):
                nuevo_numero = 1
        else:
            nuevo_numero = 1
        
        # Formatear con 4 dígitos
        nuevo_correlativo = f"{correlativo_padre}/{nuevo_numero:04d}"
        
        # Verificar que no exista (doble verificación)
        if UnidadMuestra.objects.filter(correlativo=nuevo_correlativo).exists():
            # Si existe, incrementar hasta encontrar uno disponible
            contador = nuevo_numero + 1
            while UnidadMuestra.objects.filter(correlativo=f"{correlativo_padre}/{contador:04d}").exists():
                contador += 1
            nuevo_correlativo = f"{correlativo_padre}/{contador:04d}"
        
        return nuevo_correlativo
    
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
        
        # Si no tiene correlativo y se está creando, generar uno antes de guardar
        # IMPORTANTE: No generar si es una transformación (ya tiene correlativo)
        if creating and not self.correlativo and not self.es_transformacion:
            # Generar un correlativo temporal ÚNICO usando timestamp
            import time
            self.correlativo = f'TEMP-{int(time.time() * 1000000)}-{id(self)}'
        
        super().save(*args, **kwargs)

        if creating:
            # Asignar automáticamente el código de donante si no se proporcionó
            if not self.codigo_donante and self.donante:
                self._asignar_codigo_donante_automatico()
            
            # Generar correlativo de unidad solo si es temporal
            if self.correlativo.startswith('TEMP-'):
                prefix = {
                    'PLASMA': 'PLM',
                    'PAQUETE_GLOBULAR': 'PGB',
                    'PLAQUETAS': 'PLQ',
                    'CRIO_PRECIPITADO': 'CRP',
                }.get(self.tipo_unidad, 'UNK')

                # Si tiene código de donante, usar su estructura numérica con contador
                if self.codigo_donante:
                    # Código donante formato: DON-001-0272
                    # Extraer partes: DON, 001 (donante_id), 0272 (orden_id)
                    try:
                        partes = self.codigo_donante.codigo.split('-')
                        if len(partes) >= 3:
                            donante_id = partes[1]  # "001"
                            orden_id = partes[2].lstrip('0') or '0'  # "0272" -> "272" (sin ceros iniciales)
                            
                            # Formato: {PREFIX}-{DONANTE_ID}-{ORDEN_ID}-{CONTADOR}
                            # Ejemplo: PGB-001-272-001
                            base_correlativo = f"{prefix}-{donante_id}-{orden_id}"
                            
                            # Buscar el último contador para este base
                            # Buscar todas las muestras con este patrón
                            patron_busqueda = f"{base_correlativo}-"
                            ultimas_muestras = UnidadMuestra.objects.filter(
                                correlativo__startswith=patron_busqueda,
                                tipo_unidad=self.tipo_unidad,
                                codigo_donante=self.codigo_donante
                            ).exclude(pk=self.pk).order_by('-correlativo')
                            
                            contador = 1
                            if ultimas_muestras.exists():
                                # Extraer el último número de contador
                                ultimo_correlativo = ultimas_muestras.first().correlativo
                                try:
                                    ultimo_contador = int(ultimo_correlativo.split('-')[-1])
                                    contador = ultimo_contador + 1
                                except (ValueError, IndexError):
                                    contador = ultimas_muestras.count() + 1
                            
                            # Formato final: PGB-001-272-001
                            self.correlativo = f"{base_correlativo}-{contador:03d}"
                            print(f"✅ Correlativo con código donante: {self.correlativo}")
                        else:
                            # Fallback al método anterior
                            self.correlativo = f"{prefix}-{self.pk:04d}"
                    except Exception as e:
                        print(f"⚠️ Error usando código donante para correlativo: {e}")
                        # Fallback al método anterior
                        self.correlativo = f"{prefix}-{self.pk:04d}"
                else:
                    # Si no hay código de donante, usar el ID como antes
                    self.correlativo = f"{prefix}-{self.pk:04d}"
                    print(f"ℹ️ Correlativo sin código donante: {self.correlativo}")
                
                UnidadMuestra.objects.filter(pk=self.pk).update(correlativo=self.correlativo)
    
    def _asignar_codigo_donante_automatico(self):
        """
        Asigna automáticamente el código de donante más reciente para este donante.
        Retorna el código de donante encontrado.
        """
        try:
            # Buscar el código de donante más reciente para este donante
            codigo_donante = CodigoDonante.objects.filter(
                donante=self.donante,
                activo=True
            ).order_by('-fecha_creacion').first()
            
            if codigo_donante:
                self.codigo_donante = codigo_donante
                UnidadMuestra.objects.filter(pk=self.pk).update(codigo_donante=codigo_donante)
                print(f"✅ Código de donante asignado: {codigo_donante.codigo}")
                return codigo_donante
            return None
        except Exception as e:
            print(f"⚠️ Error asignando código de donante automático: {e}")
            return None


    class Meta:
        ordering = ['-fecha_extraccion']


class SalidaUnidad(models.Model):
    """
    Modelo para registrar las salidas de unidades de muestra del banco de sangre
    """
    correlativo = models.CharField(max_length=50, unique=True, blank=True, help_text="Correlativo único de la salida")
    receptor = models.CharField(
        max_length=200,
        help_text="Nombre completo de quien recibe las unidades"
    )
    identificador_receptor = models.CharField(
        max_length=20,
        blank=True,
        help_text="Identificador del receptor (DPI, pasaporte, etc.)"
    )
    medico_solicitante = models.CharField(
        max_length=200,
        help_text="Nombre del médico que solicita"
    )
    fecha_salida = models.DateTimeField(
        help_text="Fecha y hora de la salida"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Observaciones adicionales"
    )
    tecnico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salidas_registradas',
        help_text="Técnico que registra la salida"
    )
    tecnico_nombre = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nombre del técnico"
    )
    cantidad_unidades = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad total de unidades en la salida"
    )
    pdf_salida = models.FileField(
        upload_to='salidas/',
        blank=True,
        null=True,
        help_text="PDF de la salida"
    )
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_salida']
        verbose_name = 'Salida de Unidad'
        verbose_name_plural = 'Salidas de Unidades'
    
    def __str__(self):
        return f"Salida {self.correlativo} - {self.fecha_salida.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Generar correlativo si no existe"""
        if not self.correlativo:
            # Generar correlativo: SAL-YYYYMMDD-0001
            from django.db import transaction
            with transaction.atomic():
                fecha_str = self.fecha_salida.strftime('%Y%m%d')
                base = f'SAL-{fecha_str}'
                
                # Buscar el último correlativo del día
                ultimas = SalidaUnidad.objects.filter(
                    correlativo__startswith=base
                ).order_by('-correlativo')
                
                if ultimas.exists():
                    ultimo = ultimas.first().correlativo
                    try:
                        numero = int(ultimo.split('-')[-1]) + 1
                    except:
                        numero = 1
                else:
                    numero = 1
                
                self.correlativo = f'{base}-{numero:04d}'
        
        super().save(*args, **kwargs)


class DetalleaSalidaUnidad(models.Model):
    """
    Detalle de cada unidad en una salida
    """
    salida = models.ForeignKey(
        SalidaUnidad,
        on_delete=models.CASCADE,
        related_name='detalles',
        help_text="Salida a la que pertenece"
    )
    unidad_muestra = models.ForeignKey(
        UnidadMuestra,
        on_delete=models.CASCADE,
        related_name='detalles_salida',
        help_text="Unidad de muestra"
    )
    
    class Meta:
        verbose_name = 'Detalle de Salida'
        verbose_name_plural = 'Detalles de Salida'
        unique_together = ['salida', 'unidad_muestra']
    
    def __str__(self):
        return f"{self.salida.correlativo} - {self.unidad_muestra.correlativo}"