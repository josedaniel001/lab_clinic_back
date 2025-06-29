from django.urls import path
# apps/sistema/urls.py
from rest_framework.routers import DefaultRouter
from .views import HealthCheckAPIView, ConfiguracionLaboratorioViewSet

router = DefaultRouter()
router.register(r'configuracion', ConfiguracionLaboratorioViewSet, basename='configuracion')

urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health_check'),
] + router.urls
