from django.contrib.auth.models import User, Group, Permission
from rest_framework import serializers
from .models import PermisoPersonalizado

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class PermisoPersonalizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisoPersonalizado
        fields = ['id', 'nombre', 'vista_modulo', 'activo']

class GrupoSerializer(serializers.ModelSerializer):
    permissions = PermisoSerializer(many=True, read_only=True)
    permisos_personalizados = PermisoPersonalizadoSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def create(self, validated_data):
        permisos = validated_data.pop('permissions', [])
        grupo = Group.objects.create(**validated_data)
        grupo.permissions.set(permisos)
        return grupo

    def update(self, instance, validated_data):
        permisos = validated_data.pop('permissions', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if permisos is not None:
            instance.permissions.set(permisos)
        return instance


class UsuarioSerializer(serializers.ModelSerializer):
    groups = GrupoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'groups']


