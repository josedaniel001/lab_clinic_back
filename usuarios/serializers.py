from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from administracion.models.permisos import PermisoPersonalizado
from administracion.serializers.roles import GrupoSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    groups = GrupoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'groups']


