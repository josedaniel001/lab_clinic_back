from ordenes.models import Orden
from core.filters import BaseGenericFilterSet

class OrdenesFilter(BaseGenericFilterSet):
    class Meta:
        model = Orden
        fields = '__all__'
