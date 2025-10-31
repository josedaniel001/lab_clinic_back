# banco_sangre/reports_serializers.py

from rest_framework import serializers


class EstadisticasGeneralesSerializer(serializers.Serializer):
    """Estadísticas generales del banco de sangre"""
    total_donantes = serializers.IntegerField()
    donantes_activos = serializers.IntegerField()
    donantes_aptos = serializers.IntegerField()
    total_unidades = serializers.IntegerField()
    unidades_disponibles = serializers.IntegerField()
    unidades_reservadas = serializers.IntegerField()
    unidades_vencidas = serializers.IntegerField()
    unidades_descartadas = serializers.IntegerField()
    total_entrevistas = serializers.IntegerField()
    entrevistas_aprobadas = serializers.IntegerField()
    entrevistas_rechazadas = serializers.IntegerField()


class InventarioTipoSangreSerializer(serializers.Serializer):
    """Inventario por tipo de sangre"""
    tipo_sangre = serializers.CharField()
    total_unidades = serializers.IntegerField()
    disponibles = serializers.IntegerField()
    reservadas = serializers.IntegerField()
    vencidas = serializers.IntegerField()
    descartadas = serializers.IntegerField()
    volumen_total_ml = serializers.IntegerField()


class InventarioTipoUnidadSerializer(serializers.Serializer):
    """Inventario por tipo de unidad"""
    tipo_unidad = serializers.CharField()
    tipo_unidad_display = serializers.CharField()
    total_unidades = serializers.IntegerField()
    disponibles = serializers.IntegerField()
    reservadas = serializers.IntegerField()
    vencidas = serializers.IntegerField()
    descartadas = serializers.IntegerField()
    volumen_total_ml = serializers.IntegerField()


class UnidadesProximasVencerSerializer(serializers.Serializer):
    """Unidades próximas a vencer"""
    id = serializers.IntegerField()
    correlativo = serializers.CharField()
    tipo_unidad = serializers.CharField()
    tipo_sangre = serializers.CharField()
    volumen_ml = serializers.IntegerField()
    fecha_caducidad = serializers.DateField()
    dias_restantes = serializers.IntegerField()
    estado = serializers.CharField()
    localizacion = serializers.CharField()


class DonacionesPorPeriodoSerializer(serializers.Serializer):
    """Donaciones por período de tiempo"""
    fecha = serializers.DateField()
    total_donaciones = serializers.IntegerField()
    total_unidades_creadas = serializers.IntegerField()
    volumen_total_ml = serializers.IntegerField()


class EstadisticasDonanteSerializer(serializers.Serializer):
    """Estadísticas de donantes"""
    sexo_masculino = serializers.IntegerField()
    sexo_femenino = serializers.IntegerField()
    edad_promedio = serializers.FloatField()
    edad_minima = serializers.IntegerField()
    edad_maxima = serializers.IntegerField()
    total_donantes_activos = serializers.IntegerField()
    donantes_por_tipo_sangre = serializers.DictField()
    donantes_por_municipio = serializers.DictField()


class ReporteDescartesSerializer(serializers.Serializer):
    """Reporte de descartes"""
    motivo = serializers.CharField()
    motivo_codigo = serializers.CharField()
    total_descartes = serializers.IntegerField()
    validados = serializers.IntegerField()
    pendientes_validacion = serializers.IntegerField()
    volumen_total_descartado_ml = serializers.IntegerField()


class MovimientosInventarioSerializer(serializers.Serializer):
    """Movimientos del inventario (entradas y salidas)"""
    fecha = serializers.DateField()
    entradas = serializers.IntegerField()
    salidas = serializers.IntegerField()
    descartes = serializers.IntegerField()
    transformaciones = serializers.IntegerField()
    inventario_final = serializers.IntegerField()


class TiempoPromedioProcesoSerializer(serializers.Serializer):
    """Tiempo promedio de los procesos"""
    promedio_dias_orden_a_entrevista = serializers.FloatField()
    promedio_dias_entrevista_a_muestra = serializers.FloatField()
    promedio_dias_muestra_a_salida = serializers.FloatField()


class DonantesRecurrentesSerializer(serializers.Serializer):
    """Donantes recurrentes (más de una donación)"""
    donante_id = serializers.IntegerField()
    cui = serializers.CharField()
    nombre_completo = serializers.CharField()
    total_donaciones = serializers.IntegerField()
    ultima_donacion = serializers.DateField()
    tipo_sangre = serializers.CharField()


class SalidaPorInstitucionSerializer(serializers.Serializer):
    """Salidas por institución/receptor"""
    receptor = serializers.CharField()
    medico_solicitante = serializers.CharField()
    total_salidas = serializers.IntegerField()
    total_unidades = serializers.IntegerField()
    volumen_total_ml = serializers.IntegerField()


class CompatibilidadSangreSerializer(serializers.Serializer):
    """Análisis de compatibilidad de tipos de sangre disponibles"""
    tipo_sangre = serializers.CharField()
    unidades_disponibles = serializers.IntegerField()
    puede_donar_a = serializers.ListField(child=serializers.CharField())
    puede_recibir_de = serializers.ListField(child=serializers.CharField())
    cobertura_poblacion_pct = serializers.FloatField()


class ResumenMensualSerializer(serializers.Serializer):
    """Resumen mensual del banco de sangre"""
    mes = serializers.CharField()
    año = serializers.IntegerField()
    nuevos_donantes = serializers.IntegerField()
    entrevistas_realizadas = serializers.IntegerField()
    unidades_creadas = serializers.IntegerField()
    unidades_salida = serializers.IntegerField()
    unidades_descartadas = serializers.IntegerField()
    volumen_total_recolectado_ml = serializers.IntegerField()


class AlertasInventarioSerializer(serializers.Serializer):
    """Alertas del inventario"""
    tipo_alerta = serializers.CharField()
    nivel = serializers.CharField()  # 'critico', 'advertencia', 'info'
    mensaje = serializers.CharField()
    cantidad = serializers.IntegerField()
    detalles = serializers.DictField()

