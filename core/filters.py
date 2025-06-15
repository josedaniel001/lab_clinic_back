import django_filters
from django.db import models


class BaseGenericFilterSet(django_filters.FilterSet):
    """
    Filtro dinámico que agrega automáticamente:
    - Filtros exactos para todos los campos
    - Filtros 'icontains' para campos de texto
    - Filtros de rango (gte, lte) para campos de fecha y datetime
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        model = self.Meta.model

        for field in model._meta.get_fields():
            field_name = field.name

            # Ignorar relaciones reversas y campos no concretos
            if field.auto_created and not field.concrete:
                continue

            # Evita duplicar filtros
            if field_name in self.filters:
                continue

            # Filtro exacto por defecto
            self.filters[field_name] = django_filters.CharFilter(field_name=field_name, lookup_expr='exact')

            # Filtro icontains para texto
            if isinstance(field, (models.CharField, models.TextField)):
                self.filters[f"{field_name}__icontains"] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr='icontains'
                )

            # Filtros de rango para fechas
            if isinstance(field, (models.DateField, models.DateTimeField)):
                self.filters[f"{field_name}__gte"] = django_filters.DateFilter(
                    field_name=field_name,
                    lookup_expr='gte'
                )
                self.filters[f"{field_name}__lte"] = django_filters.DateFilter(
                    field_name=field_name,
                    lookup_expr='lte'
                )

    class Meta:
        abstract = True
