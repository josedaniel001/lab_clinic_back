from rest_framework  import viewsets
from .models import Resultado
from rest_framework.response import Response
from .serializers import ResultadoSerializer
from rest_framework.decorators import action

class ResultadoViewSet(viewsets.ModelViewSet):
    queryset = Resultado.objects.all().select_related(
        'resultado__orden__paciente',
        'resultado__orden__medico',
        'resultado__examen'
    ).prefetch_related('valores')
    serializer_class = ResultadoSerializer
    
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