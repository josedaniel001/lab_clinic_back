from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLES = [
    { "id": "1", "nombre_rol": "Administrador", "status": True, "usuarios": 1 },
    { "id": "2", "nombre_rol": "Bioquímico", "status": True, "usuarios": 1 },
    { "id": "3", "nombre_rol": "Recepcionista", "status": True, "usuarios": 1 },
    { "id": "4", "nombre_rol": "Técnico de Laboratorio", "status": True, "usuarios": 0 },
]

class Command(BaseCommand):
    help = "Carga los roles base del sistema como grupos en Django"

    def handle(self, *args, **kwargs):
        for rol in ROLES:
            nombre = rol["nombre_rol"]
            grupo, creado = Group.objects.get_or_create(name=nombre)
            if creado:
                self.stdout.write(self.style.SUCCESS(f"✔ Grupo '{nombre}' creado"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Grupo '{nombre}' ya existía"))
