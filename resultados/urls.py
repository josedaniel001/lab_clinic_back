from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultadoViewSet

router = DefaultRouter()
router.register(r'', ResultadoViewSet, basename='resultado')

urlpatterns = [
    path('', include(router.urls)),
]
