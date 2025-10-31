# banco_sangre/serializers.py

from rest_framework import serializers
from ordenes.serializers import OrdenSerializer
from ordenes.models import Orden
from .models import Donante, Entrevista, UnidadMuestra, Lote, CodigoDonante, CatalogoDescarte, DescarteMuestra, SalidaUnidad, DetalleaSalidaUnidad

class DonanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donante
        fields = '__all__'
        read_only_fields = ['denegado_permanente', 'fecha_denegacion_permanente', 'motivo_denegacion_permanente']

class LoteSerializer(serializers.ModelSerializer):
    #unidades = UnidadMuestraSerializer(many=True, read_only=True)
    class Meta:
        model = Lote
        fields = '__all__'

class CatalogoDescarteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogoDescarte
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'activo',
            'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']

class DescarteMuestraSerializer(serializers.ModelSerializer):
    motivo = CatalogoDescarteSerializer(read_only=True)
    motivo_id = serializers.PrimaryKeyRelatedField(
        queryset=CatalogoDescarte.objects.filter(activo=True),
        source='motivo',
        write_only=True
    )
    responsable_nombre = serializers.CharField(source='responsable.get_full_name', read_only=True)
    validador_nombre = serializers.CharField(source='validador.get_full_name', read_only=True)
    muestra_correlativo = serializers.CharField(source='muestra.correlativo', read_only=True)
    
    class Meta:
        model = DescarteMuestra
        fields = [
            'id',
            'muestra',
            'muestra_correlativo',
            'motivo',
            'motivo_id',
            'observaciones',
            'fecha_descarte',
            'responsable',
            'responsable_nombre',
            'validado',
            'fecha_validacion',
            'validador',
            'validador_nombre'
        ]
        read_only_fields = ['fecha_descarte', 'fecha_validacion']

class CodigoDonanteSerializer(serializers.ModelSerializer):
    donante = DonanteSerializer(read_only=True)
    orden = OrdenSerializer(read_only=True)
    codigo = serializers.CharField(read_only=True)
    
    class Meta:
        model = CodigoDonante
        fields = [
            'id',
            'codigo',
            'donante',
            'orden',
            'fecha_creacion',
            'activo'
        ]
        read_only_fields = ['codigo', 'fecha_creacion']

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
        
        return attrs

class UnidadMuestraSerializer(serializers.ModelSerializer):
    dias_vigencia = serializers.IntegerField(read_only=True)
    correlativo = serializers.CharField(read_only=True)
    codigo_donante_muestra = serializers.CharField(read_only=True)
    esta_descartada = serializers.BooleanField(read_only=True)
    motivo_descarte = serializers.CharField(read_only=True)
    correlativo_padre = serializers.CharField(read_only=True)
    es_muestra_original = serializers.BooleanField(read_only=True)
    tiene_transformaciones = serializers.BooleanField(read_only=True)
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
    codigo_donante = CodigoDonanteSerializer(read_only=True)
    codigo_donante_id = serializers.PrimaryKeyRelatedField(
        queryset=CodigoDonante.objects.all(),
        source='codigo_donante',
        write_only=True,
        required=False
    )
    descarte = DescarteMuestraSerializer(read_only=True)
    # Campos para relación padre-hijo
    muestra_padre = serializers.PrimaryKeyRelatedField(
        queryset=UnidadMuestra.objects.all(),
        write_only=True,
        required=False,
        help_text="ID de la muestra padre (solo para transformaciones)"
    )
    es_transformacion = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UnidadMuestra
        fields = [
            'id',
            'correlativo',
            'codigo_donante_muestra',
            'donante',
            'donante_id',
            'codigo_donante',
            'codigo_donante_id',
            'muestra_padre',
            'es_transformacion',
            'correlativo_padre',
            'es_muestra_original',
            'tiene_transformaciones',
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
            'creado',
            'esta_descartada',
            'motivo_descarte',
            'descarte',
        ]

    def validate(self, attrs):
        donante = attrs.get('donante')
        codigo_donante = attrs.get('codigo_donante')

        # Validar que el donante NO esté denegado permanentemente
        if donante and donante.denegado_permanente:
            raise serializers.ValidationError({
                'donante': f"🔴 El donante '{donante}' tiene una DENEGACIÓN PERMANENTE y no puede donar. "
                          f"Motivo: {donante.motivo_denegacion_permanente or 'No especificado'}. "
                          f"Fecha: {donante.fecha_denegacion_permanente.strftime('%d/%m/%Y') if donante.fecha_denegacion_permanente else 'No registrada'}."
            })

        # Validar que el donante tenga entrevista aprobada Y esté apto para donación
        if donante:
            if not donante.tiene_entrevista_apro:
                raise serializers.ValidationError({
                    'donante': f"El donante '{donante}' no tiene una entrevista aprobada. "
                              f"Debe completar y aprobar la entrevista antes de crear una unidad de muestra."
                })
            
            if not donante.apto_donacion:
                raise serializers.ValidationError({
                    'donante': f"El donante '{donante}' no está apto para donación. "
                              f"Debe estar marcado como apto antes de crear una unidad de muestra."
                })
        
        # Validar que si se proporciona un código de donante, el donante coincida
        if codigo_donante and donante and codigo_donante.donante != donante:
            raise serializers.ValidationError({
                'codigo_donante': f"El donante '{donante}' no coincide con el donante del código '{codigo_donante.codigo}'"
            })

        return attrs

