# usuarios/filters.py
from django.contrib.auth.models import User
from core.filters import BaseGenericFilterSet

class UsuarioFilter(BaseGenericFilterSet):
    class Meta:
        model = User
        fields = '__all__'
