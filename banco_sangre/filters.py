from .models import Donante, UnidadMuestra, Lote, Entrevista
from core.filters import BaseGenericFilterSet
import django_filters

class UnidadMuestraFilter(BaseGenericFilterSet):
    exclude_estado = django_filters.CharFilter(method='filter_exclude_estado')
    def filter_exclude_estado(self, queryset, name, value):
        valores = [v.strip() for v in value.split(",")]
        return queryset.exclude(estado__in=valores)
    class Meta:
        model = UnidadMuestra
        exclude = ['serologias']

class DonanteFilter(BaseGenericFilterSet):
    class Meta:
        model = Donante
        fields = '__all__'

class LoteFilter(BaseGenericFilterSet):
    class Meta:
        model = Lote
        fields = '__all__'

class EntrevistaFilter(BaseGenericFilterSet):
    class Meta:
        model = Entrevista
        exclude = ['respuestas_entrevista','respuestas_adicionales_entrevista','respuestas_medicas_adicionales','respuestas_mujeres','pdf_entrevista']
