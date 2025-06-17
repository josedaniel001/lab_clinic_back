from django.core.management.base import BaseCommand
from localizacion.models import Pais, Departamento, Municipio

class Command(BaseCommand):
    help = 'Puebla los catálogos de países, departamentos y municipios'

    def handle(self, *args, **kwargs):
        catalogos = {
            "Guatemala": {
                "Guatemala": ["Ciudad de Guatemala", "Mixco", "Villa Nueva", "San Miguel Petapa"],
                "Quetzaltenango": ["Quetzaltenango", "Olintepeque", "La Esperanza"],
                "Petén": ["Flores", "San Benito", "Santa Elena"],
            },
            "México": {
                "Ciudad de México": ["Álvaro Obregón", "Coyoacán", "Iztapalapa"],
                "Jalisco": ["Guadalajara", "Zapopan", "Tlaquepaque"],
                "Nuevo León": ["Monterrey", "San Nicolás", "Guadalupe"],
            },
            "Estados Unidos": {
                "California": ["Los Angeles", "San Francisco", "San Diego"],
                "Texas": ["Houston", "Austin", "Dallas"],
                "Florida": ["Miami", "Orlando", "Tampa"],
            },
        }

        for pais_nombre, departamentos in catalogos.items():
            pais_obj, _ = Pais.objects.get_or_create(nombre=pais_nombre)
            self.stdout.write(f'✔ País: {pais_obj.nombre}')

            for depto_nombre, municipios in departamentos.items():
                depto_obj, _ = Departamento.objects.get_or_create(nombre=depto_nombre, pais=pais_obj)
                self.stdout.write(f'  └─ Departamento: {depto_obj.nombre}')

                for municipio_nombre in municipios:
                    municipio_obj, _ = Municipio.objects.get_or_create(nombre=municipio_nombre, departamento=depto_obj)
                    self.stdout.write(f'      • Municipio: {municipio_obj.nombre}')

        self.stdout.write(self.style.SUCCESS('✅ Catálogos poblados correctamente.'))