class DescarteMuestraCreateSerializer(serializers.Serializer):
    """
    Serializer para crear un descarte de muestra
    """
    motivo_id = serializers.PrimaryKeyRelatedField(
        queryset=CatalogoDescarte.objects.filter(activo=True),
        help_text="ID del motivo de descarte"
    )
    observaciones = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales del descarte"
    )
    
    def validate_motivo_id(self, value):
        if not value.activo:
            raise serializers.ValidationError("El motivo de descarte no está activo")
        return value

class ValidarDescarteSerializer(serializers.Serializer):
    """
    Serializer para validar un descarte de muestra
    """
    validado = serializers.BooleanField(
        help_text="Indica si se valida el descarte"
    )
    observaciones_validacion = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Observaciones de la validación"
    )

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

class TransformarMuestraSerializer(serializers.Serializer):
    """
    Serializer para transformar una muestra con el formato de correlativo solicitado
    """
    nuevo_tipo_unidad = serializers.ChoiceField(
        choices=UnidadMuestra.TIPO_UNIDAD_CHOICES,
        help_text="Tipo de unidad de la muestra transformada"
    )
    volumen_ml = serializers.IntegerField(
        min_value=1,
        help_text="Volumen en ml de la muestra transformada"
    )
    observaciones = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales de la transformación"
    )
    
    def validate_nuevo_tipo_unidad(self, value):
        """
        Validar que el nuevo tipo de unidad sea diferente al actual
        """
        # Esta validación se hará en la vista ya que necesitamos acceso a la muestra original
        return value
    
    def validate_volumen_ml(self, value):
        """
        Validar que el volumen sea positivo
        """
        if value <= 0:
            raise serializers.ValidationError("El volumen debe ser mayor a 0")
        return value


class TransformacionItemSerializer(serializers.Serializer):
    """
    Serializer para un item individual en la transformación en lote
    """
    id = serializers.IntegerField(
        help_text="ID de la unidad de muestra a transformar"
    )
    nuevo_tipo_unidad = serializers.ChoiceField(
        choices=UnidadMuestra.TIPO_UNIDAD_CHOICES,
        help_text="Tipo de unidad de la muestra transformada"
    )
    volumen_ml = serializers.IntegerField(
        min_value=1,
        help_text="Volumen en ml de la muestra transformada"
    )
    observaciones = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
        help_text="Observaciones adicionales de la transformación"
    )


