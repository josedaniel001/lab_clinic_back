# banco_sangre/serializers.py

from rest_framework import serializers
from ordenes.serializers import OrdenSerializer
from ordenes.models import Orden
from .models import Donante, MuestraSangre,Entrevista, UnidadMuestra

class DonanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donante
        fields = '__all__'

class MuestraSangreSerializer(serializers.ModelSerializer):
    donante = DonanteSerializer(read_only=True)
    donante_id = serializers.PrimaryKeyRelatedField(
        queryset=Donante.objects.all(),
        source='donante',
        write_only=True,
        required=False
    )
    responsable_nombre = serializers.CharField(source='responsable.username', read_only=True)

    class Meta:
        model = MuestraSangre
        fields = '__all__'
# banco_sangre/serializers.py

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
            'fecha_caducidad',
            'estado',
            'dias_vigencia',
        ]