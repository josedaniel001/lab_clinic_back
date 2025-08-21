# banco_sangre/serializers.py

from rest_framework import serializers
from ordenes.serializers import OrdenSerializer
from ordenes.models import Orden
from .models import Donante, Entrevista, UnidadMuestra, Lote, SalidaUnidad, DetalleSalida

class DonanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donante
        fields = '__all__'
    
    def to_representation(self, instance):
        """Personalizar la representación para incluir información adicional"""
        data = super().to_representation(instance)
        
        # Agregar información sobre si puede crear muestras
        data['puede_crear_muestras'] = instance.apto_donacion and instance.tiene_entrevista_apro
        
        # Agregar información sobre si puede crear nueva orden
        data['puede_crear_nueva_orden'] = instance.puede_crear_nueva_orden()
        data['dias_restantes_para_nueva_orden'] = instance.dias_restantes_para_nueva_orden()
        
        # Agregar información del historial de códigos
        data['total_codigos_historial'] = len(instance.historial_codigos) if instance.historial_codigos else 0
        
        return data

class LoteSerializer(serializers.ModelSerializer):
    #unidades = UnidadMuestraSerializer(many=True, read_only=True)
    class Meta:
        model = Lote
        fields = '__all__'

class EntrevistaSerializer(serializers.ModelSerializer):
    donante = DonanteSerializer(read_only=True)
    donante_id = serializers.PrimaryKeyRelatedField(
        queryset=Donante.objects.all(), source='donante', write_only=True, required=False
    )
    cui = serializers.CharField(write_only=True, required=False)
    correlativo = serializers.CharField(required=False, allow_blank=True)
    orden = OrdenSerializer(read_only=True)
    orden_id = serializers.PrimaryKeyRelatedField(
        queryset=Orden.objects.all(), source='orden', write_only=True, required=False
    )
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Entrevista
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'pdf_entrevista']

    def get_pdf_url(self, obj):
        if obj.pdf_entrevista:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_entrevista.url)
        return None

    def validate(self, attrs):
        # Si se proporciona CUI, buscar el donante
        cui = attrs.get('cui')
        if cui and not attrs.get('donante'):
            try:
                donante = Donante.objects.get(cui=cui)
                attrs['donante'] = donante
            except Donante.DoesNotExist:
                raise serializers.ValidationError(f"No se encontró un donante con CUI: {cui}")
        
        # Si no se proporciona orden_id, crear una orden por defecto o usar la primera disponible
        if not attrs.get('orden'):
            orden = Orden.objects.first()
            if orden:
                attrs['orden'] = orden
            else:
                raise serializers.ValidationError("No hay órdenes disponibles en el sistema")
        
        # Validar que el donante pueda crear una nueva orden (6 meses después de la última donación)
        donante = attrs.get('donante')
        if donante and not donante.puede_crear_nueva_orden():
            dias_restantes = donante.dias_restantes_para_nueva_orden()
            raise serializers.ValidationError(
                f"El donante no puede crear una nueva orden hasta dentro de {dias_restantes} días. "
                f"Debe esperar 6 meses después de la última donación ({donante.fecha_ultima_donacion})."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Crear la entrevista y generar nuevo código para el donante"""
        donante = validated_data.get('donante')
        
        # Generar nuevo código para el donante si existe
        if donante:
            donante.generar_nuevo_codigo_para_orden()
        
        return super().create(validated_data)

class UnidadMuestraSerializer(serializers.ModelSerializer):
    dias_vigencia = serializers.IntegerField(read_only=True)
    correlativo = serializers.CharField(read_only=True)
    lote = LoteSerializer(read_only=True)
    lote_id = serializers.PrimaryKeyRelatedField(
    queryset=Lote.objects.all(),
    source='lote',
    write_only=True,
    required=False
    )
    donante = DonanteSerializer(read_only=True)
    donante_id = serializers.PrimaryKeyRelatedField(
    queryset=Donante.objects.all(),
    source='donante',
    write_only=True,
    required=False
    )
    etiqueta_url = serializers.SerializerMethodField()
    
    def get_etiqueta_url(self, obj):
        """Obtener la URL de la etiqueta PDF"""
        if obj.etiqueta_pdf:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.etiqueta_pdf.url)
        return None
    
    class Meta:
        model = UnidadMuestra
        fields = [
            'id',
            'correlativo',
            'donante',
            'donante_id',
            'tipo_unidad',
            'tipo_sangre',
            'volumen_ml',
            'fecha_extraccion',
            'fecha_donacion',
            'fecha_validacion',
            'fecha_caducidad',
            'lote',
            'lote_id',
            'responsable',
            'localizacion',
            'condiciones_almacenamiento',
            'serologias',
            'observaciones',
            'estado',
            'dias_vigencia',
            'etiqueta_pdf',
            'etiqueta_url',
            'creado',
        ]

    def validate(self, attrs):
        donante = attrs.get('donante')

        if donante:
            # Verificar que el donante esté apto para donación
            if not donante.apto_donacion:
                raise serializers.ValidationError(
                    f"El donante '{donante}' no está apto para donar. Debe aprobar la entrevista primero."
                )
            
            # Verificar que el donante tenga entrevista aprobada
            if not donante.tiene_entrevista_apro:
                raise serializers.ValidationError(
                    f"El donante '{donante}' no tiene entrevista aprobada. Debe completar y aprobar la entrevista primero."
                )

        return attrs

class ActualizarEstadoDonanteSerializer(serializers.Serializer):
    """
    Serializer para actualizar el estado del donante desde una entrevista
    """
    apto_donacion = serializers.BooleanField(
        help_text="Indica si el donante está apto para donación"
    )
    tiene_entrevista_apro = serializers.BooleanField(
        help_text="Indica si el donante tiene entrevista aprobada"
    )
    
    def validate(self, attrs):
        """
        Validación adicional si es necesaria
        """
        return attrs

class DetalleSalidaSerializer(serializers.ModelSerializer):
    """Serializer para el detalle de salida"""
    unidad = UnidadMuestraSerializer(read_only=True)
    unidad_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadMuestra.objects.filter(estado='DISPONIBLE'),
        source='unidad',
        write_only=True
    )
    
    # Información adicional de la unidad para mostrar en la salida
    unidad_correlativo = serializers.CharField(source='unidad.correlativo', read_only=True)
    unidad_tipo = serializers.CharField(source='unidad.tipo_unidad', read_only=True)
    unidad_tipo_sangre = serializers.CharField(source='unidad.tipo_sangre', read_only=True)
    unidad_volumen = serializers.IntegerField(source='unidad.volumen_ml', read_only=True)
    unidad_fecha_caducidad = serializers.DateField(source='unidad.fecha_caducidad', read_only=True)
    unidad_dias_vigencia = serializers.IntegerField(source='unidad.dias_vigencia', read_only=True)
    
    class Meta:
        model = DetalleSalida
        fields = [
            'id', 'unidad', 'unidad_id', 'fecha_inclusion',
            'unidad_correlativo', 'unidad_tipo', 'unidad_tipo_sangre',
            'unidad_volumen', 'unidad_fecha_caducidad', 'unidad_dias_vigencia'
        ]
        read_only_fields = ['fecha_inclusion']

class DetalleSalidaListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listar detalles de salida"""
    unidad_correlativo = serializers.CharField(source='unidad.correlativo', read_only=True)
    unidad_tipo = serializers.CharField(source='unidad.tipo_unidad', read_only=True)
    unidad_tipo_sangre = serializers.CharField(source='unidad.tipo_sangre', read_only=True)
    unidad_volumen = serializers.IntegerField(source='unidad.volumen_ml', read_only=True)
    unidad_fecha_caducidad = serializers.DateField(source='unidad.fecha_caducidad', read_only=True)
    unidad_dias_vigencia = serializers.IntegerField(source='unidad.dias_vigencia', read_only=True)
    
    class Meta:
        model = DetalleSalida
        fields = [
            'id', 'fecha_inclusion',
            'unidad_correlativo', 'unidad_tipo', 'unidad_tipo_sangre',
            'unidad_volumen', 'unidad_fecha_caducidad', 'unidad_dias_vigencia'
        ]
        read_only_fields = ['fecha_inclusion']

class SalidaUnidadSerializer(serializers.ModelSerializer):
    """Serializer para las salidas de unidades"""
    detalles = DetalleSalidaSerializer(many=True, read_only=True)
    unidades_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de unidades a incluir en la salida"
    )
    total_unidades = serializers.IntegerField(read_only=True)
    unidades_por_tipo = serializers.ListField(read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    # Información del técnico que realiza la salida
    tecnico_salida_nombre = serializers.SerializerMethodField()
    tecnico_salida_username = serializers.CharField(source='tecnico_salida.username', read_only=True)
    tecnico_salida_email = serializers.CharField(source='tecnico_salida.email', read_only=True)
    
    # Información del aprobador
    aprobado_por_nombre = serializers.SerializerMethodField()
    aprobado_por_username = serializers.CharField(source='aprobado_por.username', read_only=True)
    
    # Resumen de unidades por tipo
    resumen_unidades = serializers.SerializerMethodField()
    
    class Meta:
        model = SalidaUnidad
        fields = [
            'id', 'correlativo', 'receptor', 'cedula_receptor', 'medico_solicitante',
            'tecnico_salida', 'tecnico_salida_nombre', 'tecnico_salida_username', 'tecnico_salida_email',
            'fecha_salida', 'observaciones', 'estado', 'fecha_creacion', 'fecha_aprobacion', 
            'aprobado_por', 'aprobado_por_nombre', 'aprobado_por_username', 'pdf_salida',
            'firma_receptor', 'firma_tecnico', 'detalles', 'unidades_ids',
            'total_unidades', 'unidades_por_tipo', 'resumen_unidades', 'pdf_url'
        ]
        read_only_fields = [
            'correlativo', 'fecha_salida', 'fecha_creacion', 'fecha_aprobacion',
            'pdf_salida', 'total_unidades', 'unidades_por_tipo', 'resumen_unidades'
        ]
    
    def get_tecnico_salida_nombre(self, obj):
        """Obtener nombre del técnico de salida"""
        if obj.tecnico_salida:
            # Intentar obtener nombre completo
            nombre_completo = obj.tecnico_salida.get_full_name()
            if nombre_completo:
                return nombre_completo
            # Si no hay nombre completo, usar username
            return obj.tecnico_salida.username
        return None
    
    def get_aprobado_por_nombre(self, obj):
        """Obtener nombre del aprobador"""
        if obj.aprobado_por:
            # Intentar obtener nombre completo
            nombre_completo = obj.aprobado_por.get_full_name()
            if nombre_completo:
                return nombre_completo
            # Si no hay nombre completo, usar username
            return obj.aprobado_por.username
        return None
    
    def get_resumen_unidades(self, obj):
        """Obtener resumen de unidades por tipo"""
        from django.db.models import Count
        resumen = obj.detalles.values('unidad__tipo_unidad').annotate(
            cantidad=Count('id'),
            volumen_total=Count('id')  # Aquí podrías sumar volúmenes si es necesario
        ).values('unidad__tipo_unidad', 'cantidad', 'volumen_total')
        
        return list(resumen)
    
    def get_pdf_url(self, obj):
        if obj.pdf_salida:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_salida.url)
        return None
    
    def validate(self, attrs):
        """Validar que las unidades estén disponibles"""
        unidades_ids = attrs.get('unidades_ids', [])
        
        if not unidades_ids:
            raise serializers.ValidationError("Debe seleccionar al menos una unidad")
        
        # Verificar que todas las unidades estén disponibles
        unidades_disponibles = UnidadMuestra.objects.filter(
            id__in=unidades_ids,
            estado='DISPONIBLE'
        )
        
        if len(unidades_disponibles) != len(unidades_ids):
            raise serializers.ValidationError(
                "Algunas unidades no están disponibles o ya fueron entregadas"
            )
        
        return attrs
    
    def create(self, validated_data):
        """Crear la salida y sus detalles"""
        unidades_ids = validated_data.pop('unidades_ids', [])
        
        # Crear la salida (el técnico ya debe estar asignado desde el ViewSet)
        salida = SalidaUnidad.objects.create(**validated_data)
        
        # Crear los detalles
        for unidad_id in unidades_ids:
            DetalleSalida.objects.create(
                salida=salida,
                unidad_id=unidad_id
            )
        
        return salida

class SalidaUnidadListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar salidas"""
    total_unidades = serializers.IntegerField(read_only=True)
    tecnico_salida_nombre = serializers.SerializerMethodField()
    detalles = DetalleSalidaListSerializer(many=True, read_only=True)
    resumen_unidades = serializers.SerializerMethodField()
    
    class Meta:
        model = SalidaUnidad
        fields = [
            'id', 'correlativo', 'receptor', 'medico_solicitante',
            'fecha_salida', 'estado', 'total_unidades', 'tecnico_salida_nombre',
            'detalles', 'resumen_unidades'
        ]
    
    def get_tecnico_salida_nombre(self, obj):
        """Obtener nombre del técnico de salida"""
        if obj.tecnico_salida:
            # Intentar obtener nombre completo
            nombre_completo = obj.tecnico_salida.get_full_name()
            if nombre_completo:
                return nombre_completo
            # Si no hay nombre completo, usar username
            return obj.tecnico_salida.username
        return None
    
    def get_resumen_unidades(self, obj):
        """Obtener resumen de unidades por tipo"""
        from django.db.models import Count
        resumen = obj.detalles.values('unidad__tipo_unidad').annotate(
            cantidad=Count('id'),
            volumen_total=Count('id')  # Aquí podrías sumar volúmenes si es necesario
        ).values('unidad__tipo_unidad', 'cantidad', 'volumen_total')
        
        return list(resumen)