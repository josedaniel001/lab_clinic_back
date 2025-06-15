from rest_framework import serializers
from .models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

    def validate(self, data):
        nombre = data.get("nombre")
        edad = data.get("edad")
        sexo = data.get("sexo")
        celular = data.get("celular")

        if Paciente.objects.filter(
            nombre__iexact=nombre.strip(),
            edad=edad,
            sexo=sexo,
            celular=celular
        ).exists():
            raise serializers.ValidationError("Este paciente ya está registrado.")

        return data