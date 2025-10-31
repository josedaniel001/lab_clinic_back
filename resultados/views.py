from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime
from .models import Resultado, ResultadoDetalle, CatalogoMotivoDenegacion, HistorialDenegacion
from .serializers import (
    ResultadoSerializer, RevertirValidacionSerializer, 
    CatalogoMotivoDenegacionSerializer, HistorialDenegacionSerializer
)
from ordenes.models import DetalleOrden, Orden
from django.template.loader import render_to_string
from weasyprint import HTML
import os
from django.conf import settings
from sistema.models import ConfiguracionLaboratorio
import base64

def get_logo_data(config, request=None):
    """Obtiene el logo del laboratorio en formato base64 o URL"""
    if not config or not getattr(config, "logo", None) or not getattr(config, "mostrar_logo", False):
        return None
    try:
        logo_data = None
        if hasattr(config.logo, 'path') and os.path.exists(config.logo.path):
            with open(config.logo.path, 'rb') as f:
                logo_data = f.read()
        if not logo_data and hasattr(config.logo, 'read'):
            try:
                config.logo.seek(0)
                logo_data = config.logo.read()
            except Exception:
                logo_data = None
        if logo_data:
            b64 = base64.b64encode(logo_data).decode('utf-8')
            ext = os.path.splitext(config.logo.name)[1].lower()
            mime = 'image/png' if ext == '.png' else 'image/gif' if ext == '.gif' else 'image/jpeg'
            return f"data:{mime};base64,{b64}"
        else:
            if request and hasattr(config.logo, 'url'):
                return request.build_absolute_uri(config.logo.url)
            elif hasattr(config.logo, 'url'):
                return f"{request.scheme}://{request.get_host()}{config.logo.url}" if request else config.logo.url
            return None
    except Exception as e:
        print(f"Error al procesar logo: {e}")
        return None

