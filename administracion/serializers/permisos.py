from rest_framework import serializers
from administracion.models.permisos import PermisoPersonalizado

class PermisoPersonalizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisoPersonalizado
        fields = ['id', 'nombre', 'vista_modulo', 'activo']