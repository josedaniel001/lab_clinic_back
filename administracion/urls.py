from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.roles import GrupoViewSet
from .views.permisos import PermisoPersonalizadoViewSet

router = DefaultRouter()
router.register(r'roles', GrupoViewSet, basename='roles')
router.register(r'permisos', PermisoPersonalizadoViewSet, basename='permisos')

urlpatterns = [
    path('', include(router.urls)),
]
