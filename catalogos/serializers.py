from rest_framework import serializers
from .models import CatalogoUnidadParametro

class CatalogoUnidadParametroSerializer(serializers.ModelSerializer):
    """Serializer para el catálogo de unidades de parámetros"""
    
    class Meta:
        model = CatalogoUnidadParametro
        fields = [
            'id', 'codigo', 'nombre', 'simbolo', 'categoria', 
            'descripcion', 'activo', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion']
