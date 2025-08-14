# banco_sangre/serializers.py

from rest_framework import serializers
from ordenes.serializers import OrdenSerializer
from ordenes.models import Orden
from .models import Donante, Entrevista, UnidadMuestra, Lote

class DonanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donante
        fields = '__all__'

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
        
        return attrs

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
            'creado',
        ]

    def validate(self, attrs):
        donante = attrs.get('donante')

        if donante and not donante.apto_donacion:
            raise serializers.ValidationError(
            f"El donante '{donante}' no está apto para donar."
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