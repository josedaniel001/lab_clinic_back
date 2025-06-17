from rest_framework import viewsets
from .models import Pais, Departamento, Municipio
from .serializers import PaisSerializer, DepartamentoSerializer, MunicipioSerializer

class PaisViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pais.objects.all()
    serializer_class = PaisSerializer

class DepartamentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Departamento.objects.select_related('pais').all()
    serializer_class = DepartamentoSerializer

class MunicipioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipio.objects.select_related('departamento__pais').all()
    serializer_class = MunicipioSerializer
