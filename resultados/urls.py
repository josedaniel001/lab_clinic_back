from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultadoViewSet, CatalogoMotivoDenegacionViewSet, HistorialDenegacionViewSet

router = DefaultRouter()
router.register(r'resultados', ResultadoViewSet, basename='resultado')
router.register(r'motivos-denegacion', CatalogoMotivoDenegacionViewSet, basename='motivo-denegacion')
router.register(r'historial-denegaciones', HistorialDenegacionViewSet, basename='historial-denegacion')

urlpatterns = [
    path('', include(router.urls)),
]
