# banco_sangre/views.py

from rest_framework import viewsets,status
from .models import Donante, Entrevista, UnidadMuestra,Lote
from .serializers import DonanteSerializer,  EntrevistaSerializer, UnidadMuestraSerializer, LoteSerializer
from rest_framework.response import Response

class DonanteViewSet(viewsets.ModelViewSet):
    queryset = Donante.objects.all()
    serializer_class = DonanteSerializer


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer
# banco_sangre/views.py

class EntrevistaViewSet(viewsets.ModelViewSet):
    queryset = Entrevista.objects.select_related(
        'donante', 'orden'
    ).prefetch_related(
        'orden__detalleorden_set',
        'orden__detalleorden_set__examen'
    )
    serializer_class = EntrevistaSerializer

class UnidadMuestraViewSet(viewsets.ModelViewSet):
    queryset = UnidadMuestra.objects.all()
    serializer_class = UnidadMuestraSerializer

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        unidades = serializer.save()

        # Refrescar para cada unidad (correlativo)
        if is_many:
            for unidad in unidades:
                unidad.refresh_from_db()
        else:
            unidades.refresh_from_db()

        response_serializer = self.get_serializer(unidades, many=is_many)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)