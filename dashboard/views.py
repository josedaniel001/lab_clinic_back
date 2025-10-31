from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek, TruncDate
from django.utils import timezone
from datetime import datetime, timedelta
from .models import DashboardMetric, DashboardWidget, DashboardConfig
from .serializers import (
    DashboardMetricSerializer, DashboardWidgetSerializer, DashboardConfigSerializer,
    MetricasGeneralesSerializer, GraficoExamenesPorDiaSerializer,
    GraficoPacientesPorMesSerializer, GraficoResultadosPorEstadoSerializer,
    GraficoOrdenesPorMedicoSerializer, TopExamenesSerializer, TopMedicosSerializer,
    EstadisticasTiempoRespuestaSerializer, AlertasSerializer, ResumenFinancieroSerializer,
    DashboardCompletoSerializer
)
from pacientes.models import Paciente
from medicos.models import Medico
from ordenes.models import Orden
from resultados.models import Resultado
from examenes.models import Examen
from banco_sangre.models import Donante
import logging

logger = logging.getLogger(__name__)


class DashboardMetricViewSet(viewsets.ModelViewSet):
    queryset = DashboardMetric.objects.all()
    serializer_class = DashboardMetricSerializer

    @action(detail=False, methods=['get'])
    def metricas_generales(self, request):
        """Obtiene métricas generales del sistema"""
        try:
            hoy = timezone.now().date()
            inicio_mes = hoy.replace(day=1)
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            
            # Métricas de Pacientes
            total_pacientes = Paciente.objects.count()
            pacientes_hoy = Paciente.objects.filter(fecha_registro=hoy).count()
            pacientes_mes = Paciente.objects.filter(
                fecha_registro__gte=inicio_mes
            ).count()
            pacientes_semana = Paciente.objects.filter(
                fecha_registro__gte=inicio_semana
            ).count()
            
            # Métricas de Exámenes
            total_examenes = Examen.objects.count()
            examenes_pendientes = Examen.objects.filter(estado='Pendiente').count()
            examenes_completados = Examen.objects.filter(estado='Completado').count()
            examenes_mes = Examen.objects.filter(
                fecha_creacion__gte=inicio_mes
            ).count()
            examenes_semana = Examen.objects.filter(
                fecha_creacion__gte=inicio_semana
            ).count()
            
            # Métricas de Resultados
            total_resultados = Resultado.objects.count()
            resultados_pendientes = Resultado.objects.filter(estado='PENDIENTE').count()
            resultados_completados = Resultado.objects.filter(estado='COMPLETADO').count()
            resultados_mes = Resultado.objects.filter(
                fecha_resultado__gte=inicio_mes
            ).count()
            resultados_semana = Resultado.objects.filter(
                fecha_resultado__gte=inicio_semana
            ).count()
            
            # Métricas de Órdenes
            total_ordenes = Orden.objects.count()
            ordenes_pendientes = Orden.objects.filter(estado='PENDIENTE').count()
            ordenes_completadas = Orden.objects.filter(estado='ENTREGADO').count()
            ordenes_mes = Orden.objects.filter(
                fecha__gte=inicio_mes
            ).count()
            ordenes_semana = Orden.objects.filter(
                fecha__gte=inicio_semana
            ).count()
            
            # Métricas de Médicos
            total_medicos = Medico.objects.count()
            medicos_activos = Medico.objects.filter(activo=True).count()
            medicos_inactivos = Medico.objects.filter(activo=False).count()
            
            # Métricas del Banco de Sangre
            total_donantes = Donante.objects.count()
            donantes_activos = Donante.objects.filter(activo=True).count()
            # Simular donaciones basadas en donantes activos (ya que no hay campo fecha_donacion)
            donaciones_mes = donantes_activos  # Simulación
            donaciones_semana = donantes_activos  # Simulación
            
            # Métricas de Usuarios
            total_usuarios = User.objects.count()
            usuarios_activos = User.objects.filter(is_active=True).count()
            usuarios_inactivos = User.objects.filter(is_active=False).count()
            
            metricas = {
                'total_pacientes': total_pacientes,
                'pacientes_hoy': pacientes_hoy,
                'pacientes_mes': pacientes_mes,
                'pacientes_semana': pacientes_semana,
                'total_examenes': total_examenes,
                'examenes_pendientes': examenes_pendientes,
                'examenes_completados': examenes_completados,
                'examenes_mes': examenes_mes,
                'examenes_semana': examenes_semana,
                'total_resultados': total_resultados,
                'resultados_pendientes': resultados_pendientes,
                'resultados_completados': resultados_completados,
                'resultados_mes': resultados_mes,
                'resultados_semana': resultados_semana,
                'total_ordenes': total_ordenes,
                'ordenes_pendientes': ordenes_pendientes,
                'ordenes_completadas': ordenes_completadas,
                'ordenes_mes': ordenes_mes,
                'ordenes_semana': ordenes_semana,
                'total_medicos': total_medicos,
                'medicos_activos': medicos_activos,
                'medicos_inactivos': medicos_inactivos,
                'total_donantes': total_donantes,
                'donantes_activos': donantes_activos,
                'donaciones_mes': donaciones_mes,
                'donaciones_semana': donaciones_semana,
                'total_usuarios': total_usuarios,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
            }
            
            serializer = MetricasGeneralesSerializer(metricas)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en metricas_generales: {str(e)}")
            return Response(
                {'error': 'Error al obtener métricas generales'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def grafico_examenes_dia(self, request):
        """Gráfico de exámenes por día (últimos 30 días)"""
        try:
            fecha_inicio = timezone.now().date() - timedelta(days=30)
            
            examenes_por_dia = Examen.objects.filter(
                fecha_creacion__gte=fecha_inicio
            ).annotate(
                fecha=TruncDate('fecha_creacion')
            ).values('fecha').annotate(
                total=Count('id'),
                completados=Count('id', filter=Q(estado='Completado')),
                pendientes=Count('id', filter=Q(estado='Pendiente'))
            ).order_by('fecha')
            
            serializer = GraficoExamenesPorDiaSerializer(examenes_por_dia, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en grafico_examenes_dia: {str(e)}")
            return Response(
                {'error': 'Error al obtener gráfico de exámenes por día'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def grafico_pacientes_mes(self, request):
        """Gráfico de pacientes por mes (últimos 12 meses)"""
        try:
            fecha_inicio = timezone.now().date() - timedelta(days=365)
            
            pacientes_por_mes = Paciente.objects.filter(
                fecha_registro__gte=fecha_inicio
            ).annotate(
                mes=TruncMonth('fecha_registro')
            ).values('mes').annotate(
                total=Count('id'),
                nuevos=Count('id')
            ).order_by('mes')
            
            # Formatear meses
            datos_formateados = []
            for item in pacientes_por_mes:
                datos_formateados.append({
                    'mes': item['mes'].strftime('%Y-%m'),
                    'total': item['total'],
                    'nuevos': item['nuevos']
                })
            
            serializer = GraficoPacientesPorMesSerializer(datos_formateados, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en grafico_pacientes_mes: {str(e)}")
            return Response(
                {'error': 'Error al obtener gráfico de pacientes por mes'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def grafico_resultados_estado(self, request):
        """Gráfico de resultados por estado"""
        try:
            resultados_por_estado = Resultado.objects.values('estado').annotate(
                total=Count('id')
            ).order_by('-total')
            
            total_resultados = sum(item['total'] for item in resultados_por_estado)
            
            datos_formateados = []
            for item in resultados_por_estado:
                porcentaje = (item['total'] / total_resultados * 100) if total_resultados > 0 else 0
                datos_formateados.append({
                    'estado': item['estado'],
                    'total': item['total'],
                    'porcentaje': round(porcentaje, 2)
                })
            
            serializer = GraficoResultadosPorEstadoSerializer(datos_formateados, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en grafico_resultados_estado: {str(e)}")
            return Response(
                {'error': 'Error al obtener gráfico de resultados por estado'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def grafico_ordenes_medico(self, request):
        """Gráfico de órdenes por médico (top 10)"""
        try:
            ordenes_por_medico = Orden.objects.values(
                'medico__nombre', 'medico__apellido'
            ).annotate(
                total=Count('id'),
                completadas=Count('id', filter=Q(estado='ENTREGADO')),
                pendientes=Count('id', filter=Q(estado='PENDIENTE'))
            ).order_by('-total')[:10]
            
            datos_formateados = []
            for item in ordenes_por_medico:
                nombre_completo = f"{item['medico__nombre']} {item['medico__apellido']}"
                datos_formateados.append({
                    'medico': nombre_completo,
                    'total': item['total'],
                    'completadas': item['completadas'],
                    'pendientes': item['pendientes']
                })
            
            serializer = GraficoOrdenesPorMedicoSerializer(datos_formateados, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en grafico_ordenes_medico: {str(e)}")
            return Response(
                {'error': 'Error al obtener gráfico de órdenes por médico'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def top_examenes(self, request):
        """Top exámenes más solicitados"""
        try:
            # Obtener exámenes más solicitados
            examenes_populares = Examen.objects.values('nombre').annotate(
                total=Count('id')
            ).order_by('-total')[:10]
            
            total_examenes = sum(item['total'] for item in examenes_populares)
            
            datos_formateados = []
            for item in examenes_populares:
                porcentaje = (item['total'] / total_examenes * 100) if total_examenes > 0 else 0
                datos_formateados.append({
                    'nombre': item['nombre'],
                    'total': item['total'],
                    'porcentaje': round(porcentaje, 2)
                })
            
            serializer = TopExamenesSerializer(datos_formateados, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en top_examenes: {str(e)}")
            return Response(
                {'error': 'Error al obtener top exámenes'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def top_medicos(self, request):
        """Top médicos más activos"""
        try:
            medicos_activos = Medico.objects.annotate(
                total_ordenes=Count('ordenes'),
                total_pacientes=Count('ordenes__paciente', distinct=True)
            ).order_by('-total_ordenes')[:10]
            
            datos_formateados = []
            for medico in medicos_activos:
                datos_formateados.append({
                    'medico': f"{medico.nombre} {medico.apellido}",
                    'total_ordenes': medico.total_ordenes,
                    'total_pacientes': medico.total_pacientes
                })
            
            serializer = TopMedicosSerializer(datos_formateados, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en top_medicos: {str(e)}")
            return Response(
                {'error': 'Error al obtener top médicos'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def estadisticas_tiempo_respuesta(self, request):
        """Estadísticas de tiempo de respuesta de resultados"""
        try:
            resultados_completados = Resultado.objects.filter(
                estado='COMPLETADO',
                fecha_resultado__isnull=False,
                fecha_validacion__isnull=False
            )
            
            if resultados_completados.exists():
                tiempos_respuesta = []
                for resultado in resultados_completados:
                    if resultado.fecha_resultado and resultado.fecha_validacion:
                        tiempo = (resultado.fecha_validacion - resultado.fecha_resultado).total_seconds() / 3600
                        tiempos_respuesta.append(tiempo)
                
                if tiempos_respuesta:
                    promedio = sum(tiempos_respuesta) / len(tiempos_respuesta)
                    mediana = sorted(tiempos_respuesta)[len(tiempos_respuesta) // 2]
                    minimo = min(tiempos_respuesta)
                    maximo = max(tiempos_respuesta)
                    
                    estadisticas = {
                        'promedio_horas': round(promedio, 2),
                        'mediana_horas': round(mediana, 2),
                        'minimo_horas': round(minimo, 2),
                        'maximo_horas': round(maximo, 2),
                        'total_muestras': len(tiempos_respuesta)
                    }
                else:
                    estadisticas = {
                        'promedio_horas': 0,
                        'mediana_horas': 0,
                        'minimo_horas': 0,
                        'maximo_horas': 0,
                        'total_muestras': 0
                    }
            else:
                estadisticas = {
                    'promedio_horas': 0,
                    'mediana_horas': 0,
                    'minimo_horas': 0,
                    'maximo_horas': 0,
                    'total_muestras': 0
                }
            
            serializer = EstadisticasTiempoRespuestaSerializer(estadisticas)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en estadisticas_tiempo_respuesta: {str(e)}")
            return Response(
                {'error': 'Error al obtener estadísticas de tiempo de respuesta'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def alertas(self, request):
        """Alertas del sistema"""
        try:
            alertas = []
            
            # Alerta: Exámenes pendientes por más de 24 horas
            examenes_pendientes_24h = Examen.objects.filter(
                estado='Pendiente',
                fecha_creacion__lt=timezone.now() - timedelta(hours=24)
            ).count()
            
            if examenes_pendientes_24h > 0:
                alertas.append({
                    'tipo': 'examenes_pendientes',
                    'mensaje': f'{examenes_pendientes_24h} exámenes pendientes por más de 24 horas',
                    'severidad': 'warning',
                    'fecha': timezone.now(),
                    'resuelto': False
                })
            
            # Alerta: Resultados pendientes por más de 48 horas
            resultados_pendientes_48h = Resultado.objects.filter(
                estado='PENDIENTE',
                fecha_resultado__lt=timezone.now() - timedelta(hours=48)
            ).count()
            
            if resultados_pendientes_48h > 0:
                alertas.append({
                    'tipo': 'resultados_pendientes',
                    'mensaje': f'{resultados_pendientes_48h} resultados pendientes por más de 48 horas',
                    'severidad': 'error',
                    'fecha': timezone.now(),
                    'resuelto': False
                })
            
            # Alerta: Pocos donantes activos
            donantes_activos = Donante.objects.filter(activo=True).count()
            if donantes_activos < 10:
                alertas.append({
                    'tipo': 'donantes_bajos',
                    'mensaje': f'Solo {donantes_activos} donantes activos en el banco de sangre',
                    'severidad': 'warning',
                    'fecha': timezone.now(),
                    'resuelto': False
                })
            
            serializer = AlertasSerializer(alertas, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en alertas: {str(e)}")
            return Response(
                {'error': 'Error al obtener alertas'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def resumen_financiero(self, request):
        """Resumen financiero (simulado)"""
        try:
            # Simular datos financieros (en un sistema real, estos vendrían de un módulo de facturación)
            hoy = timezone.now().date()
            inicio_mes = hoy.replace(day=1)
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            
            # Simular ingresos basados en órdenes completadas
            ordenes_mes = Orden.objects.filter(
                estado='ENTREGADO',
                fecha__gte=inicio_mes
            ).count()
            
            ordenes_semana = Orden.objects.filter(
                estado='ENTREGADO',
                fecha__gte=inicio_semana
            ).count()
            
            ordenes_hoy = Orden.objects.filter(
                estado='ENTREGADO',
                fecha=hoy
            ).count()
            
            # Simular precios (en un sistema real, estos vendrían de la configuración)
            precio_promedio_orden = 150.00  # Q150 por orden en promedio
            
            ingresos_mes = ordenes_mes * precio_promedio_orden
            ingresos_semana = ordenes_semana * precio_promedio_orden
            ingresos_hoy = ordenes_hoy * precio_promedio_orden
            
            # Calcular crecimiento mensual (simulado)
            mes_anterior = inicio_mes - timedelta(days=1)
            inicio_mes_anterior = mes_anterior.replace(day=1)
            ordenes_mes_anterior = Orden.objects.filter(
                estado='ENTREGADO',
                fecha__gte=inicio_mes_anterior,
                fecha__lt=inicio_mes
            ).count()
            
            if ordenes_mes_anterior > 0:
                crecimiento_mensual = ((ordenes_mes - ordenes_mes_anterior) / ordenes_mes_anterior) * 100
            else:
                crecimiento_mensual = 0
            
            resumen = {
                'ingresos_mes': round(ingresos_mes, 2),
                'ingresos_semana': round(ingresos_semana, 2),
                'ingresos_hoy': round(ingresos_hoy, 2),
                'promedio_por_orden': precio_promedio_orden,
                'crecimiento_mensual': round(crecimiento_mensual, 2)
            }
            
            serializer = ResumenFinancieroSerializer(resumen)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en resumen_financiero: {str(e)}")
            return Response(
                {'error': 'Error al obtener resumen financiero'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def dashboard_completo(self, request):
        """Dashboard completo con todas las métricas"""
        try:
            # Obtener todas las métricas
            metricas_response = self.metricas_generales(request)
            grafico_examenes_response = self.grafico_examenes_dia(request)
            grafico_pacientes_response = self.grafico_pacientes_mes(request)
            grafico_resultados_response = self.grafico_resultados_estado(request)
            grafico_ordenes_response = self.grafico_ordenes_medico(request)
            top_examenes_response = self.top_examenes(request)
            top_medicos_response = self.top_medicos(request)
            estadisticas_response = self.estadisticas_tiempo_respuesta(request)
            alertas_response = self.alertas(request)
            resumen_response = self.resumen_financiero(request)
            
            dashboard_data = {
                'metricas': metricas_response.data,
                'grafico_examenes_dia': grafico_examenes_response.data,
                'grafico_pacientes_mes': grafico_pacientes_response.data,
                'grafico_resultados_estado': grafico_resultados_response.data,
                'grafico_ordenes_medico': grafico_ordenes_response.data,
                'top_examenes': top_examenes_response.data,
                'top_medicos': top_medicos_response.data,
                'estadisticas_tiempo': estadisticas_response.data,
                'alertas': alertas_response.data,
                'resumen_financiero': resumen_response.data,
                'fecha_actualizacion': timezone.now()
            }
            
            serializer = DashboardCompletoSerializer(dashboard_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error en dashboard_completo: {str(e)}")
            return Response(
                {'error': 'Error al obtener dashboard completo'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer

    def get_queryset(self):
        """Filtrar widgets por usuario"""
        if self.request.user.is_authenticated:
            return DashboardWidget.objects.filter(
                Q(usuario=self.request.user) | Q(usuario__isnull=True)
            )
        return DashboardWidget.objects.filter(usuario__isnull=True)


class DashboardConfigViewSet(viewsets.ModelViewSet):
    queryset = DashboardConfig.objects.all()
    serializer_class = DashboardConfigSerializer

    def get_queryset(self):
        """Filtrar configuración por usuario"""
        if self.request.user.is_authenticated:
            return DashboardConfig.objects.filter(usuario=self.request.user)
        return DashboardConfig.objects.none()
