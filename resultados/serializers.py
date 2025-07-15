from rest_framework import serializers
from .models import Resultado, ResultadoDetalle

class ResultadoDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoDetalle
        fields = ['parametro', 'valor', 'unidad', 'rango_normal', 'estado']

class ResultadoSerializer(serializers.ModelSerializer):
    numero_orden = serializers.SerializerMethodField()
    paciente = serializers.SerializerMethodField()
    donante = serializers.SerializerMethodField()
    numero_documento_paciente = serializers.SerializerMethodField()
    numero_documento_donante = serializers.SerializerMethodField()
    medico = serializers.SerializerMethodField()
    examen = serializers.SerializerMethodField()
    valores = ResultadoDetalleSerializer( many=True)

    class Meta:
        model = Resultado
        fields = [
            'id',
            'numero_orden',
            'paciente',
            'donante',
            'numero_documento_paciente',
            'numero_documento_donante',
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
        orden = obj.resultado.orden
        if orden.paciente:
            return f"{orden.paciente.nombres} {orden.paciente.apellidos}"
        return None
    def get_numero_documento_paciente(self, obj):
        orden = obj.resultado.orden
        if orden.paciente:
            return orden.paciente.numero_documento
        return None

    def get_donante(self, obj):
        orden = obj.resultado.orden
        if orden.donante:
            return f"{orden.donante.primer_nombre} {orden.donante.primer_apellido}"
        return None
    
    def get_numero_documento_donante(self, obj):
        orden = obj.resultado.orden
        if orden.donante:
            return orden.donante.cui
        return None

    def get_medico(self, obj):
        return obj.resultado.orden.medico.nombres+" "+obj.resultado.orden.medico.apellidos if obj.resultado.orden.medico else "N/A"

    def get_examen(self, obj):
        return obj.resultado.examen.nombre