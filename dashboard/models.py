from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum, Avg, Q
from pacientes.models import Paciente
from medicos.models import Medico
from ordenes.models import Orden
from resultados.models import Resultado
from examenes.models import Examen
from banco_sangre.models import Donante


class DashboardMetric(models.Model):
    """Modelo para almacenar métricas del dashboard"""
    nombre = models.CharField(max_length=100, unique=True)
    valor = models.FloatField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.CharField(max_length=50, choices=[
        ('pacientes', 'Pacientes'),
        ('examenes', 'Exámenes'),
        ('resultados', 'Resultados'),
        ('financiero', 'Financiero'),
        ('operativo', 'Operativo'),
    ])
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Métrica del Dashboard'
        verbose_name_plural = 'Métricas del Dashboard'
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return f"{self.nombre}: {self.valor}"

    @classmethod
    def get_metricas_pacientes(cls):
        """Obtiene métricas relacionadas con pacientes"""
        total_pacientes = Paciente.objects.count()
        pacientes_hoy = Paciente.objects.filter(
            fecha_creacion__date=timezone.now().date()
        ).count()
        pacientes_mes = Paciente.objects.filter(
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year
        ).count()
        
        return {
            'total_pacientes': total_pacientes,
            'pacientes_hoy': pacientes_hoy,
            'pacientes_mes': pacientes_mes,
        }

    @classmethod
    def get_metricas_examenes(cls):
        """Obtiene métricas relacionadas con exámenes"""
        total_examenes = Examen.objects.count()
        examenes_pendientes = Examen.objects.filter(estado='pendiente').count()
        examenes_completados = Examen.objects.filter(estado='completado').count()
        examenes_mes = Examen.objects.filter(
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year
        ).count()
        
        return {
            'total_examenes': total_examenes,
            'examenes_pendientes': examenes_pendientes,
            'examenes_completados': examenes_completados,
            'examenes_mes': examenes_mes,
        }

    @classmethod
    def get_metricas_resultados(cls):
        """Obtiene métricas relacionadas con resultados"""
        total_resultados = Resultado.objects.count()
        resultados_pendientes = Resultado.objects.filter(estado='pendiente').count()
        resultados_completados = Resultado.objects.filter(estado='completado').count()
        resultados_mes = Resultado.objects.filter(
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year
        ).count()
        
        return {
            'total_resultados': total_resultados,
            'resultados_pendientes': resultados_pendientes,
            'resultados_completados': resultados_completados,
            'resultados_mes': resultados_mes,
        }

    @classmethod
    def get_metricas_ordenes(cls):
        """Obtiene métricas relacionadas con órdenes"""
        total_ordenes = Orden.objects.count()
        ordenes_pendientes = Orden.objects.filter(estado='pendiente').count()
        ordenes_completadas = Orden.objects.filter(estado='completada').count()
        ordenes_mes = Orden.objects.filter(
            fecha_creacion__month=timezone.now().month,
            fecha_creacion__year=timezone.now().year
        ).count()
        
        return {
            'total_ordenes': total_ordenes,
            'ordenes_pendientes': ordenes_pendientes,
            'ordenes_completadas': ordenes_completadas,
            'ordenes_mes': ordenes_mes,
        }

    @classmethod
    def get_metricas_medicos(cls):
        """Obtiene métricas relacionadas con médicos"""
        total_medicos = Medico.objects.count()
        medicos_activos = Medico.objects.filter(activo=True).count()
        medicos_inactivos = Medico.objects.filter(activo=False).count()
        
        return {
            'total_medicos': total_medicos,
            'medicos_activos': medicos_activos,
            'medicos_inactivos': medicos_inactivos,
        }

    @classmethod
    def get_metricas_banco_sangre(cls):
        """Obtiene métricas del banco de sangre"""
        total_donantes = Donante.objects.count()
        donantes_activos = Donante.objects.filter(activo=True).count()
        donaciones_mes = Donante.objects.filter(
            fecha_ultima_donacion__month=timezone.now().month,
            fecha_ultima_donacion__year=timezone.now().year
        ).count()
        
        return {
            'total_donantes': total_donantes,
            'donantes_activos': donantes_activos,
            'donaciones_mes': donaciones_mes,
        }


class DashboardWidget(models.Model):
    """Modelo para configurar widgets del dashboard"""
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=[
        ('grafico', 'Gráfico'),
        ('metrica', 'Métrica'),
        ('tabla', 'Tabla'),
        ('lista', 'Lista'),
    ])
    configuracion = models.JSONField(default=dict)
    posicion_x = models.IntegerField(default=0)
    posicion_y = models.IntegerField(default=0)
    ancho = models.IntegerField(default=4)
    alto = models.IntegerField(default=3)
    activo = models.BooleanField(default=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Widget del Dashboard'
        verbose_name_plural = 'Widgets del Dashboard'
        ordering = ['posicion_y', 'posicion_x']

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class DashboardConfig(models.Model):
    """Configuración general del dashboard"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    configuracion = models.JSONField(default=dict)
    tema = models.CharField(max_length=20, choices=[
        ('claro', 'Claro'),
        ('oscuro', 'Oscuro'),
        ('auto', 'Automático'),
    ], default='auto')
    actualizacion_automatica = models.BooleanField(default=True)
    intervalo_actualizacion = models.IntegerField(default=30)  # segundos
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración del Dashboard'
        verbose_name_plural = 'Configuraciones del Dashboard'

    def __str__(self):
        return f"Configuración de {self.usuario.username}"
