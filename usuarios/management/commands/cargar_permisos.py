from django.core.management.base import BaseCommand
from usuarios.models import PermisoPersonalizado

PERMISOS = [
    {"nombre": "ver_dashboard", "vista_modulo": "Dashboard", "activo":True},
    {"nombre": "ver_modulo_recepcion", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "ver_pacientes", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "crear_paciente", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "editar_paciente", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "eliminar_paciente", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "ver_medicos", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "crear_medico", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "editar_medico", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "eliminar_medico", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "ver_ordenes", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "crear_orden", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "eliminar_orden", "vista_modulo": "Recepción", "activo":True},
    {"nombre": "ver_modulo_laboratorio", "vista_modulo": "Laboratorio", "activo":True},
    {"nombre": "ver_resultados", "vista_modulo": "Laboratorio", "activo":True},
    {"nombre": "validar_resultados", "vista_modulo": "Laboratorio", "activo":True},
    {"nombre": "ver_inventario", "vista_modulo": "Laboratorio", "activo":True},
    {"nombre": "ver_modulo_reportes", "vista_modulo": "Reportes", "activo":True},
    {"nombre": "ver_estadisticas", "vista_modulo": "Reportes", "activo":True},
    {"nombre": "ver_modulo_admin", "vista_modulo": "Administración", "activo":True},
    {"nombre": "ver_usuarios", "vista_modulo": "Administración", "activo":True},
    {"nombre": "crear_usuario", "vista_modulo": "Administración", "activo":True},
    {"nombre": "editar_usuario", "vista_modulo": "Administración", "activo":True},
    {"nombre": "eliminar_usuario", "vista_modulo": "Administración", "activo":True},
    {"nombre": "ver_roles", "vista_modulo": "Administración", "activo":True},
    {"nombre": "crear_rol", "vista_modulo": "Administración", "activo":True},
    {"nombre": "editar_rol", "vista_modulo": "Administración", "activo":True},
    {"nombre": "eliminar_rol", "vista_modulo": "Administración", "activo":True},
    {"nombre": "editar_permisos", "vista_modulo": "Administración", "activo":True},
    {"nombre": "ver_notificaciones", "vista_modulo": "Dashboard", "activo":True},
]

class Command(BaseCommand):
    help = 'Carga los permisos personalizados iniciales'

    def handle(self, *args, **kwargs):
       for permiso in PERMISOS:
         if "nombre" not in permiso or "vista_modulo" not in permiso or "activo" not in permiso:
            self.stdout.write(self.style.ERROR(f"❌ Permiso inválido o incompleto: {permiso}"))
            continue
         obj, creado = PermisoPersonalizado.objects.get_or_create(
            nombre=permiso["nombre"],
            defaults={
            "vista_modulo": permiso["vista_modulo"],
            "activo": permiso["activo"]
            }
         )

