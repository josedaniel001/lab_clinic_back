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
        queryset=Donante.objects.all(), source='donante', write_only=True
    )
    orden = OrdenSerializer(read_only=True)
    orden_id = serializers.PrimaryKeyRelatedField(
        queryset=Orden.objects.all(), source='orden', write_only=True
    )

    class Meta:
        model = Entrevista
        fields = [
            'id', 'correlativo', 'donante', 'donante_id',
            'orden', 'orden_id', 'doctor', 'donador_de',
            'fecha', 'fecha_entrega', 'resultado',
            'observaciones', 'creado'
        ]

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
    class Meta:
        model = UnidadMuestra
        fields = [
            'id',
            'correlativo',
            'donante',
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