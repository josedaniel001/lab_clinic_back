# banco_sangre/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonanteViewSet, MuestraSangreViewSet, EntrevistaViewSet

router = DefaultRouter()
router.register(r'donantes', DonanteViewSet)
router.register(r'muestras', MuestraSangreViewSet)
router.register(r'entrevistas', EntrevistaViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
