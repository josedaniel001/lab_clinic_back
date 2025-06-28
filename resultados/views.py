from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Resultado, ResultadoDetalle
from .serializers import ResultadoSerializer
from ordenes.models import DetalleOrden

class ResultadoViewSet(viewsets.ModelViewSet):
    queryset = Resultado.objects.all().select_related(
        'resultado__orden__paciente',
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

        # Crear resultado
        resultado = Resultado.objects.create(
            resultado=detalle,
            observaciones=data.get("observaciones", ""),
            validado_por=data.get("validado_por", ""),            
            fecha_validacion=data.get("fecha_validacion"),
            estado=data.get("estado", "PENDIENTE"),
            prioridad=data.get("prioridad", "normal")
        )

        # Crear detalles
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
