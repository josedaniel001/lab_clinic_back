from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from administracion.models.permisos import PermisoPersonalizado

class Command(BaseCommand):
    help = "Asigna permisos personalizados a los roles (grupos)"

    def handle(self, *args, **kwargs):
        permisos_por_rol = {
            "Administrador": [
                "ver_dashboard", "ver_modulo_admin", "ver_usuarios", "crear_usuario",
                "editar_usuario", "eliminar_usuario", "ver_roles", "crear_rol",
                "editar_rol", "eliminar_rol", "editar_permisos", "ver_notificaciones"
            ],
            "Bioquímico": [
                "ver_modulo_laboratorio", "ver_resultados", "validar_resultados"
            ],
            "Recepcionista": [
                "ver_modulo_recepcion", "ver_pacientes", "crear_paciente",
                "editar_paciente", "eliminar_paciente", "ver_medicos", "crear_medico",
                "editar_medico", "eliminar_medico", "ver_ordenes", "crear_orden",
                "eliminar_orden"
            ],
            "Técnico de Laboratorio": [
                "ver_modulo_laboratorio", "ver_inventario"
            ]
        }

        for nombre_rol, lista_permisos in permisos_por_rol.items():
            grupo, _ = Group.objects.get_or_create(name=nombre_rol)
            permisos = PermisoPersonalizado.objects.filter(nombre__in=lista_permisos)

            if not permisos.exists():
                self.stdout.write(self.style.WARNING(f"⚠ No se encontraron permisos para {nombre_rol}"))
                continue

            grupo.permisos_personalizados.set(permisos)  # 💡 rel many-to-many
            self.stdout.write(self.style.SUCCESS(f"✓ Permisos asignados al grupo: {nombre_rol}"))
