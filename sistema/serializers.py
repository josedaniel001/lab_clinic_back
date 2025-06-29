# apps/sistema/serializers.py

from rest_framework import serializers
from .models import ConfiguracionLaboratorio

class ConfiguracionLaboratorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionLaboratorio
        fields = '__all__'
