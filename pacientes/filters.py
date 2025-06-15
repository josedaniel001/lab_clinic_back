import django_filters
from .models import Paciente

class PacienteFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    correo = django_filters.CharFilter(lookup_expr='icontains')
    procedencia = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Paciente
        fields = {
            'nombre': ['icontains'],
            'edad': ['exact'],
            'sexo': ['exact'],
            'celular': ['icontains'],
            'correo': ['icontains'],
            'procedencia': ['icontains'],
        }
