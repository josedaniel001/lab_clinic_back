from rest_framework.permissions import BasePermission

class EsStaffOAdministradorGrupo(BasePermission):
    """
    Permite el acceso si el usuario:
    - Es staff (superusuario o administrador de Django)
    - O pertenece al grupo "Administrador"
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_staff:
                return True
            return request.user.groups.filter(name="Administrador").exists()
        return False

# Puedes extender fácilmente agregando más roles
class EsStaffOBioquimicoORecepcionista(BasePermission):
    """
    Permite acceso si es staff o pertenece a ciertos grupos específicos
    """
    grupos_permitidos = ["Administrador", "	Técnico de Laboratorio"]

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.is_staff:
                return True
            return request.user.groups.filter(name__in=self.grupos_permitidos).exists()
        return False