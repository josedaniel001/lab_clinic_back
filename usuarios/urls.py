from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UsuarioViewSet,GrupoViewSet  

router = DefaultRouter()
router.register(r'', UsuarioViewSet)
router.register(r'roles', GrupoViewSet, basename='roles')  # roles (grupos)

urlpatterns = [
    path('', include(router.urls)),
]
