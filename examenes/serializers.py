from rest_framework import serializers
from .models import Examen

class ExamenSerializer(serializers.ModelSerializer):
    codigo = serializers.CharField() 
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
        # Remueve el campo 'codigo' si alguien intenta modificarlo en PUT/PATCH
        validated_data.pop('codigo', None)
        return super().update(instance, validated_data)