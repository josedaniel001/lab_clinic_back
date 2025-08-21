# banco_sangre/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonanteViewSet, EntrevistaViewSet, UnidadMuestraViewSet, LoteViewSet, SalidaUnidadViewSet

router = DefaultRouter()
router.register(r'donantes', DonanteViewSet)
router.register(r'entrevistas', EntrevistaViewSet)
router.register(r'unidades', UnidadMuestraViewSet)
router.register(r'lotes', LoteViewSet)
router.register(r'salidas', SalidaUnidadViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
