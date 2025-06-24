from examenes.models import Examen
from core.filters import BaseGenericFilterSet

class ExamenesFilter(BaseGenericFilterSet):
    class Meta:
        model = Examen
        fields = '__all__'
