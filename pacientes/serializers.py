from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    ciudad = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = [
            'id',
            'numero_documento',
            'tipo_documento',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'telefono',
            'email',
            'direccion',
            'ciudad',
            'genero',
            'estado_civil',
            'ocupacion',
            'fecha_registro',
            'activo',
        ]

    def get_ciudad(self, obj):
        return obj.municipio.nombre if obj.municipio else None

    def validate(self, data):
        numero_documento = (data.get("numero_documento") or "").strip()
        nombres = (data.get("nombres") or "").strip()
        apellidos = (data.get("apellidos") or "").strip()

        if Paciente.objects.filter(
            numero_documento__iexact=numero_documento,
            nombres__iexact=nombres,
            apellidos__iexact=apellidos
        ).exists():
            raise serializers.ValidationError("Este paciente ya está registrado.")

        return data

