from django.core.management.base import BaseCommand
from catalogos.models import CatalogoUnidadParametro

class Command(BaseCommand):
    help = 'Pobla el catálogo de unidades de parámetros con datos iniciales'

    def handle(self, *args, **options):
        """Pobla el catálogo con unidades comunes de laboratorio"""
        
        unidades_data = [
            # Hematología
            {
                'codigo': 'GDL',
                'nombre': 'Gramos por decilitro',
                'simbolo': 'g/dL',
                'categoria': 'Hematología',
                'descripcion': 'Unidad estándar para hemoglobina y proteínas'
            },
            {
                'codigo': 'MUL',
                'nombre': 'Millones por microlitro',
                'simbolo': 'M/μL',
                'categoria': 'Hematología',
                'descripcion': 'Unidad para conteo de hematíes'
            },
            {
                'codigo': 'KUL',
                'nombre': 'Miles por microlitro',
                'simbolo': 'K/μL',
                'categoria': 'Hematología',
                'descripcion': 'Unidad para conteo de leucocitos y plaquetas'
            },
            {
                'codigo': 'PCT',
                'nombre': 'Porcentaje',
                'simbolo': '%',
                'categoria': 'Hematología',
                'descripcion': 'Unidad para hematocrito y otros porcentajes'
            },
            
            # Química Clínica
            {
                'codigo': 'MGDL',
                'nombre': 'Miligramos por decilitro',
                'simbolo': 'mg/dL',
                'categoria': 'Química Clínica',
                'descripcion': 'Unidad estándar para glucosa, colesterol, triglicéridos'
            },
            {
                'codigo': 'UMOL',
                'nombre': 'Micromoles por litro',
                'simbolo': 'μmol/L',
                'categoria': 'Química Clínica',
                'descripcion': 'Unidad para creatinina, urea'
            },
            {
                'codigo': 'MMOL',
                'nombre': 'Milimoles por litro',
                'simbolo': 'mmol/L',
                'categoria': 'Química Clínica',
                'descripcion': 'Unidad para electrolitos'
            },
            {
                'codigo': 'UI',
                'nombre': 'Unidades internacionales',
                'simbolo': 'UI/L',
                'categoria': 'Química Clínica',
                'descripcion': 'Unidad para enzimas'
            },
            
            # Endocrinología
            {
                'codigo': 'MUI',
                'nombre': 'Micro unidades internacionales',
                'simbolo': 'μUI/mL',
                'categoria': 'Endocrinología',
                'descripcion': 'Unidad para insulina'
            },
            {
                'codigo': 'NGML',
                'nombre': 'Nanogramos por mililitro',
                'simbolo': 'ng/mL',
                'categoria': 'Endocrinología',
                'descripcion': 'Unidad para hormonas tiroideas'
            },
            {
                'codigo': 'PGML',
                'nombre': 'Picogramos por mililitro',
                'simbolo': 'pg/mL',
                'categoria': 'Endocrinología',
                'descripcion': 'Unidad para hormonas de baja concentración'
            },
            
            # Microbiología
            {
                'codigo': 'CFU',
                'nombre': 'Unidades formadoras de colonias',
                'simbolo': 'UFC/mL',
                'categoria': 'Microbiología',
                'descripcion': 'Unidad para conteo bacteriano'
            },
            {
                'codigo': 'NEG',
                'nombre': 'Negativo',
                'simbolo': 'Negativo',
                'categoria': 'Microbiología',
                'descripcion': 'Resultado cualitativo negativo'
            },
            {
                'codigo': 'POS',
                'nombre': 'Positivo',
                'simbolo': 'Positivo',
                'categoria': 'Microbiología',
                'descripcion': 'Resultado cualitativo positivo'
            },
            
            # Inmunología
            {
                'codigo': 'REACT',
                'nombre': 'Reactivo',
                'simbolo': 'Reactivo',
                'categoria': 'Inmunología',
                'descripcion': 'Resultado reactivo en pruebas serológicas'
            },
            {
                'codigo': 'NOREA',
                'nombre': 'No Reactivo',
                'simbolo': 'No Reactivo',
                'categoria': 'Inmunología',
                'descripcion': 'Resultado no reactivo en pruebas serológicas'
            },
            {
                'codigo': 'INDET',
                'nombre': 'Indeterminado',
                'simbolo': 'Indeterminado',
                'categoria': 'Inmunología',
                'descripcion': 'Resultado indeterminado en pruebas serológicas'
            },
            
            # Otros
            {
                'codigo': 'MMHG',
                'nombre': 'Milímetros de mercurio',
                'simbolo': 'mmHg',
                'categoria': 'Otros',
                'descripcion': 'Unidad para presión arterial'
            },
            {
                'codigo': 'GRADOS',
                'nombre': 'Grados Celsius',
                'simbolo': '°C',
                'categoria': 'Otros',
                'descripcion': 'Unidad para temperatura'
            },
            {
                'codigo': 'LMIN',
                'nombre': 'Litros por minuto',
                'simbolo': 'L/min',
                'categoria': 'Otros',
                'descripcion': 'Unidad para flujo'
            }
        ]
        
        creados = 0
        actualizados = 0
        
        for unidad_data in unidades_data:
            unidad, created = CatalogoUnidadParametro.objects.get_or_create(
                codigo=unidad_data['codigo'],
                defaults=unidad_data
            )
            
            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creada: {unidad.simbolo} - {unidad.nombre}')
                )
            else:
                # Actualizar datos existentes
                for key, value in unidad_data.items():
                    if key != 'codigo':
                        setattr(unidad, key, value)
                unidad.save()
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Actualizada: {unidad.simbolo} - {unidad.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Resumen:\n'
                f'   • Unidades creadas: {creados}\n'
                f'   • Unidades actualizadas: {actualizados}\n'
                f'   • Total procesadas: {creados + actualizados}'
            )
        )
