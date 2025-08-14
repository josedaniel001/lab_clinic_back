from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Puebla todas las tablas con datos de prueba (donantes, médicos, exámenes, pacientes, órdenes, resultados)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--donantes',
            type=int,
            default=50,
            help='Número de donantes a crear (default: 50)'
        )
        parser.add_argument(
            '--medicos',
            type=int,
            default=20,
            help='Número de médicos a crear (default: 20)'
        )
        parser.add_argument(
            '--unidades',
            type=int,
            default=100,
            help='Número de unidades de muestra a crear (default: 100)'
        )
        parser.add_argument(
            '--examenes',
            type=int,
            default=30,
            help='Número de exámenes a crear (default: 30)'
        )
        parser.add_argument(
            '--donantes',
            type=int,
            default=50,
            help='Número de donantes a crear (default: 50)'
        )
        parser.add_argument(
            '--ordenes',
            type=int,
            default=100,
            help='Número de órdenes a crear (default: 100)'
        )
        parser.add_argument(
            '--resultados',
            type=int,
            default=80,
            help='Número de resultados a crear (default: 80)'
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando población completa de datos de prueba...')
        
        # Ejecutar comando de datos de banco de sangre
        self.stdout.write('📊 Poblando datos de banco de sangre...')
        call_command(
            'poblar_datos_prueba',
            donantes=options['donantes'],
            medicos=options['medicos'],
            unidades=options['unidades']
        )
        
        # Ejecutar comando de datos de exámenes
        self.stdout.write('🔬 Poblando datos de exámenes...')
        call_command(
            'poblar_examenes_prueba',
            examenes=options['examenes'],
            donantes=options['donantes'],
            ordenes=options['ordenes'],
            resultados=options['resultados']
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Población completa finalizada exitosamente!'))
        self.stdout.write('')
        self.stdout.write('📋 Resumen de datos creados:')
        self.stdout.write(f'   • Donantes: {options["donantes"]}')
        self.stdout.write(f'   • Médicos: {options["medicos"]}')
        self.stdout.write(f'   • Unidades de muestra: {options["unidades"]}')
        self.stdout.write(f'   • Exámenes: {options["examenes"]}')
        self.stdout.write(f'   • Donantes (exámenes): {options["donantes"]}')
        self.stdout.write(f'   • Órdenes: {options["ordenes"]}')
        self.stdout.write(f'   • Resultados: {options["resultados"]}')
        self.stdout.write('')
        self.stdout.write('👤 Usuario administrador: admin/admin123') 