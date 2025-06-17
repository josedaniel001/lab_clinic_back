from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from administracion.models.permisos import PermisoPersonalizado
from administracion.serializers.permisos import PermisoPersonalizadoSerializer
from django.contrib.auth.models import Group

class PermisoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        permisos = PermisoPersonalizado.objects.all()
        serializer = PermisoPersonalizadoSerializer(permisos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='rol/(?P<rol_id>[^/.]+)')
    def permisos_por_rol(self, request, rol_id=None):
        try:
            grupo = Group.objects.get(id=rol_id)
            permisos = grupo.permisos_personalizados.all()
            data = [{'id': p.id, 'nombre': p.nombre, 'activo': p.activo} for p in permisos]
            return Response(data)
        except Group.DoesNotExist:
            return Response({'error': 'Rol no encontrado'}, status=404)
