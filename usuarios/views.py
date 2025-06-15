from django.contrib.auth.models import User, Group, Permission
from rest_framework import viewsets, filters, permissions
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from .serializers import UsuarioSerializer, GrupoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response


class IsAdminUserGroup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Administrador").exists()


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['is_active', 'is_staff']

class GrupoViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = [IsAdminUser]  # Solo admins pueden modificar roles


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GrupoSerializer
    permission_classes = [IsAdminUserGroup]

class PerfilUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_active": user.is_active
        })