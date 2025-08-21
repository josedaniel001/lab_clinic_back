from django.core.management.base import BaseCommand
from banco_sangre.models import Donante

class Command(BaseCommand):
    help = 'Genera códigos para donantes que no tengan código asignado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la generación de códigos incluso si ya tienen uno',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            donantes = Donante.objects.all()
            self.stdout.write("Generando códigos para TODOS los donantes...")
        else:
            donantes = Donante.objects.filter(codigo_donante__isnull=True)
            self.stdout.write("Generando códigos para donantes sin código...")
        
        count = 0
        for donante in donantes:
            try:
                if not donante.codigo_donante or force:
                    donante.generar_codigo_donante()
                    donante.save()
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Código generado para {donante.primer_nombre} {donante.primer_apellido}: {donante.codigo_donante}'
                        )
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error con donante {donante.cui}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Proceso completado. Se generaron {count} códigos exitosamente.'
            )
        )
