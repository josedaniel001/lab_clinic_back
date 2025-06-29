from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    path('api/resultados/', include('resultados.urls')),
    path('api/', include('pacientes.urls')),
    path('api/', include('ordenes.urls')),
    path('api/', include('examenes.urls')),
    path('api/', include('medicos.urls')),
    path('api/', include('sistema.urls')),  # Aquí se encuentra /health/
    path('api/', include('administracion.urls')) # /api/roles/, /api/permisos/
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