class ResultadoViewSet(viewsets.ModelViewSet):
    queryset = Resultado.objects.all().select_related(
        'resultado__orden__paciente',
        'resultado__orden__donante',
        'resultado__orden__medico',
        'resultado__examen'
    ).prefetch_related('valores')
    serializer_class = ResultadoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        detalle_orden_id = data.get("detalle_orden_id")

        if not detalle_orden_id:
            return Response({"error": "El campo 'detalle_orden_id' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            detalle = DetalleOrden.objects.get(id=detalle_orden_id)
        except DetalleOrden.DoesNotExist:
            return Response({"error": "Detalle de orden no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(detalle, "resultado"):
            return Response({"error": "Ya existe un resultado para este examen."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Solo convierte fecha_validacion si la mandas
        fecha_validacion = data.get("fecha_validacion")
        if fecha_validacion:
            if isinstance(fecha_validacion, str):
                fecha_validacion = datetime.fromisoformat(fecha_validacion).date()
            elif isinstance(fecha_validacion, datetime):
                fecha_validacion = fecha_validacion.date()

        # ⚠️ Normalmente no deberías poner fecha_validacion si el estado es EN PROCESO.
        resultado = Resultado.objects.create(
            resultado=detalle,
            observaciones=data.get("observaciones", ""),
            validado_por=data.get("validado_por", ""),            
            fecha_validacion=fecha_validacion if fecha_validacion else None,
            estado="EN PROCESO",
            prioridad=data.get("prioridad", "normal")
        )

        valores = data.get("valores", [])
        for valor in valores:
            ResultadoDetalle.objects.create(
                resultado=resultado,
                parametro=valor.get("parametro"),
                valor=valor.get("valor"),
                unidad=valor.get("unidad"),
                rango_normal=valor.get("rango_normal"),
                estado=valor.get("estado")
            )

        detalle.estado = "EN PROCESO"
        detalle.save()

        orden = detalle.orden
        if not DetalleOrden.objects.filter(orden=orden).exclude(estado="EN PROCESO").exists():
            orden.estado = "EN PROCESO"
            orden.save()

        serializer = self.get_serializer(resultado)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, url_path=r'ordenes/(?P<orden_id>\d+)/resultados', methods=['get'])
    def resultados_por_orden(self, request, orden_id=None):
        from ordenes.models import DetalleOrden

        detalle_ids = DetalleOrden.objects.filter(
            orden_id=orden_id,
            resultado__isnull=False
        ).values_list('resultado', flat=True)

        queryset = self.get_queryset().filter(id__in=detalle_ids)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'], url_path='validar')
    def validar(self, request, pk=None):
        """
        Valida resultados: actualiza detalles, estado y la relación con DetalleOrden y Orden.
        También actualiza el campo apto_donacion del donante si se proporciona.
        """
        resultados_data = request.data.get('resultados', [])
        id_usuario = request.data.get('id_usuario')

        if not resultados_data:
            return Response({"error": "No se enviaron resultados a validar."},
                            status=status.HTTP_400_BAD_REQUEST)

        from ordenes.models import DetalleOrden

        for resultado_data in resultados_data:
            resultado_id = resultado_data.get('id')
            observaciones = resultado_data.get('observaciones', '')
            valores = resultado_data.get('valores', [])
            donante_apto = resultado_data.get('donante_apto')  # Campo para aptitud del donante
            motivo_denegacion_id = resultado_data.get('motivo_denegacion_id')  # ID del motivo de denegación
            observaciones_denegacion = resultado_data.get('observaciones_denegacion', '')  # Observaciones adicionales

            try:
                resultado = Resultado.objects.get(id=resultado_id)
            except Resultado.DoesNotExist:
                print(f"❌ Resultado {resultado_id} no encontrado")
                continue

            # Debug: Imprimir estado actual
            print(f"🔍 Estado actual del resultado {resultado_id}: {resultado.estado}")

            # 1. Actualizar cada ResultadoDetalle
            resultado.valores.all().delete()  # limpia los existentes
            for valor in valores:
                ResultadoDetalle.objects.create(
                    resultado=resultado,
                    parametro=valor.get("parametro"),
                    valor=valor.get("valor"),
                    unidad=valor.get("unidad"),
                    rango_normal=valor.get("rango_normal"),
                    estado=valor.get("estado")
                )

            # 2. Actualizar Resultado - FORZAR EL CAMBIO
            resultado.observaciones = observaciones
            resultado.estado = "VALIDADO"
            resultado.validado_por = id_usuario
            resultado.fecha_validacion = timezone.now().date()
            
            # Si el donante no es apto, guardar el motivo de denegación Y crear registro de historial
            if donante_apto is False and motivo_denegacion_id:
                from .models import CatalogoMotivoDenegacion, HistorialDenegacion
                try:
                    motivo = CatalogoMotivoDenegacion.objects.get(id=motivo_denegacion_id, activo=True)
                    resultado.motivo_denegacion = motivo
                    resultado.observaciones_denegacion = observaciones_denegacion
                    print(f"✅ Motivo de denegación asignado: {motivo.nombre}")
                    
                    # Crear registro en el historial de denegaciones
                    orden = resultado.resultado.orden
                    if orden.donante:
                        # Extraer valores críticos de los valores del resultado
                        valores_criticos = {}
                        for valor in valores:
                            if valor.get('estado') in ['anormal', 'critico', 'alto', 'bajo']:
                                valores_criticos[valor.get('parametro')] = {
                                    'valor': valor.get('valor'),
                                    'unidad': valor.get('unidad'),
                                    'rango_normal': valor.get('rango_normal'),
                                    'estado': valor.get('estado')
                                }
                        
                        historial = HistorialDenegacion.objects.create(
                            donante=orden.donante,
                            resultado=resultado,
                            orden=orden,
                            motivo_denegacion=motivo,
                            observaciones=observaciones_denegacion,
                            usuario_deniego=id_usuario or 'Sistema',
                            resultado_examen=resultado.resultado.examen.nombre,
                            valores_criticos=valores_criticos
                        )
                        print(f"✅ Registro de historial de denegación creado: ID {historial.id}")
                        
                        # Si es denegación PERMANENTE, marcar al donante permanentemente
                        if motivo.tipo_denegacion == 'PERMANENTE':
                            orden.donante.denegado_permanente = True
                            orden.donante.fecha_denegacion_permanente = timezone.now()
                            orden.donante.motivo_denegacion_permanente = f"{motivo.codigo} - {motivo.nombre}"
                            orden.donante.save(update_fields=[
                                'denegado_permanente',
                                'fecha_denegacion_permanente',
                                'motivo_denegacion_permanente'
                            ])
                            print(f"🔴 Donante marcado como DENEGADO PERMANENTE: {motivo.nombre}")
                    
                except CatalogoMotivoDenegacion.DoesNotExist:
                    print(f"⚠️ Motivo de denegación con ID {motivo_denegacion_id} no encontrado o inactivo")
            
            # Limpiar motivo si el donante es apto
            if donante_apto is True:
                resultado.motivo_denegacion = None
                resultado.observaciones_denegacion = ''
            
            # Guardar y verificar inmediatamente
            resultado.save(update_fields=[
                'observaciones', 'estado', 'validado_por', 'fecha_validacion',
                'motivo_denegacion', 'observaciones_denegacion'
            ])
            
            # Debug: Verificar que se guardó
            resultado.refresh_from_db()
            print(f"✅ Estado después de guardar: {resultado.estado}")

            # 3. Actualizar DetalleOrden relacionado
            detalle = resultado.resultado  # tu FK OneToOneField
            print(f"🔍 Estado actual del detalle: {detalle.estado}")
            detalle.estado = "VALIDADO"
            detalle.save(update_fields=['estado'])

            # Debug: Verificar detalle
            detalle.refresh_from_db()
            print(f"✅ Estado del detalle después de guardar: {detalle.estado}")

            # 4. Si todos los DetalleOrden están validados, actualizar Orden
            orden = detalle.orden
            print(f"🔍 Estado actual de la orden: {orden.estado}")
            
            # Verificar si todos los detalles están validados
            detalles_pendientes = DetalleOrden.objects.filter(orden=orden).exclude(estado="VALIDADO").count()
            print(f"📊 Detalles pendientes de validar: {detalles_pendientes}")
            
            if not DetalleOrden.objects.filter(orden=orden).exclude(estado="VALIDADO").exists():
                orden.estado = "VALIDADO"
                orden.save(update_fields=['estado'])
                print(f"✅ Orden actualizada a VALIDADO")

            # 5. Actualizar apto_donacion del donante y continuar_entrevista de la orden
            if donante_apto is not None:
                # Actualizar donante si existe
                if orden.donante:
                    orden.donante.apto_donacion = donante_apto
                    orden.donante.save(update_fields=['apto_donacion'])
                    print(f"✅ Donante actualizado: apto_donacion = {donante_apto}")
                
                # Actualizar continuar_entrevista en la orden
                orden.continuar_entrevista = donante_apto
                orden.save(update_fields=['continuar_entrevista'])
                print(f"✅ Orden actualizada: continuar_entrevista = {donante_apto}")

        return Response({"message": "Resultados validados correctamente."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='verificar-estado/(?P<resultado_id>[^/.]+)')
    def verificar_estado(self, request, resultado_id=None):
        """
        Endpoint de diagnóstico para verificar el estado de un resultado.
        """
        try:
            resultado = Resultado.objects.get(id=resultado_id)
            return Response({
                "existe": True,
                "id": resultado.id,
                "estado": resultado.estado,
                "numero_orden": resultado.resultado.orden.codigo,
                "examen": resultado.resultado.examen.nombre,
                "puede_revertir": resultado.estado == 'VALIDADO',
                "fecha_validacion": resultado.fecha_validacion
            })
        except Resultado.DoesNotExist:
            return Response({
                "existe": False,
                "error": f"No se encontró el resultado con ID {resultado_id}"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='revertir-validacion')
    def revertir_validacion(self, request, pk=None):
        """
        Revierte un resultado VALIDADO a EN PROCESO para permitir edición en casos de emergencia.
        Solo puede revertirse si el resultado está actualmente VALIDADO.
        """
        print(f"🔍 DEBUG: Intentando revertir resultado con pk={pk}")
        print(f"🔍 DEBUG: Request data: {request.data}")
        
        # Verificar si el resultado existe antes de usar get_object()
        try:
            resultado = Resultado.objects.get(pk=pk)
            print(f"✅ DEBUG: Resultado encontrado - ID: {resultado.id}, Estado: {resultado.estado}")
        except Resultado.DoesNotExist:
            print(f"❌ DEBUG: Resultado con ID {pk} no existe")
            return Response(
                {"error": f"No se encontró el resultado con ID {pk}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que el resultado esté en estado VALIDADO
        if resultado.estado != 'VALIDADO':
            return Response(
                {
                    "error": f"No se puede revertir. El resultado está en estado '{resultado.estado}'. Solo se pueden revertir resultados VALIDADOS."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar datos con el serializer
        serializer = RevertirValidacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        motivo_reversion = serializer.validated_data.get('motivo_reversion', 'Reversión por emergencia')
        usuario_responsable = serializer.validated_data.get('usuario_responsable', 'Sistema')

        try:
            from ordenes.models import DetalleOrden

            # 1. Guardar información de auditoría (opcional: agregar a observaciones)
            observacion_reversion = f"\n[REVERTIDO] {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - Usuario: {usuario_responsable} - Motivo: {motivo_reversion}"
            if resultado.observaciones:
                resultado.observaciones += observacion_reversion
            else:
                resultado.observaciones = observacion_reversion

            # 2. Actualizar el resultado a EN PROCESO
            resultado.estado = 'EN PROCESO'
            # Limpiar campos de validación
            resultado.fecha_validacion = None
            resultado.validado_por = None
            
            # Guardar y verificar
            resultado.save(update_fields=['estado', 'fecha_validacion', 'validado_por', 'observaciones'])
            resultado.refresh_from_db()
            print(f"✅ Resultado {resultado.id} revertido a EN PROCESO")

            # 3. Actualizar el DetalleOrden relacionado
            detalle = resultado.resultado
            print(f"🔍 Estado actual del detalle: {detalle.estado}")
            detalle.estado = 'EN PROCESO'
            detalle.save(update_fields=['estado'])
            detalle.refresh_from_db()
            print(f"✅ DetalleOrden actualizado a EN PROCESO")

            # 4. Actualizar la Orden si es necesario
            orden = detalle.orden
            print(f"🔍 Estado actual de la orden: {orden.estado}")
            
            # Si la orden estaba VALIDADA, cambiarla a EN PROCESO
            if orden.estado == 'VALIDADO':
                orden.estado = 'EN PROCESO'
                orden.save(update_fields=['estado'])
                print(f"✅ Orden actualizada a EN PROCESO")

            # 5. Si había afectado al donante, podríamos revertirlo también (opcional)
            if orden.donante and hasattr(orden, 'continuar_entrevista'):
                # Opcional: Limpiar continuar_entrevista si fue establecido por este resultado
                print(f"ℹ️ Donante: {orden.donante.primer_nombre} {orden.donante.primer_apellido}")

            return Response({
                "mensaje": "Resultado revertido exitosamente a EN PROCESO",
                "resultado": {
                    "id": resultado.id,
                    "estado": resultado.estado,
                    "numero_orden": orden.codigo,
                    "examen": resultado.resultado.examen.nombre,
                    "fecha_reversion": timezone.now(),
                    "motivo_reversion": motivo_reversion,
                    "usuario_responsable": usuario_responsable
                },
                "detalle_orden": {
                    "id": detalle.id,
                    "estado": detalle.estado
                },
                "orden": {
                    "id": orden.id,
                    "codigo": orden.codigo,
                    "estado": orden.estado
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"⚠️ Error al revertir validación: {str(e)}")
            return Response(
                {"error": f"Error al revertir la validación: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='revertir-por-orden')
    def revertir_por_orden(self, request):
        """
        Revierte todos los resultados VALIDADOS de una orden específica.
        Recibe el ID de la orden y busca todos sus resultados asociados.
        """
        # Obtener el ID de la orden
        orden_id = request.data.get('orden_id')
        
        if not orden_id:
            return Response(
                {"error": "Se requiere 'orden_id' en el body de la petición"},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"🔍 DEBUG: Buscando resultados de la orden ID: {orden_id}")

        # Validar datos con el serializer
        serializer = RevertirValidacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        motivo_reversion = serializer.validated_data.get('motivo_reversion', 'Reversión por emergencia')
        usuario_responsable = serializer.validated_data.get('usuario_responsable', 'Sistema')

        try:
            from ordenes.models import Orden, DetalleOrden
            
            # Verificar que la orden existe
            try:
                orden = Orden.objects.get(id=orden_id)
                print(f"✅ DEBUG: Orden encontrada - Código: {orden.codigo}")
            except Orden.DoesNotExist:
                return Response(
                    {"error": f"No se encontró la orden con ID {orden_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Obtener todos los DetalleOrden de esta orden que tengan resultados
            detalles = DetalleOrden.objects.filter(orden=orden).select_related('resultado')
            print(f"📋 DEBUG: Encontrados {detalles.count()} detalles de orden")
            
            # Obtener los IDs de resultados asociados a esta orden
            resultado_ids = []
            for detalle in detalles:
                if hasattr(detalle, 'resultado'):
                    resultado_ids.append(detalle.resultado.id)
                    print(f"   • Detalle {detalle.id} → Resultado {detalle.resultado.id} (Estado: {detalle.resultado.estado})")

            if not resultado_ids:
                return Response(
                    {"error": f"La orden {orden.codigo} no tiene resultados asociados"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            print(f"🎯 DEBUG: IDs de resultados a procesar: {resultado_ids}")

            # Obtener solo los resultados VALIDADOS
            resultados_validados = Resultado.objects.filter(
                id__in=resultado_ids,
                estado='VALIDADO'
            )

            if not resultados_validados.exists():
                return Response(
                    {
                        "error": f"La orden {orden.codigo} no tiene resultados en estado VALIDADO para revertir",
                        "total_resultados": len(resultado_ids),
                        "estados": list(Resultado.objects.filter(id__in=resultado_ids).values_list('estado', flat=True))
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Revertir cada resultado validado
            resultados_revertidos = []
            resultados_fallidos = []

            for resultado in resultados_validados:
                try:
                    # Guardar información de auditoría
                    observacion_reversion = f"\n[REVERTIDO] {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - Usuario: {usuario_responsable} - Motivo: {motivo_reversion}"
                    if resultado.observaciones:
                        resultado.observaciones += observacion_reversion
                    else:
                        resultado.observaciones = observacion_reversion

                    # Actualizar el resultado a EN PROCESO
                    resultado.estado = 'EN PROCESO'
                    resultado.fecha_validacion = None
                    resultado.validado_por = None
                    resultado.save(update_fields=['estado', 'fecha_validacion', 'validado_por', 'observaciones'])
                    resultado.refresh_from_db()

                    # Actualizar el DetalleOrden relacionado
                    detalle = resultado.resultado
                    detalle.estado = 'EN PROCESO'
                    detalle.save(update_fields=['estado'])

                    resultados_revertidos.append({
                        "id": resultado.id,
                        "examen": resultado.resultado.examen.nombre,
                        "estado": resultado.estado
                    })
                    
                    print(f"✅ Resultado {resultado.id} ({resultado.resultado.examen.nombre}) revertido exitosamente")

                except Exception as e:
                    resultados_fallidos.append({
                        "id": resultado.id,
                        "error": str(e)
                    })
                    print(f"⚠️ Error al revertir resultado {resultado.id}: {str(e)}")

            # Actualizar el estado de la orden si todos los resultados fueron revertidos
            if orden.estado == 'VALIDADO' and resultados_revertidos:
                orden.estado = 'EN PROCESO'
                orden.save(update_fields=['estado'])
                print(f"✅ Orden {orden.codigo} actualizada a EN PROCESO")

            return Response({
                "mensaje": f"Proceso de reversión completado para la orden {orden.codigo}",
                "orden": {
                    "id": orden.id,
                    "codigo": orden.codigo,
                    "estado": orden.estado
                },
                "resultados_revertidos": resultados_revertidos,
                "resultados_fallidos": resultados_fallidos,
                "total_revertidos": len(resultados_revertidos),
                "total_fallidos": len(resultados_fallidos),
                "motivo_reversion": motivo_reversion,
                "usuario_responsable": usuario_responsable
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"⚠️ Error general al revertir por orden: {str(e)}")
            return Response(
                {"error": f"Error al procesar la orden: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='revertir-multiples-ordenes')
    def revertir_multiples_ordenes(self, request):
        """
        Revierte todos los resultados VALIDADOS de múltiples órdenes.
        Recibe una lista de IDs de órdenes y procesa cada una.
        """
        # Obtener la lista de IDs de órdenes
        orden_ids = request.data.get('orden_ids', [])
        
        if not orden_ids:
            return Response(
                {"error": "Se requiere 'orden_ids' (lista de IDs) en el body de la petición"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(orden_ids, list):
            return Response(
                {"error": "'orden_ids' debe ser una lista de IDs"},
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"🔍 DEBUG: Procesando {len(orden_ids)} órdenes para reversión")

        # Validar datos con el serializer
        serializer = RevertirValidacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        motivo_reversion = serializer.validated_data.get('motivo_reversion', 'Reversión por emergencia')
        usuario_responsable = serializer.validated_data.get('usuario_responsable', 'Sistema')

        from ordenes.models import Orden, DetalleOrden

        ordenes_procesadas = []
        ordenes_fallidas = []
        total_resultados_revertidos = 0

        # Procesar cada orden
        for orden_id in orden_ids:
            try:
                print(f"\n📋 Procesando orden ID: {orden_id}")
                
                # Verificar que la orden existe
                try:
                    orden = Orden.objects.get(id=orden_id)
                    print(f"✅ Orden encontrada: {orden.codigo}")
                except Orden.DoesNotExist:
                    ordenes_fallidas.append({
                        "orden_id": orden_id,
                        "error": f"No se encontró la orden con ID {orden_id}"
                    })
                    print(f"❌ Orden {orden_id} no encontrada")
                    continue

                # Obtener todos los DetalleOrden de esta orden
                detalles = DetalleOrden.objects.filter(orden=orden).select_related('resultado')
                
                # Obtener los IDs de resultados asociados a esta orden
                resultado_ids = []
                for detalle in detalles:
                    if hasattr(detalle, 'resultado'):
                        resultado_ids.append(detalle.resultado.id)

                if not resultado_ids:
                    ordenes_fallidas.append({
                        "orden_id": orden_id,
                        "codigo": orden.codigo,
                        "error": "No tiene resultados asociados"
                    })
                    print(f"⚠️ Orden {orden.codigo} sin resultados")
                    continue

                # Obtener solo los resultados VALIDADOS
                resultados_validados = Resultado.objects.filter(
                    id__in=resultado_ids,
                    estado='VALIDADO'
                )

                if not resultados_validados.exists():
                    ordenes_fallidas.append({
                        "orden_id": orden_id,
                        "codigo": orden.codigo,
                        "error": "No tiene resultados en estado VALIDADO"
                    })
                    print(f"⚠️ Orden {orden.codigo} sin resultados validados")
                    continue

                # Revertir cada resultado validado
                resultados_revertidos = []
                for resultado in resultados_validados:
                    try:
                        # Guardar información de auditoría
                        observacion_reversion = f"\n[REVERTIDO] {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - Usuario: {usuario_responsable} - Motivo: {motivo_reversion}"
                        if resultado.observaciones:
                            resultado.observaciones += observacion_reversion
                        else:
                            resultado.observaciones = observacion_reversion

                        # Actualizar el resultado a EN PROCESO
                        resultado.estado = 'EN PROCESO'
                        resultado.fecha_validacion = None
                        resultado.validado_por = None
                        resultado.save(update_fields=['estado', 'fecha_validacion', 'validado_por', 'observaciones'])

                        # Actualizar el DetalleOrden relacionado
                        detalle = resultado.resultado
                        detalle.estado = 'EN PROCESO'
                        detalle.save(update_fields=['estado'])

                        resultados_revertidos.append({
                            "id": resultado.id,
                            "examen": resultado.resultado.examen.nombre
                        })
                        
                    except Exception as e:
                        print(f"⚠️ Error al revertir resultado {resultado.id}: {str(e)}")

                # Actualizar el estado de la orden
                if orden.estado == 'VALIDADO' and resultados_revertidos:
                    orden.estado = 'EN PROCESO'
                    orden.save(update_fields=['estado'])

                # Agregar a procesadas
                ordenes_procesadas.append({
                    "orden_id": orden.id,
                    "codigo": orden.codigo,
                    "estado": orden.estado,
                    "resultados_revertidos": len(resultados_revertidos),
                    "examenes": [r["examen"] for r in resultados_revertidos]
                })
                
                total_resultados_revertidos += len(resultados_revertidos)
                print(f"✅ Orden {orden.codigo}: {len(resultados_revertidos)} resultado(s) revertido(s)")

            except Exception as e:
                ordenes_fallidas.append({
                    "orden_id": orden_id,
                    "error": str(e)
                })
                print(f"❌ Error procesando orden {orden_id}: {str(e)}")

        return Response({
            "mensaje": f"Proceso completado. {len(ordenes_procesadas)} orden(es) procesada(s), {total_resultados_revertidos} resultado(s) revertido(s).",
            "ordenes_procesadas": ordenes_procesadas,
            "ordenes_fallidas": ordenes_fallidas,
            "total_ordenes_procesadas": len(ordenes_procesadas),
            "total_ordenes_fallidas": len(ordenes_fallidas),
            "total_resultados_revertidos": total_resultados_revertidos,
            "motivo_reversion": motivo_reversion,
            "usuario_responsable": usuario_responsable
        }, status=status.HTTP_200_OK if ordenes_procesadas else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='revertir-validacion-multiple')
    def revertir_validacion_multiple(self, request):
        """
        Revierte múltiples resultados VALIDADOS a EN PROCESO para permitir edición en casos de emergencia.
        Acepta una lista de IDs de resultados a revertir.
        """
        # Validar datos con el serializer
        serializer = RevertirValidacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        motivo_reversion = serializer.validated_data.get('motivo_reversion', 'Reversión por emergencia')
        usuario_responsable = serializer.validated_data.get('usuario_responsable', 'Sistema')
        
        # Obtener IDs de resultados a revertir
        resultado_ids = request.data.get('resultado_ids', [])
        
        if not resultado_ids:
            return Response(
                {"error": "Se requiere una lista de 'resultado_ids' para revertir"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(resultado_ids, list):
            return Response(
                {"error": "'resultado_ids' debe ser una lista de IDs"},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultados_revertidos = []
        resultados_fallidos = []
        ordenes_actualizadas = set()

        for resultado_id in resultado_ids:
            try:
                resultado = Resultado.objects.get(id=resultado_id)
                
                # Validar que el resultado esté en estado VALIDADO
                if resultado.estado != 'VALIDADO':
                    resultados_fallidos.append({
                        "id": resultado_id,
                        "error": f"El resultado está en estado '{resultado.estado}', no puede ser revertido"
                    })
                    continue

                from ordenes.models import DetalleOrden

                # 1. Guardar información de auditoría
                observacion_reversion = f"\n[REVERTIDO] {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} - Usuario: {usuario_responsable} - Motivo: {motivo_reversion}"
                if resultado.observaciones:
                    resultado.observaciones += observacion_reversion
                else:
                    resultado.observaciones = observacion_reversion

                # 2. Actualizar el resultado a EN PROCESO
                resultado.estado = 'EN PROCESO'
                resultado.fecha_validacion = None
                resultado.validado_por = None
                resultado.save(update_fields=['estado', 'fecha_validacion', 'validado_por', 'observaciones'])
                resultado.refresh_from_db()

                # 3. Actualizar el DetalleOrden relacionado
                detalle = resultado.resultado
                detalle.estado = 'EN PROCESO'
                detalle.save(update_fields=['estado'])

                # 4. Actualizar la Orden si es necesario
                orden = detalle.orden
                if orden.estado == 'VALIDADO':
                    orden.estado = 'EN PROCESO'
                    orden.save(update_fields=['estado'])
                    ordenes_actualizadas.add(orden.codigo)

                resultados_revertidos.append({
                    "id": resultado.id,
                    "numero_orden": orden.codigo,
                    "examen": resultado.resultado.examen.nombre,
                    "estado": resultado.estado
                })
                
                print(f"✅ Resultado {resultado.id} revertido exitosamente")

            except Resultado.DoesNotExist:
                resultados_fallidos.append({
                    "id": resultado_id,
                    "error": "Resultado no encontrado"
                })
            except Exception as e:
                resultados_fallidos.append({
                    "id": resultado_id,
                    "error": str(e)
                })
                print(f"⚠️ Error al revertir resultado {resultado_id}: {str(e)}")

        return Response({
            "mensaje": f"Proceso de reversión completado. {len(resultados_revertidos)} resultados revertidos exitosamente.",
            "resultados_revertidos": resultados_revertidos,
            "resultados_fallidos": resultados_fallidos,
            "total_revertidos": len(resultados_revertidos),
            "total_fallidos": len(resultados_fallidos),
            "ordenes_actualizadas": list(ordenes_actualizadas),
            "motivo_reversion": motivo_reversion,
            "usuario_responsable": usuario_responsable
        }, status=status.HTTP_200_OK if resultados_revertidos else status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='generar-pdf-orden')
    def generar_pdf_orden(self, request):
        """
        Genera un PDF de resultados para una orden con datos EDITABLES.
        Permite modificar cualquier dato antes de generar el PDF.
        NUEVA FUNCIONALIDAD: Cambia automáticamente el doctor en la BD cuando se envía información del doctor.
        
        Body esperado:
        {
            "orden_id": 123,  // ID de la orden (requerido para cambio automático de médico)
            "datos": {  // Datos editables (opcional, se obtienen de la BD si no se envían)
                "orden_codigo": "ORD-001",
                "fecha_orden": "2025-01-15",
                "estado": "VALIDADO",
                "prioridad": "normal",
                "tipo_paciente": "donante",
                "paciente_nombre": "Juan Pérez",
                "paciente_documento": "1234567890",
                "paciente_edad": "35",
                "paciente_sexo": "Masculino",
                "medico_nombre": "Dr. María López",  // NUEVO: Cambia automáticamente el médico en la BD
                "medico_id": 456,  // NUEVO: Alternativa por ID del médico
                "examenes": [
                    {
                        "nombre": "Hemograma Completo",
                        "valores": [
                            {
                                "parametro": "Hemoglobina",
                                "valor": "15.5",
                                "unidad": "g/dL",
                                "rango_normal": "13-17",
                                "estado": "normal"
                            }
                        ],
                        "observaciones": "Valores dentro de lo normal",
                        "fecha_resultado": "2025-01-15",
                        "fecha_validacion": "2025-01-15",
                        "validado_por": "Dr. Carlos Méndez"
                    }
                ],
                "observaciones_generales": "Todos los exámenes dentro de rangos normales",
                "notas_importantes": "",
                "responsable_laboratorio": "Lic. Ana García",
                "validador": "Dr. Carlos Méndez",
                "fecha_validacion": "2025-01-15"
            }
        }
        
        FUNCIONALIDAD AUTOMÁTICA:
        - Si se envía 'medico_nombre' o 'medico_id' en datos, automáticamente cambia el médico en la BD
        - Busca el médico por ID (prioridad) o por nombre
        - Actualiza la orden con el nuevo médico antes de generar el PDF
        """
        print("📄 Iniciando generación de PDF de resultados")
        
        # Obtener orden_id si se proporciona
        orden_id = request.data.get('orden_id')
        datos_custom = request.data.get('datos', {})
        
        # Variable para almacenar la orden si se necesita cambiar el médico
        orden_actualizada = None
        
        # Si se proporciona orden_id, obtener datos de la BD
        if orden_id:
            try:
                orden = Orden.objects.get(id=orden_id)
                print(f"✅ Orden encontrada: {orden.codigo}")
                
                # NUEVA FUNCIONALIDAD: Cambiar médico automáticamente si se detecta en datos_custom
                if datos_custom:
                    try:
                        from medicos.models import Medico
                        nuevo_medico = None
                        
                        # Opción 1: Buscar por ID del médico si se proporciona
                        if 'medico_id' in datos_custom and datos_custom['medico_id']:
                            try:
                                nuevo_medico = Medico.objects.get(id=datos_custom['medico_id'])
                                print(f"🔍 Médico encontrado por ID: {nuevo_medico}")
                            except Medico.DoesNotExist:
                                print(f"⚠️ No se encontró médico con ID: {datos_custom['medico_id']}")
                        
                        # Opción 2: Buscar por nombre si no se encontró por ID
                        elif 'medico_nombre' in datos_custom and datos_custom['medico_nombre']:
                            medico_nombre = datos_custom.get('medico_nombre', '')
                            if medico_nombre and medico_nombre != str(orden.medico):
                                # Limpiar el nombre (quitar "Dr.", "Dra.", etc.)
                                nombre_limpio = medico_nombre.replace('Dr.', '').replace('Dra.', '').strip()
                                partes_nombre = nombre_limpio.split()
                                
                                if len(partes_nombre) >= 2:
                                    # Buscar por nombre y apellido
                                    medicos = Medico.objects.filter(
                                        nombres__icontains=partes_nombre[0],
                                        apellidos__icontains=partes_nombre[1]
                                    )
                                else:
                                    # Buscar solo por nombre
                                    medicos = Medico.objects.filter(
                                        nombres__icontains=partes_nombre[0]
                                    )
                                
                                if medicos.exists():
                                    nuevo_medico = medicos.first()
                                    print(f"🔍 Médico encontrado por nombre: {nuevo_medico}")
                        
                        # Si se encontró un nuevo médico, actualizar la orden
                        if nuevo_medico and nuevo_medico != orden.medico:
                            # Guardar el médico anterior para posible rollback
                            medico_anterior = orden.medico
                            medico_anterior_nombre = str(medico_anterior) if medico_anterior else "Sin asignar"
                            
                            # Actualizar el médico en la orden
                            orden.medico = nuevo_medico
                            orden.save()
                            orden_actualizada = orden
                            
                            print(f"✅ Médico cambiado automáticamente de '{medico_anterior_nombre}' a '{nuevo_medico}' en la orden {orden.codigo}")
                        elif nuevo_medico == orden.medico:
                            print(f"ℹ️ El médico ya está asignado correctamente: {nuevo_medico}")
                            
                    except Exception as e:
                        print(f"⚠️ Error al cambiar médico automáticamente: {str(e)}")
                        # No fallar el proceso, solo registrar el error
                
                # Si hay datos personalizados, complementar con datos de la orden
                if datos_custom:
                    # Obtener datos completos de la orden
                    datos_orden = self._construir_datos_desde_orden(orden)
                    
                    # Mantener solo los campos específicos que se enviaron en datos_custom
                    # y complementar con los datos de la orden para evitar N/A
                    datos_completos = datos_orden.copy()
                    datos_completos.update(datos_custom)  # Los datos personalizados sobrescriben los de la orden
                    datos_custom = datos_completos
                else:
                    # Si no hay datos personalizados, construir desde la orden
                    datos_custom = self._construir_datos_desde_orden(orden)
                
            except Orden.DoesNotExist:
                return Response(
                    {"error": f"No se encontró la orden con ID {orden_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Validar que tengamos datos para generar el PDF
        if not datos_custom:
            return Response(
                {"error": "Se requiere 'orden_id' o 'datos' personalizados para generar el PDF"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Agregar fecha de generación
            datos_custom['fecha_generacion'] = timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Asegurar que orden_codigo esté presente para el template
            if 'orden_codigo' not in datos_custom and orden_id:
                try:
                    orden = Orden.objects.get(id=orden_id)
                    datos_custom['orden_codigo'] = orden.codigo
                except Orden.DoesNotExist:
                    datos_custom['orden_codigo'] = "N/A"
            
            # Obtener configuración del laboratorio
            config = ConfiguracionLaboratorio.objects.first()
            logo_data = get_logo_data(config, request)
            
            # Renderizar template
            html_string = render_to_string(
                'banco_sangre/resultado_pdf.html',
                {
                    'datos': datos_custom,
                    'config': config,
                    'logo_data': logo_data
                }
            )
            
            # Crear directorio para PDFs
            pdf_dir = os.path.join(settings.MEDIA_ROOT, 'resultados_pdf')
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Generar nombre de archivo
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            orden_codigo = datos_custom.get('orden_codigo', 'SIN_CODIGO').replace('/', '_')
            pdf_filename = f'resultado_{orden_codigo}_{timestamp}.pdf'
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            # Generar PDF
            HTML(string=html_string, base_url=None).write_pdf(
                pdf_path,
                optimize_size=('fonts', 'images'),
                font_config=None
            )
            
            print(f"✅ PDF generado: {pdf_path}")
            
            # Construir URL
            file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}resultados_pdf/{pdf_filename}')
            
            # Preparar respuesta con información del cambio de médico
            respuesta = {
                "mensaje": "PDF generado exitosamente",
                "pdf_url": file_url,
                "archivo": pdf_filename,
                "datos_utilizados": datos_custom
            }
            
            # NUEVA FUNCIONALIDAD: Agregar información del cambio de médico si se realizó
            if orden_actualizada:
                respuesta["cambio_medico"] = {
                    "realizado": True,
                    "orden_id": orden_actualizada.id,
                    "orden_codigo": orden_actualizada.codigo,
                    "nuevo_medico_nombre": str(orden_actualizada.medico) if orden_actualizada.medico else "Sin asignar",
                    "mensaje": f"Médico actualizado exitosamente en la orden {orden_actualizada.codigo}"
                }
            
            return Response(respuesta, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error generando PDF: {str(e)}")
            return Response(
                {"error": f"Error al generar el PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _construir_datos_desde_orden(self, orden):
        """Construye el diccionario de datos desde una orden de la BD"""
        # Información básica de la orden
        datos = {
            "orden_codigo": orden.codigo,
            "fecha_orden": orden.fecha.strftime('%d/%m/%Y'),
            "estado": orden.estado,
            "prioridad": "normal",  # Puedes ajustar según tu modelo
        }
        
        # Información del paciente/donante
        if orden.donante:
            # Obtener el código del donante para esta orden
            from banco_sangre.models import CodigoDonante
            try:
                codigo_donante = CodigoDonante.objects.filter(
                    orden=orden,
                    donante=orden.donante,
                    activo=True
                ).first()
                codigo_donante_str = codigo_donante.codigo if codigo_donante else orden.codigo
            except:
                codigo_donante_str = orden.codigo
            
            datos.update({
                "tipo_paciente": "donante",
                "codigo_donante": codigo_donante_str,  # 👈 Nuevo campo
                "paciente_nombre": f"{orden.donante.primer_nombre} {orden.donante.primer_apellido}",
                "paciente_documento": orden.donante.cui,
                "paciente_edad": orden.donante.edad if hasattr(orden.donante, 'edad') else None,
                "paciente_sexo": orden.donante.sexo if hasattr(orden.donante, 'sexo') else None,
                "paciente_telefono": orden.donante.celular if hasattr(orden.donante, 'celular') else None,
                "paciente_direccion": orden.donante.direccion if hasattr(orden.donante, 'direccion') else None,
            })
        elif orden.paciente:
            datos.update({
                "tipo_paciente": "paciente",
                "paciente_nombre": f"{orden.paciente.nombres} {orden.paciente.apellidos}",
                "paciente_documento": orden.paciente.numero_documento,
                "paciente_edad": orden.paciente.edad if hasattr(orden.paciente, 'edad') else None,
                "paciente_sexo": orden.paciente.sexo if hasattr(orden.paciente, 'sexo') else None,
            })
        
        # Información del médico
        if orden.medico:
            datos.update({
                "medico_nombre": f"{orden.medico.nombres} {orden.medico.apellidos}",
                "medico_colegiado": orden.medico.colegiado if hasattr(orden.medico, 'colegiado') else None,
            })
        
        # Obtener todos los resultados de la orden
        detalles = DetalleOrden.objects.filter(orden=orden).select_related('examen', 'resultado')
        
        examenes = []
        for detalle in detalles:
            if hasattr(detalle, 'resultado'):
                resultado = detalle.resultado
                
                # Obtener valores del resultado
                valores = []
                for valor in resultado.valores.all():
                    valores.append({
                        "parametro": valor.parametro,
                        "valor": valor.valor,
                        "unidad": valor.unidad,
                        "rango_normal": valor.rango_normal,
                        "estado": valor.estado
                    })
                
                examenes.append({
                    "nombre": detalle.examen.nombre,
                    "valores": valores,
                    "observaciones": resultado.observaciones or "",
                    "fecha_resultado": resultado.fecha_resultado.strftime('%d/%m/%Y') if resultado.fecha_resultado else None,
                    "fecha_validacion": resultado.fecha_validacion.strftime('%d/%m/%Y') if resultado.fecha_validacion else None,
                    "validado_por": resultado.validado_por or ""
                })
        
        datos["examenes"] = examenes
        datos["observaciones_generales"] = datos.get("observaciones_generales", "")
        datos["notas_importantes"] = datos.get("notas_importantes", "")
        datos["responsable_laboratorio"] = datos.get("responsable_laboratorio", "")
        datos["validador"] = datos.get("validador", "")
        datos["fecha_validacion"] = datos.get("fecha_validacion", timezone.now().strftime('%d/%m/%Y'))
        
        # Asegurar campos adicionales que el template necesita
        datos["fecha_orden"] = datos.get("fecha_orden", orden.fecha.strftime('%d/%m/%Y'))
        datos["paciente_edad"] = datos.get("paciente_edad", "N/A")
        datos["paciente_sexo"] = datos.get("paciente_sexo", "N/A")
        datos["paciente_documento"] = datos.get("paciente_documento", "N/A")
        datos["medico_nombre"] = datos.get("medico_nombre", "N/A")
        datos["estado_orden"] = datos.get("estado_orden", orden.estado)
        
        return datos

    @action(detail=False, methods=['post'], url_path='revertir-cambio-medico')
    def revertir_cambio_medico(self, request):
        """
        Revierte el cambio de médico en una orden específica.
        Útil si se cambió el médico por error al generar el PDF.
        
        Body esperado:
        {
            "orden_id": 123,
            "medico_anterior_id": 456  // ID del médico anterior a restaurar
        }
        """
        orden_id = request.data.get('orden_id')
        medico_anterior_id = request.data.get('medico_anterior_id')
        
        if not orden_id:
            return Response(
                {"error": "Se requiere 'orden_id' para revertir el cambio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            orden = Orden.objects.get(id=orden_id)
            
            if medico_anterior_id:
                from medicos.models import Medico
                medico_anterior = Medico.objects.get(id=medico_anterior_id)
                orden.medico = medico_anterior
            else:
                orden.medico = None
            
            orden.save()
            
            return Response({
                "mensaje": f"Médico revertido exitosamente en la orden {orden.codigo}",
                "orden_id": orden.id,
                "orden_codigo": orden.codigo,
                "medico_actual": str(orden.medico) if orden.medico else "Sin asignar"
            }, status=status.HTTP_200_OK)
            
        except Orden.DoesNotExist:
            return Response(
                {"error": f"No se encontró la orden con ID {orden_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Medico.DoesNotExist:
            return Response(
                {"error": f"No se encontró el médico con ID {medico_anterior_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al revertir el cambio de médico: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CatalogoMotivoDenegacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el catálogo de motivos de denegación
    """
    queryset = CatalogoMotivoDenegacion.objects.all().order_by('codigo')
    serializer_class = CatalogoMotivoDenegacionSerializer
    
    def get_queryset(self):
        """Filtrar solo motivos activos por defecto"""
        queryset = super().get_queryset()
        incluir_inactivos = self.request.query_params.get('incluir_inactivos', 'false').lower() == 'true'
        
        if not incluir_inactivos:
            queryset = queryset.filter(activo=True)
        
        return queryset


class HistorialDenegacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para consultar el historial de denegaciones.
    Las denegaciones se crean automáticamente al validar resultados.
    """
    queryset = HistorialDenegacion.objects.select_related(
        'donante',
        'resultado',
        'orden',
        'motivo_denegacion'
    ).all().order_by('-fecha_denegacion')
    serializer_class = HistorialDenegacionSerializer
    
    def get_queryset(self):
        """Filtrar por donante, orden o motivo si se proporciona"""
        queryset = super().get_queryset()
        
        # Filtrar por donante
        donante_id = self.request.query_params.get('donante_id')
        if donante_id:
            queryset = queryset.filter(donante_id=donante_id)
        
        # Filtrar por orden
        orden_id = self.request.query_params.get('orden_id')
        if orden_id:
            queryset = queryset.filter(orden_id=orden_id)
        
        # Filtrar por motivo
        motivo_id = self.request.query_params.get('motivo_id')
        if motivo_id:
            queryset = queryset.filter(motivo_denegacion_id=motivo_id)
        
        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            from datetime import datetime
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            queryset = queryset.filter(fecha_denegacion__gte=fecha_desde_dt)
        
        if fecha_hasta:
            from datetime import datetime
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            queryset = queryset.filter(fecha_denegacion__lte=fecha_hasta_dt)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Estadísticas del historial de denegaciones
        """
        from django.db.models import Count
        
        # Total de denegaciones
        total_denegaciones = self.get_queryset().count()
        
        # Denegaciones por motivo
        por_motivo = self.get_queryset().values(
            'motivo_denegacion__codigo',
            'motivo_denegacion__nombre'
        ).annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Donantes con más denegaciones
        donantes_frecuentes = self.get_queryset().values(
            'donante__id',
            'donante__cui',
            'donante__primer_nombre',
            'donante__primer_apellido'
        ).annotate(
            total_denegaciones=Count('id')
        ).order_by('-total_denegaciones')[:10]
        
        # Denegaciones por mes (últimos 12 meses)
        from django.db.models.functions import TruncMonth
        por_mes = self.get_queryset().annotate(
            mes=TruncMonth('fecha_denegacion')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('-mes')[:12]
        
        return Response({
            'total_denegaciones': total_denegaciones,
            'denegaciones_por_motivo': list(por_motivo),
            'donantes_frecuentes': list(donantes_frecuentes),
            'denegaciones_por_mes': list(por_mes)
        })