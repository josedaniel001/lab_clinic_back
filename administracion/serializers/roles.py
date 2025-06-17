from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from administracion.models.permisos import PermisoPersonalizado

class PermisoPersonalizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermisoPersonalizado
        fields = ['id', 'nombre', 'vista_modulo', 'activo']

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class GrupoSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True, required=False
    )
    permisos_personalizados = serializers.PrimaryKeyRelatedField(
        queryset=PermisoPersonalizado.objects.all(), many=True, required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permisos_personalizados']

    def create(self, validated_data):
        permisos_django = validated_data.pop('permissions', [])
        permisos_personalizados = validated_data.pop('permisos_personalizados', [])
        grupo = Group.objects.create(**validated_data)
        grupo.permissions.set(permisos_django)
        grupo.permisos_personalizados.set(permisos_personalizados)
        return grupo

    def update(self, instance, validated_data):
        permisos_django = validated_data.pop('permissions', None)
        permisos_personalizados = validated_data.pop('permisos_personalizados', None)

        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if permisos_django is not None:
            instance.permissions.set(permisos_django)
        if permisos_personalizados is not None:
            instance.permisos_personalizados.set(permisos_personalizados)

        return instance
