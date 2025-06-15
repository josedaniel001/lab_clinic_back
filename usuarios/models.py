# en usuarios/models.py
from django.db import models
from django.contrib.auth.models import Group

class PermisoPersonalizado(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    vista_modulo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

Group.add_to_class('permisos_personalizados', models.ManyToManyField(PermisoPersonalizado, blank=True))