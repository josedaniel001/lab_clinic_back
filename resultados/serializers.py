from rest_framework import serializers
from .models import Resultado, ResultadoDetalle, CatalogoMotivoDenegacion, HistorialDenegacion

class CatalogoMotivoDenegacionSerializer(serializers.ModelSerializer):
    """Serializer para el catálogo de motivos de denegación"""
    es_permanente = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CatalogoMotivoDenegacion
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 
            'tipo_denegacion', 'es_permanente', 'tiempo_diferimiento_dias',
            'activo', 'fecha_creacion'
        ]
        read_only_fields = ['fecha_creacion', 'es_permanente']


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
    valores = ResultadoDetalleSerializer(many=True)
    motivo_denegacion_detalle = CatalogoMotivoDenegacionSerializer(source='motivo_denegacion', read_only=True)

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
            'motivo_denegacion',
            'motivo_denegacion_detalle',
            'observaciones_denegacion',
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

class HistorialDenegacionSerializer(serializers.ModelSerializer):
    """Serializer para el historial de denegaciones"""
    donante_nombre = serializers.CharField(source='donante.__str__', read_only=True)
    orden_codigo = serializers.CharField(source='orden.codigo', read_only=True)
    motivo_detalle = CatalogoMotivoDenegacionSerializer(source='motivo_denegacion', read_only=True)
    
    class Meta:
        model = HistorialDenegacion
        fields = [
            'id',
            'donante',
            'donante_nombre',
            'resultado',
            'orden',
            'orden_codigo',
            'motivo_denegacion',
            'motivo_detalle',
            'observaciones',
            'usuario_deniego',
            'fecha_denegacion',
            'resultado_examen',
            'valores_criticos',
        ]
        read_only_fields = ['fecha_denegacion']


class RevertirValidacionSerializer(serializers.Serializer):
    """
    Serializer para revertir un resultado validado a EN PROCESO
    """
    motivo_reversion = serializers.CharField(
        max_length=500,
        required=False,
        default='Reversión por emergencia',
        help_text="Motivo por el cual se revierte la validación"
    )
    usuario_responsable = serializers.CharField(
        max_length=100,
        required=False,
        default='Sistema',
        help_text="Usuario que realiza la reversión"
    )