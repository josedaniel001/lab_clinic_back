from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardMetricViewSet, DashboardWidgetViewSet, DashboardConfigViewSet

router = DefaultRouter()
router.register(r'metricas', DashboardMetricViewSet, basename='metricas')
router.register(r'widgets', DashboardWidgetViewSet, basename='widgets')
router.register(r'configuracion', DashboardConfigViewSet, basename='configuracion')

urlpatterns = [
    path('', include(router.urls)),
]
