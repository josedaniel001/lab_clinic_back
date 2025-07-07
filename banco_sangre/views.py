# banco_sangre/views.py

from rest_framework import viewsets
from .models import Donante, MuestraSangre, Entrevista, UnidadMuestra
from .serializers import DonanteSerializer, MuestraSangreSerializer, EntrevistaSerializer, UnidadMuestraSerializer

class DonanteViewSet(viewsets.ModelViewSet):
    queryset = Donante.objects.all()
    serializer_class = DonanteSerializer

class MuestraSangreViewSet(viewsets.ModelViewSet):
    queryset = MuestraSangre.objects.all()
    serializer_class = MuestraSangreSerializer

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