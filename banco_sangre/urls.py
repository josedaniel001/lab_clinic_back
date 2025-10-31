# banco_sangre/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonanteViewSet, EntrevistaViewSet, UnidadMuestraViewSet, LoteViewSet, CodigoDonanteViewSet, CatalogoDescarteViewSet, DescarteMuestraViewSet, SalidaUnidadViewSet
from .reports_views import ReportesViewSet

router = DefaultRouter()
router.register(r'donantes', DonanteViewSet)
router.register(r'entrevistas', EntrevistaViewSet)
router.register(r'unidades', UnidadMuestraViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'codigos-donante', CodigoDonanteViewSet)
router.register(r'catalogo-descarte', CatalogoDescarteViewSet)
router.register(r'descartes', DescarteMuestraViewSet)
router.register(r'salidas', SalidaUnidadViewSet)
router.register(r'reportes', ReportesViewSet, basename='reportes')


urlpatterns = [
    path('', include(router.urls)),
]
