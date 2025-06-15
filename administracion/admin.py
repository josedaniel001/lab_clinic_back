from administracion.models.permisos import PermisoPersonalizado
from django.contrib import admin

from django.contrib.admin.sites import AlreadyRegistered

try:
    admin.site.register(PermisoPersonalizado)
except AlreadyRegistered:
    pass

