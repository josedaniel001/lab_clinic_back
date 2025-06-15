from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets, filters, permissions,status
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from .serializers import UsuarioSerializer, GrupoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import EsStaffOAdministradorGrupo
from usuarios.filters import UsuarioFilter


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [EsStaffOAdministradorGrupo]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff']
    filterset_class = UsuarioFilter
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        password = data.pop("password", None)
        rol_id = data.pop("rol_id", None)

        user_serializer = self.get_serializer(data=data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        if password:
            user.set_password(password)
            user.save()

        if rol_id:
            try:
                group = Group.objects.get(id=rol_id)
                user.groups.add(group)
            except Group.DoesNotExist:
                return Response({"error": "Grupo no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"id": user.id, "message": "Usuario creado exitosamente"}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        rol_id = request.data.get("rol_id")
        if rol_id:
            instance.groups.clear()
            try:
                group = Group.objects.get(id=rol_id)
                instance.groups.add(group)
            except Group.DoesNotExist:
                return Response({"error": "Grupo no encontrado"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Usuario actualizado exitosamente"})

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response({"message": "Usuario eliminado exitosamente"}, status=status.HTTP_204_NO_CONTENT)

class GrupoViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = [EsStaffOAdministradorGrupo]  # Admins y staff pueden modificar roles

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = [EsStaffOAdministradorGrupo]

class PerfilUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        grupos = user.groups.all()

        # Permisos estándar del sistema (auth_permission)
        permisos_sistema = Permission.objects.filter(group__user=user).values_list(
            'content_type__app_label', 'codename'
        ).distinct()

        permisos = [
            f"{app_label}.{codename}" for app_label, codename in permisos_sistema
        ]

        # Permisos personalizados (tu modelo)
        permisos_personalizados = set()
        for grupo in grupos:
            if hasattr(grupo, 'permisos_personalizados'):
                permisos_personalizados.update([
                    permiso.nombre for permiso in grupo.permisos_personalizados.all()
                ])

        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "groups": [g.name for g in grupos],
            "permissions": permisos,  # solo los permisos del sistema
            "role": grupos[0].name if grupos else None,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "display_name": user.first_name or user.username,
            # Si el frontend también quiere verlos, puedes descomentar esto:
            "custom_permissions": list(permisos_personalizados),
        })
