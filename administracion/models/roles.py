from django.contrib.auth.models import Group
from django.db import models
from .permisos import PermisoPersonalizado

Group.add_to_class(
    'permisos_personalizados',
    models.ManyToManyField(PermisoPersonalizado, blank=True, related_name='grupos')
)
