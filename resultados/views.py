from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime
from .models import Resultado, ResultadoDetalle
from .serializers import ResultadoSerializer
from ordenes.models import DetalleOrden

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
            donante_apto = resultado_data.get('donante_apto')  # Nuevo campo

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
            
            # Guardar y verificar inmediatamente
            resultado.save(update_fields=['observaciones', 'estado', 'validado_por', 'fecha_validacion'])
            
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
