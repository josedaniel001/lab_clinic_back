# banco_sangre/reports_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Min, Max, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Donante, UnidadMuestra, Entrevista, DescarteMuestra, SalidaUnidad, DetalleaSalidaUnidad
from .reports_serializers import (
    EstadisticasGeneralesSerializer,
    InventarioTipoSangreSerializer,
    InventarioTipoUnidadSerializer,
    UnidadesProximasVencerSerializer,
    DonacionesPorPeriodoSerializer,
    EstadisticasDonanteSerializer,
    ReporteDescartesSerializer,
    MovimientosInventarioSerializer,
    DonantesRecurrentesSerializer,
    SalidaPorInstitucionSerializer,
    CompatibilidadSangreSerializer,
    ResumenMensualSerializer,
    AlertasInventarioSerializer,
)


class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para reportería avanzada y estadísticas del banco de sangre
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='estadisticas-generales')
    def estadisticas_generales(self, request):
        """
        Obtiene estadísticas generales del banco de sangre.
        
        GET /api/banco_sangre/reportes/estadisticas-generales/
        """
        # Donantes
        total_donantes = Donante.objects.count()
        donantes_activos = Donante.objects.filter(activo=True).count()
        donantes_aptos = Donante.objects.filter(apto_donacion=True, activo=True).count()

        # Unidades
        total_unidades = UnidadMuestra.objects.count()
        unidades_disponibles = UnidadMuestra.objects.filter(estado='DISPONIBLE').count()
        unidades_reservadas = UnidadMuestra.objects.filter(estado='RESERVADO').count()
        unidades_vencidas = UnidadMuestra.objects.filter(estado='VENCIDO').count()
        unidades_descartadas = UnidadMuestra.objects.filter(estado='DESCARTADO').count()

        # Entrevistas
        total_entrevistas = Entrevista.objects.count()
        entrevistas_aprobadas = Entrevista.objects.filter(estado='aprobada').count()
        entrevistas_rechazadas = Entrevista.objects.filter(estado='rechazada').count()

        data = {
            'total_donantes': total_donantes,
            'donantes_activos': donantes_activos,
            'donantes_aptos': donantes_aptos,
            'total_unidades': total_unidades,
            'unidades_disponibles': unidades_disponibles,
            'unidades_reservadas': unidades_reservadas,
            'unidades_vencidas': unidades_vencidas,
            'unidades_descartadas': unidades_descartadas,
            'total_entrevistas': total_entrevistas,
            'entrevistas_aprobadas': entrevistas_aprobadas,
            'entrevistas_rechazadas': entrevistas_rechazadas,
        }

        serializer = EstadisticasGeneralesSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='inventario-tipo-sangre')
    def inventario_tipo_sangre(self, request):
        """
        Inventario agrupado por tipo de sangre.
        
        GET /api/banco_sangre/reportes/inventario-tipo-sangre/
        """
        inventario = UnidadMuestra.objects.values('tipo_sangre').annotate(
            total_unidades=Count('id'),
            disponibles=Count('id', filter=Q(estado='DISPONIBLE')),
            reservadas=Count('id', filter=Q(estado='RESERVADO')),
            vencidas=Count('id', filter=Q(estado='VENCIDO')),
            descartadas=Count('id', filter=Q(estado='DESCARTADO')),
            volumen_total_ml=Sum('volumen_ml')
        ).order_by('tipo_sangre')

        serializer = InventarioTipoSangreSerializer(inventario, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='inventario-tipo-unidad')
    def inventario_tipo_unidad(self, request):
        """
        Inventario agrupado por tipo de unidad (Plasma, Paquete Globular, etc.).
        
        GET /api/banco_sangre/reportes/inventario-tipo-unidad/
        """
        inventario = UnidadMuestra.objects.values('tipo_unidad').annotate(
            total_unidades=Count('id'),
            disponibles=Count('id', filter=Q(estado='DISPONIBLE')),
            reservadas=Count('id', filter=Q(estado='RESERVADO')),
            vencidas=Count('id', filter=Q(estado='VENCIDO')),
            descartadas=Count('id', filter=Q(estado='DESCARTADO')),
            volumen_total_ml=Sum('volumen_ml')
        ).order_by('tipo_unidad')

        # Agregar display name
        tipo_unidad_dict = dict(UnidadMuestra.TIPO_UNIDAD_CHOICES)
        result = []
        for item in inventario:
            item['tipo_unidad_display'] = tipo_unidad_dict.get(item['tipo_unidad'], item['tipo_unidad'])
            result.append(item)

        serializer = InventarioTipoUnidadSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='unidades-proximas-vencer')
    def unidades_proximas_vencer(self, request):
        """
        Lista de unidades próximas a vencer (configurable).
        
        Query params:
        - dias: Número de días de anticipación (default: 7)
        
        GET /api/banco_sangre/reportes/unidades-proximas-vencer/?dias=7
        """
        dias = int(request.query_params.get('dias', 7))
        fecha_limite = timezone.now().date() + timedelta(days=dias)

        unidades = UnidadMuestra.objects.filter(
            estado__in=['DISPONIBLE', 'RESERVADO'],
            fecha_caducidad__lte=fecha_limite,
            fecha_caducidad__gte=timezone.now().date()
        ).order_by('fecha_caducidad')

        result = []
        for unidad in unidades:
            result.append({
                'id': unidad.id,
                'correlativo': unidad.correlativo,
                'tipo_unidad': unidad.get_tipo_unidad_display(),
                'tipo_sangre': unidad.tipo_sangre,
                'volumen_ml': unidad.volumen_ml,
                'fecha_caducidad': unidad.fecha_caducidad,
                'dias_restantes': unidad.dias_vigencia,
                'estado': unidad.estado,
                'localizacion': unidad.localizacion or 'No especificada'
            })

        serializer = UnidadesProximasVencerSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='donaciones-por-periodo')
    def donaciones_por_periodo(self, request):
        """
        Donaciones agrupadas por período de tiempo.
        
        Query params:
        - fecha_inicio: Fecha inicial (YYYY-MM-DD)
        - fecha_fin: Fecha final (YYYY-MM-DD)
        - agrupar_por: 'dia', 'semana', 'mes' (default: 'dia')
        
        GET /api/banco_sangre/reportes/donaciones-por-periodo/?fecha_inicio=2025-01-01&fecha_fin=2025-10-21&agrupar_por=mes
        """
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')
        agrupar_por = request.query_params.get('agrupar_por', 'dia')

        # Fechas por defecto: últimos 30 días
        if not fecha_inicio_str:
            fecha_inicio = timezone.now().date() - timedelta(days=30)
        else:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()

        if not fecha_fin_str:
            fecha_fin = timezone.now().date()
        else:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        # Agrupar por fecha de extracción
        if agrupar_por == 'mes':
            from django.db.models.functions import TruncMonth
            donaciones = UnidadMuestra.objects.filter(
                fecha_extraccion__range=[fecha_inicio, fecha_fin],
                es_transformacion=False  # Solo muestras originales
            ).annotate(
                fecha=TruncMonth('fecha_extraccion')
            ).values('fecha').annotate(
                total_donaciones=Count('donante', distinct=True),
                total_unidades_creadas=Count('id'),
                volumen_total_ml=Sum('volumen_ml')
            ).order_by('fecha')
        elif agrupar_por == 'semana':
            from django.db.models.functions import TruncWeek
            donaciones = UnidadMuestra.objects.filter(
                fecha_extraccion__range=[fecha_inicio, fecha_fin],
                es_transformacion=False
            ).annotate(
                fecha=TruncWeek('fecha_extraccion')
            ).values('fecha').annotate(
                total_donaciones=Count('donante', distinct=True),
                total_unidades_creadas=Count('id'),
                volumen_total_ml=Sum('volumen_ml')
            ).order_by('fecha')
        else:  # día
            donaciones = UnidadMuestra.objects.filter(
                fecha_extraccion__range=[fecha_inicio, fecha_fin],
                es_transformacion=False
            ).values('fecha_extraccion').annotate(
                total_donaciones=Count('donante', distinct=True),
                total_unidades_creadas=Count('id'),
                volumen_total_ml=Sum('volumen_ml')
            ).order_by('fecha_extraccion')

            # Renombrar fecha_extraccion a fecha
            result = []
            for item in donaciones:
                result.append({
                    'fecha': item['fecha_extraccion'],
                    'total_donaciones': item['total_donaciones'],
                    'total_unidades_creadas': item['total_unidades_creadas'],
                    'volumen_total_ml': item['volumen_total_ml'] or 0
                })
            serializer = DonacionesPorPeriodoSerializer(result, many=True)
            return Response(serializer.data)

        serializer = DonacionesPorPeriodoSerializer(donaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='estadisticas-donantes')
    def estadisticas_donantes(self, request):
        """
        Estadísticas demográficas de los donantes.
        
        GET /api/banco_sangre/reportes/estadisticas-donantes/
        """
        # Conteo por sexo
        sexo_masculino = Donante.objects.filter(sexo='Masculino', activo=True).count()
        sexo_femenino = Donante.objects.filter(sexo='Femenino', activo=True).count()

        # Edad promedio
        edades = Donante.objects.filter(activo=True).aggregate(
            promedio=Avg('edad'),
            minima=Min('edad'),
            maxima=Max('edad')
        )

        # Donantes activos
        total_activos = Donante.objects.filter(activo=True).count()

        # Por tipo de sangre - obtener desde las unidades de muestra
        # Agrupar por donante y tomar el tipo de sangre más reciente
        tipos_sangre = UnidadMuestra.objects.filter(
            donante__activo=True,
            donante__isnull=False
        ).values('tipo_sangre').annotate(
            total=Count('donante', distinct=True)
        ).order_by('-total')
        donantes_por_tipo_sangre = {item['tipo_sangre']: item['total'] for item in tipos_sangre}

        # Por municipio
        municipios = Donante.objects.filter(activo=True, municipio__isnull=False).values(
            'municipio__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:10]  # Top 10
        donantes_por_municipio = {item['municipio__nombre']: item['total'] for item in municipios}

        data = {
            'sexo_masculino': sexo_masculino,
            'sexo_femenino': sexo_femenino,
            'edad_promedio': round(edades['promedio'], 1) if edades['promedio'] else 0,
            'edad_minima': edades['minima'] or 0,
            'edad_maxima': edades['maxima'] or 0,
            'total_donantes_activos': total_activos,
            'donantes_por_tipo_sangre': donantes_por_tipo_sangre,
            'donantes_por_municipio': donantes_por_municipio,
        }

        serializer = EstadisticasDonanteSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='reporte-descartes')
    def reporte_descartes(self, request):
        """
        Reporte de descartes agrupados por motivo.
        
        GET /api/banco_sangre/reportes/reporte-descartes/
        """
        descartes = DescarteMuestra.objects.values(
            'motivo__nombre',
            'motivo__codigo'
        ).annotate(
            total_descartes=Count('id'),
            validados=Count('id', filter=Q(validado=True)),
            pendientes_validacion=Count('id', filter=Q(validado=False)),
        ).order_by('-total_descartes')

        # Calcular volumen descartado
        result = []
        for item in descartes:
            # Obtener IDs de muestras descartadas con este motivo
            muestras_descartadas = DescarteMuestra.objects.filter(
                motivo__nombre=item['motivo__nombre']
            ).values_list('muestra_id', flat=True)
            
            volumen_total = UnidadMuestra.objects.filter(
                id__in=muestras_descartadas
            ).aggregate(total=Sum('volumen_ml'))['total'] or 0

            result.append({
                'motivo': item['motivo__nombre'],
                'motivo_codigo': item['motivo__codigo'],
                'total_descartes': item['total_descartes'],
                'validados': item['validados'],
                'pendientes_validacion': item['pendientes_validacion'],
                'volumen_total_descartado_ml': volumen_total
            })

        serializer = ReporteDescartesSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='donantes-recurrentes')
    def donantes_recurrentes(self, request):
        """
        Lista de donantes con más de una donación.
        
        Query params:
        - min_donaciones: Mínimo de donaciones (default: 2)
        
        GET /api/banco_sangre/reportes/donantes-recurrentes/?min_donaciones=3
        """
        min_donaciones = int(request.query_params.get('min_donaciones', 2))

        # Contar unidades por donante (solo originales, no transformadas)
        donantes_data = UnidadMuestra.objects.filter(
            es_transformacion=False,
            donante__isnull=False
        ).values('donante').annotate(
            total_donaciones=Count('id'),
            ultima_donacion=Max('fecha_extraccion')
        ).filter(
            total_donaciones__gte=min_donaciones
        ).order_by('-total_donaciones')

        # Obtener datos completos del donante
        result = []
        for item in donantes_data:
            donante = Donante.objects.get(id=item['donante'])
            # Determinar tipo de sangre desde la última unidad donada
            tipo_sangre = UnidadMuestra.objects.filter(
                donante=donante,
                es_transformacion=False
            ).order_by('-fecha_extraccion').first()
            
            result.append({
                'donante_id': donante.id,
                'cui': donante.cui,
                'nombre_completo': str(donante),
                'total_donaciones': item['total_donaciones'],
                'ultima_donacion': item['ultima_donacion'],
                'tipo_sangre': tipo_sangre.tipo_sangre if tipo_sangre else 'N/A'
            })

        serializer = DonantesRecurrentesSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='salidas-por-institucion')
    def salidas_por_institucion(self, request):
        """
        Salidas agrupadas por institución/receptor.
        
        Query params:
        - fecha_inicio: Fecha inicial (YYYY-MM-DD)
        - fecha_fin: Fecha final (YYYY-MM-DD)
        
        GET /api/banco_sangre/reportes/salidas-por-institucion/?fecha_inicio=2025-01-01
        """
        fecha_inicio_str = request.query_params.get('fecha_inicio')
        fecha_fin_str = request.query_params.get('fecha_fin')

        queryset = SalidaUnidad.objects.all()

        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
            queryset = queryset.filter(fecha_salida__gte=fecha_inicio)

        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            queryset = queryset.filter(fecha_salida__lte=fecha_fin)

        salidas = queryset.values('receptor', 'medico_solicitante').annotate(
            total_salidas=Count('id'),
            total_unidades=Sum('cantidad_unidades')
        ).order_by('-total_salidas')

        # Calcular volumen total
        result = []
        for item in salidas:
            # Obtener todas las salidas de este receptor
            salidas_receptor = SalidaUnidad.objects.filter(
                receptor=item['receptor'],
                medico_solicitante=item['medico_solicitante']
            )
            
            if fecha_inicio_str:
                salidas_receptor = salidas_receptor.filter(fecha_salida__gte=fecha_inicio)
            if fecha_fin_str:
                salidas_receptor = salidas_receptor.filter(fecha_salida__lte=fecha_fin)
            
            # Obtener IDs de unidades
            detalles_ids = DetalleaSalidaUnidad.objects.filter(
                salida__in=salidas_receptor
            ).values_list('unidad_muestra_id', flat=True)
            
            volumen_total = UnidadMuestra.objects.filter(
                id__in=detalles_ids
            ).aggregate(total=Sum('volumen_ml'))['total'] or 0

            result.append({
                'receptor': item['receptor'],
                'medico_solicitante': item['medico_solicitante'],
                'total_salidas': item['total_salidas'],
                'total_unidades': item['total_unidades'] or 0,
                'volumen_total_ml': volumen_total
            })

        serializer = SalidaPorInstitucionSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='compatibilidad-sangre')
    def compatibilidad_sangre(self, request):
        """
        Análisis de compatibilidad de tipos de sangre disponibles.
        
        GET /api/banco_sangre/reportes/compatibilidad-sangre/
        """
        # Matriz de compatibilidad
        compatibilidad_matriz = {
            'O-': {'puede_donar_a': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'], 'puede_recibir_de': ['O-']},
            'O+': {'puede_donar_a': ['O+', 'A+', 'B+', 'AB+'], 'puede_recibir_de': ['O-', 'O+']},
            'A-': {'puede_donar_a': ['A-', 'A+', 'AB-', 'AB+'], 'puede_recibir_de': ['O-', 'A-']},
            'A+': {'puede_donar_a': ['A+', 'AB+'], 'puede_recibir_de': ['O-', 'O+', 'A-', 'A+']},
            'B-': {'puede_donar_a': ['B-', 'B+', 'AB-', 'AB+'], 'puede_recibir_de': ['O-', 'B-']},
            'B+': {'puede_donar_a': ['B+', 'AB+'], 'puede_recibir_de': ['O-', 'O+', 'B-', 'B+']},
            'AB-': {'puede_donar_a': ['AB-', 'AB+'], 'puede_recibir_de': ['O-', 'A-', 'B-', 'AB-']},
            'AB+': {'puede_donar_a': ['AB+'], 'puede_recibir_de': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']},
        }

        # Distribución poblacional aproximada
        distribucion_poblacional = {
            'O+': 38, 'O-': 7, 'A+': 34, 'A-': 6, 'B+': 9, 'B-': 2, 'AB+': 3, 'AB-': 1
        }

        result = []
        for tipo_sangre, info in compatibilidad_matriz.items():
            unidades_disponibles = UnidadMuestra.objects.filter(
                tipo_sangre=tipo_sangre,
                estado='DISPONIBLE'
            ).count()

            result.append({
                'tipo_sangre': tipo_sangre,
                'unidades_disponibles': unidades_disponibles,
                'puede_donar_a': info['puede_donar_a'],
                'puede_recibir_de': info['puede_recibir_de'],
                'cobertura_poblacion_pct': distribucion_poblacional.get(tipo_sangre, 0)
            })

        serializer = CompatibilidadSangreSerializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='resumen-mensual')
    def resumen_mensual(self, request):
        """
        Resumen mensual del banco de sangre.
        
        Query params:
        - año: Año (default: año actual)
        - mes: Mes 1-12 (default: mes actual)
        
        GET /api/banco_sangre/reportes/resumen-mensual/?año=2025&mes=10
        """
        año = int(request.query_params.get('año', timezone.now().year))
        mes = int(request.query_params.get('mes', timezone.now().month))

        # Rango de fechas del mes
        fecha_inicio = datetime(año, mes, 1).date()
        if mes == 12:
            fecha_fin = datetime(año + 1, 1, 1).date() - timedelta(days=1)
        else:
            fecha_fin = datetime(año, mes + 1, 1).date() - timedelta(days=1)

        # Nuevos donantes registrados
        nuevos_donantes = Donante.objects.filter(
            # Asumiendo que los donantes se crean cuando donan por primera vez
            # Si hay fecha_creacion en el modelo, usarla
        ).count()

        # Entrevistas realizadas
        entrevistas_realizadas = Entrevista.objects.filter(
            fecha__range=[fecha_inicio, fecha_fin]
        ).count()

        # Unidades creadas (solo originales)
        unidades_creadas = UnidadMuestra.objects.filter(
            fecha_extraccion__range=[fecha_inicio, fecha_fin],
            es_transformacion=False
        ).count()

        # Unidades de salida
        unidades_salida = DetalleaSalidaUnidad.objects.filter(
            salida__fecha_salida__range=[fecha_inicio, fecha_fin]
        ).count()

        # Unidades descartadas
        unidades_descartadas = DescarteMuestra.objects.filter(
            fecha_descarte__range=[fecha_inicio, fecha_fin]
        ).count()

        # Volumen total recolectado
        volumen_total = UnidadMuestra.objects.filter(
            fecha_extraccion__range=[fecha_inicio, fecha_fin],
            es_transformacion=False
        ).aggregate(total=Sum('volumen_ml'))['total'] or 0

        data = {
            'mes': fecha_inicio.strftime('%B'),
            'año': año,
            'nuevos_donantes': nuevos_donantes,
            'entrevistas_realizadas': entrevistas_realizadas,
            'unidades_creadas': unidades_creadas,
            'unidades_salida': unidades_salida,
            'unidades_descartadas': unidades_descartadas,
            'volumen_total_recolectado_ml': volumen_total
        }

        serializer = ResumenMensualSerializer(data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='alertas-inventario')
    def alertas_inventario(self, request):
        """
        Alertas del inventario (stock bajo, próximas a vencer, etc.).
        
        GET /api/banco_sangre/reportes/alertas-inventario/
        """
        alertas = []

        # Alerta 1: Unidades próximas a vencer (< 7 días)
        proximas_vencer = UnidadMuestra.objects.filter(
            estado='DISPONIBLE',
            fecha_caducidad__lte=timezone.now().date() + timedelta(days=7),
            fecha_caducidad__gte=timezone.now().date()
        ).count()

        if proximas_vencer > 0:
            alertas.append({
                'tipo_alerta': 'unidades_proximas_vencer',
                'nivel': 'advertencia',
                'mensaje': f'{proximas_vencer} unidades próximas a vencer en los próximos 7 días',
                'cantidad': proximas_vencer,
                'detalles': {'dias_limite': 7}
            })

        # Alerta 2: Stock bajo por tipo de sangre (< 5 unidades)
        tipos_sangre = UnidadMuestra.objects.filter(
            estado='DISPONIBLE'
        ).values('tipo_sangre').annotate(
            total=Count('id')
        ).filter(total__lt=5)

        for tipo in tipos_sangre:
            nivel = 'critico' if tipo['total'] < 2 else 'advertencia'
            alertas.append({
                'tipo_alerta': 'stock_bajo_tipo_sangre',
                'nivel': nivel,
                'mensaje': f'Stock bajo de tipo {tipo["tipo_sangre"]}: {tipo["total"]} unidades disponibles',
                'cantidad': tipo['total'],
                'detalles': {'tipo_sangre': tipo['tipo_sangre']}
            })

        # Alerta 3: Unidades vencidas sin descartar
        vencidas_sin_descartar = UnidadMuestra.objects.filter(
            fecha_caducidad__lt=timezone.now().date(),
            estado='DISPONIBLE'
        ).count()

        if vencidas_sin_descartar > 0:
            alertas.append({
                'tipo_alerta': 'unidades_vencidas_sin_descartar',
                'nivel': 'critico',
                'mensaje': f'{vencidas_sin_descartar} unidades vencidas que requieren descarte',
                'cantidad': vencidas_sin_descartar,
                'detalles': {}
            })

        # Alerta 4: Descartes pendientes de validación
        descartes_pendientes = DescarteMuestra.objects.filter(validado=False).count()

        if descartes_pendientes > 0:
            alertas.append({
                'tipo_alerta': 'descartes_pendientes_validacion',
                'nivel': 'info',
                'mensaje': f'{descartes_pendientes} descartes pendientes de validación',
                'cantidad': descartes_pendientes,
                'detalles': {}
            })

        serializer = AlertasInventarioSerializer(alertas, many=True)
        return Response(serializer.data)

