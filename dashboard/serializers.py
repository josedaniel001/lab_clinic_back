from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DashboardMetric, DashboardWidget, DashboardConfig
from pacientes.models import Paciente
from medicos.models import Medico
from ordenes.models import Orden
from resultados.models import Resultado
from examenes.models import Examen
from banco_sangre.models import Donante
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek


class DashboardMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardMetric
        fields = '__all__'


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = '__all__'


class DashboardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardConfig
        fields = '__all__'


class MetricasGeneralesSerializer(serializers.Serializer):
    """Serializer para métricas generales del dashboard"""
    
    # Métricas de Pacientes
    total_pacientes = serializers.IntegerField()
    pacientes_hoy = serializers.IntegerField()
    pacientes_mes = serializers.IntegerField()
    pacientes_semana = serializers.IntegerField()
    
    # Métricas de Exámenes
    total_examenes = serializers.IntegerField()
    examenes_pendientes = serializers.IntegerField()
    examenes_completados = serializers.IntegerField()
    examenes_mes = serializers.IntegerField()
    examenes_semana = serializers.IntegerField()
    
    # Métricas de Resultados
    total_resultados = serializers.IntegerField()
    resultados_pendientes = serializers.IntegerField()
    resultados_completados = serializers.IntegerField()
    resultados_mes = serializers.IntegerField()
    resultados_semana = serializers.IntegerField()
    
    # Métricas de Órdenes
    total_ordenes = serializers.IntegerField()
    ordenes_pendientes = serializers.IntegerField()
    ordenes_completadas = serializers.IntegerField()
    ordenes_mes = serializers.IntegerField()
    ordenes_semana = serializers.IntegerField()
    
    # Métricas de Médicos
    total_medicos = serializers.IntegerField()
    medicos_activos = serializers.IntegerField()
    medicos_inactivos = serializers.IntegerField()
    
    # Métricas del Banco de Sangre
    total_donantes = serializers.IntegerField()
    donantes_activos = serializers.IntegerField()
    donaciones_mes = serializers.IntegerField()
    donaciones_semana = serializers.IntegerField()
    
    # Métricas de Usuarios
    total_usuarios = serializers.IntegerField()
    usuarios_activos = serializers.IntegerField()
    usuarios_inactivos = serializers.IntegerField()


class GraficoExamenesPorDiaSerializer(serializers.Serializer):
    """Serializer para gráfico de exámenes por día"""
    fecha = serializers.DateField()
    total = serializers.IntegerField()
    completados = serializers.IntegerField()
    pendientes = serializers.IntegerField()


class GraficoPacientesPorMesSerializer(serializers.Serializer):
    """Serializer para gráfico de pacientes por mes"""
    mes = serializers.CharField()
    total = serializers.IntegerField()
    nuevos = serializers.IntegerField()


class GraficoResultadosPorEstadoSerializer(serializers.Serializer):
    """Serializer para gráfico de resultados por estado"""
    estado = serializers.CharField()
    total = serializers.IntegerField()
    porcentaje = serializers.FloatField()


class GraficoOrdenesPorMedicoSerializer(serializers.Serializer):
    """Serializer para gráfico de órdenes por médico"""
    medico = serializers.CharField()
    total = serializers.IntegerField()
    completadas = serializers.IntegerField()
    pendientes = serializers.IntegerField()


class TopExamenesSerializer(serializers.Serializer):
    """Serializer para top exámenes más solicitados"""
    nombre = serializers.CharField()
    total = serializers.IntegerField()
    porcentaje = serializers.FloatField()


class TopMedicosSerializer(serializers.Serializer):
    """Serializer para top médicos más activos"""
    medico = serializers.CharField()
    total_ordenes = serializers.IntegerField()
    total_pacientes = serializers.IntegerField()


class EstadisticasTiempoRespuestaSerializer(serializers.Serializer):
    """Serializer para estadísticas de tiempo de respuesta"""
    promedio_horas = serializers.FloatField()
    mediana_horas = serializers.FloatField()
    minimo_horas = serializers.FloatField()
    maximo_horas = serializers.FloatField()
    total_muestras = serializers.IntegerField()


class AlertasSerializer(serializers.Serializer):
    """Serializer para alertas del sistema"""
    tipo = serializers.CharField()
    mensaje = serializers.CharField()
    severidad = serializers.CharField()
    fecha = serializers.DateTimeField()
    resuelto = serializers.BooleanField()


class ResumenFinancieroSerializer(serializers.Serializer):
    """Serializer para resumen financiero"""
    ingresos_mes = serializers.DecimalField(max_digits=10, decimal_places=2)
    ingresos_semana = serializers.DecimalField(max_digits=10, decimal_places=2)
    ingresos_hoy = serializers.DecimalField(max_digits=10, decimal_places=2)
    promedio_por_orden = serializers.DecimalField(max_digits=10, decimal_places=2)
    crecimiento_mensual = serializers.FloatField()


class DashboardCompletoSerializer(serializers.Serializer):
    """Serializer completo del dashboard"""
    metricas = MetricasGeneralesSerializer()
    grafico_examenes_dia = GraficoExamenesPorDiaSerializer(many=True)
    grafico_pacientes_mes = GraficoPacientesPorMesSerializer(many=True)
    grafico_resultados_estado = GraficoResultadosPorEstadoSerializer(many=True)
    grafico_ordenes_medico = GraficoOrdenesPorMedicoSerializer(many=True)
    top_examenes = TopExamenesSerializer(many=True)
    top_medicos = TopMedicosSerializer(many=True)
    estadisticas_tiempo = EstadisticasTiempoRespuestaSerializer()
    alertas = AlertasSerializer(many=True)
    resumen_financiero = ResumenFinancieroSerializer()
    fecha_actualizacion = serializers.DateTimeField()
