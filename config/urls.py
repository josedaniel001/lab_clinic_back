from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usuarios.views import PerfilUsuarioAPIView

def test_static_view(request):
    """Vista de prueba para verificar archivos estáticos"""
    context = {
        'debug': settings.DEBUG,
        'static_url': settings.STATIC_URL,
        'static_root': settings.STATIC_ROOT,
    }
    return render(request, 'test_static.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-static/', test_static_view, name='test_static'),
    
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
    path('api/', include('administracion.urls')), # /api/roles/, /api/permisos/
    path('api/banco_sangre/', include('banco_sangre.urls')) # /api/donantes
]

# Configuración para servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
