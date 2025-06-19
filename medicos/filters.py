from medicos.models import Medico
from core.filters import BaseGenericFilterSet

class MedicoFilter(BaseGenericFilterSet):
    class Meta:
        model = Medico
        fields = '__all__'
