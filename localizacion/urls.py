from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaisViewSet, DepartamentoViewSet, MunicipioViewSet

router = DefaultRouter()
router.register(r'paises', PaisViewSet, basename='paises')
router.register(r'departamentos', DepartamentoViewSet, basename='departamentos')
router.register(r'municipios', MunicipioViewSet, basename='municipios')

urlpatterns = [
    path('', include(router.urls)),
]
