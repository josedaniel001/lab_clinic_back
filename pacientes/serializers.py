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
        nombres = data.get("nombres")
        apellidos = data.get("apellidos")
        numero_documento = data.get("numero_documento")

        if Paciente.objects.filter(
            numero_documento__iexact=numero_documento.strip(),
            nombres__iexact=nombres.strip(),
            apellidos__iexact=apellidos.strip()
        ).exists():
            raise serializers.ValidationError("Este paciente ya está registrado.")

        return data
