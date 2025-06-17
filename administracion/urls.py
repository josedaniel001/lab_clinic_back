from django.urls import path, include
from rest_framework.routers import DefaultRouter
from administracion.views.roles import RolViewSet
from administracion.views.permisos import PermisoViewSet

router = DefaultRouter()
router.register(r'roles', RolViewSet, basename='roles')
router.register(r'permisos', PermisoViewSet, basename='permisos')

urlpatterns = [
    path('', include(router.urls)),
]
