from django.core.management.base import BaseCommand
from banco_sangre.models import Donante, UnidadMuestra
from django.db.models import Max

class Command(BaseCommand):
    help = 'Actualiza las fechas de última donación basándose en las unidades existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la actualización incluso si ya tienen fecha',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write("Actualizando fechas de última donación...")
        
        # Obtener la fecha más reciente de extracción para cada donante
        donantes_con_unidades = UnidadMuestra.objects.filter(
            donante__isnull=False
        ).values('donante').annotate(
            ultima_fecha=Max('fecha_extraccion')
        )
        
        count = 0
        for item in donantes_con_unidades:
            try:
                donante = Donante.objects.get(id=item['donante'])
                ultima_fecha = item['ultima_fecha']
                
                if force or not donante.fecha_ultima_donacion:
                    donante.fecha_ultima_donacion = ultima_fecha
                    donante.save()
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Fecha actualizada para {donante.primer_nombre} {donante.primer_apellido}: {ultima_fecha}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'⚠ Donante {donante.primer_nombre} {donante.primer_apellido} ya tiene fecha: {donante.fecha_ultima_donacion}'
                    )
                    
            except Donante.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Donante con ID {item["donante"]} no encontrado'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error actualizando donante {item["donante"]}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado. Se actualizaron {count} fechas exitosamente.'
            )
        )
