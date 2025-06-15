from pacientes.models import Paciente
from core.filters import BaseGenericFilterSet

class PacienteFilter(BaseGenericFilterSet):
    class Meta:
        model = Paciente
        fields = '__all__'
