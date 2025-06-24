from rest_framework import serializers
from .models import Examen

class ExamenSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField(read_only=True)  # ← No permite actualizar este campo
    class Meta:
        model = Examen
        fields = [
            'id',
            'codigo',
            'nombre',
            'categoria',
            'precio',
            'tiempo_procesamiento',
            'metodologia',
            'preparacion_paciente',
            'valores_referencia',
            'estado',
            'fecha_creacion',
        ]
def update(self, instance, validated_data):
        validated_data.pop('codigo', None)  # Se ignora cualquier intento de cambio
        return super().update(instance, validated_data)