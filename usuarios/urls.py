from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UsuarioViewSet,GrupoViewSet,PerfilUsuarioAPIView  

router = DefaultRouter()
router.register(r'', UsuarioViewSet)
router.register(r'roles', GrupoViewSet, basename='roles')  # roles (grupos)

urlpatterns  = [
    path('perfil/', PerfilUsuarioAPIView.as_view(), name='perfil_usuario'),
    path('', include(router.urls)),    
]
