from rest_framework import viewsets
from .models import Paciente
from .serializers import PacienteSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import PacienteFilter

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteFilter
