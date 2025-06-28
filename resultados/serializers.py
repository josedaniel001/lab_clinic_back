from rest_framework import serializers
from .models import Resultado, ResultadoDetalle

class ResultadoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoDetalle
        fields = ['parametro', 'valor', 'unidad', 'rango_normal', 'estado']

class ResultadoSerializer(serializers.ModelSerializer):
    numero_orden = serializers.SerializerMethodField()
    paciente = serializers.SerializerMethodField()
    numero_documento_paciente = serializers.SerializerMethodField()
    medico = serializers.SerializerMethodField()
    examen = serializers.SerializerMethodField()
    valores = ResultadoDetalleSerializer( many=True)

    class Meta:
        model = Resultado
        fields = [
            'id',
            'numero_orden',
            'paciente',
            'numero_documento_paciente',
            'medico',
            'examen',
            'fecha_resultado',
            'fecha_validacion',
            'estado',
            'prioridad',
            'valores',
            'observaciones',
            'validado_por',
        ]

    def get_numero_orden(self, obj):
        return obj.resultado.orden.codigo

    def get_paciente(self, obj):
        return obj.resultado.orden.paciente.nombres+" "+obj.resultado.orden.paciente.apellidos

    def get_numero_documento_paciente(self, obj):
        return obj.resultado.orden.paciente.numero_documento

    def get_medico(self, obj):
        return obj.resultado.orden.medico.nombres+" "+obj.resultado.orden.medico.apellidos if obj.resultado.orden.medico else "N/A"

    def get_examen(self, obj):
        return obj.resultado.examen.nombre