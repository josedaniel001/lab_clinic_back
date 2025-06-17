from rest_framework import serializers
from .models import Pais, Departamento, Municipio

class PaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pais
        fields = ['id', 'nombre']

class DepartamentoSerializer(serializers.ModelSerializer):
    pais = PaisSerializer(read_only=True)

    class Meta:
        model = Departamento
        fields = ['id', 'nombre', 'pais']

class MunicipioSerializer(serializers.ModelSerializer):
    departamento = DepartamentoSerializer(read_only=True)

    class Meta:
        model = Municipio
        fields = ['id', 'nombre', 'departamento']
