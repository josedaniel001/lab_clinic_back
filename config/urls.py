from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usuarios.views import PerfilUsuarioAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Módulo de autenticación y perfil
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', PerfilUsuarioAPIView.as_view(), name='auth_me'),
    path('api/localizacion/', include('localizacion.urls')),
    # Módulos de la aplicación
    path('api/usuarios/', include('usuarios.urls')),
    path('api/pacientes/', include('pacientes.urls')),
    path('api/', include('sistema.urls')),  # Aquí se encuentra /health/
    path('api/', include('administracion.urls')) # /api/roles/, /api/permisos/
]
