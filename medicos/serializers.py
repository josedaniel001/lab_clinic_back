from rest_framework import serializers
from .models import Medico

class MedicoSerializer(serializers.ModelSerializer):
    ciudad = serializers.SerializerMethodField()

    class Meta:
        model = Medico
        fields = [
            'id',
            'numero_documento',
            'tipo_documento',
            'nombres',
            'apellidos',            
            'telefono_consultorio',
            'celular',
            'codigo_laboratorio',
            'email',
            'direccion_consultorio',
            'ciudad',
            'genero',
            'especialidad_medica',            
            'fecha_registro',
            'activo',
        ]

    def get_ciudad(self, obj):
        return obj.municipio.nombre if obj.municipio else None

    def validate(self, data):
        numero_documento = (data.get("numero_documento") or "").strip()
        nombres = (data.get("nombres") or "").strip()
        apellidos = (data.get("apellidos") or "").strip()

        if Medico.objects.filter(
            numero_documento__iexact=numero_documento,
            nombres__iexact=nombres,
            apellidos__iexact=apellidos
        ).exists():
            raise serializers.ValidationError("Este medico/a ya está registrado.")

        return data