class TransformarLoteMuestrasSerializer(serializers.Serializer):
    """
    Serializer para transformar múltiples muestras en una sola petición
    """
    transformaciones = TransformacionItemSerializer(many=True)
    
    def validate_transformaciones(self, value):
        """
        Validar que haya al menos una transformación y no más de 50
        """
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos una transformación")
        
        if len(value) > 50:
            raise serializers.ValidationError("No se pueden transformar más de 50 muestras a la vez")
        
        # Verificar que no haya IDs duplicados
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No se pueden transformar la misma muestra múltiples veces")
        
        return value


class TransformacionMultipleItemSerializer(serializers.Serializer):
    """
    Serializer para un item individual al transformar UNA unidad padre en MÚLTIPLES hijas
    """
    nuevo_tipo_unidad = serializers.ChoiceField(
        choices=UnidadMuestra.TIPO_UNIDAD_CHOICES,
        help_text="Tipo de unidad de la muestra transformada"
    )
    volumen_ml = serializers.IntegerField(
        min_value=1,
        help_text="Volumen en ml de la muestra transformada"
    )
    observaciones = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
        help_text="Observaciones adicionales de la transformación"
    )


class TransformarMultipleSerializer(serializers.Serializer):
    """
    Serializer para transformar UNA unidad padre en MÚLTIPLES unidades hijas
    """
    transformaciones = TransformacionMultipleItemSerializer(many=True)
    
    def validate_transformaciones(self, value):
        """
        Validar que haya al menos una transformación y no más de 20
        """
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos una transformación")
        
        if len(value) > 20:
            raise serializers.ValidationError("No se pueden crear más de 20 unidades hijas a la vez")
        
        return value


class DetalleSalidaUnidadSerializer(serializers.ModelSerializer):
    unidad_muestra = UnidadMuestraSerializer(read_only=True)
    
    class Meta:
        model = DetalleaSalidaUnidad
        fields = ['id', 'unidad_muestra']


class SalidaUnidadSerializer(serializers.ModelSerializer):
    detalles = DetalleSalidaUnidadSerializer(many=True, read_only=True)
    unidades = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="Lista de IDs de unidades de muestra"
    )
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SalidaUnidad
        fields = [
            'id',
            'correlativo',
            'receptor',
            'identificador_receptor',
            'medico_solicitante',
            'fecha_salida',
            'observaciones',
            'tecnico',
            'tecnico_id',
            'tecnico_nombre',
            'cantidad_unidades',
            'unidades',
            'detalles',
            'pdf_salida',
            'pdf_url',
            'creado'
        ]
        read_only_fields = ['correlativo', 'pdf_salida', 'creado']
    
    def get_pdf_url(self, obj):
        if obj.pdf_salida:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_salida.url)
        return None
    
    def validate_unidades(self, value):
        """Validar que las unidades existan y estén disponibles"""
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos una unidad")
        
        unidades = UnidadMuestra.objects.filter(id__in=value)
        
        if unidades.count() != len(value):
            raise serializers.ValidationError("Algunas unidades no existen")
        
        # Validar que estén disponibles
        no_disponibles = []
        for unidad in unidades:
            if unidad.estado not in ['DISPONIBLE']:
                no_disponibles.append(unidad.correlativo)
        
        if no_disponibles:
            raise serializers.ValidationError(
                f"Las siguientes unidades no están disponibles: {', '.join(no_disponibles)}"
            )
        
        return value
    
    def create(self, validated_data):
        unidades_ids = validated_data.pop('unidades')
        
        # Crear la salida
        salida = SalidaUnidad.objects.create(**validated_data)
        
        # Crear los detalles y cambiar estado a RESERVADO
        for unidad_id in unidades_ids:
            unidad = UnidadMuestra.objects.get(id=unidad_id)
            DetalleaSalidaUnidad.objects.create(
                salida=salida,
                unidad_muestra=unidad
            )
            # Cambiar estado para que no se pueda usar más
            unidad.estado = 'RESERVADO'
            unidad.save(update_fields=['estado'])
        
        return salida