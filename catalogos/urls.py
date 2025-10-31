from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatalogoUnidadParametroViewSet

router = DefaultRouter()
router.register(r'unidades-parametros', CatalogoUnidadParametroViewSet, basename='unidad-parametro')

urlpatterns = [
    path('', include(router.urls)),
]
