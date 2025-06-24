from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamenViewSet

router = DefaultRouter()
router.register(r'examenes', ExamenViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
