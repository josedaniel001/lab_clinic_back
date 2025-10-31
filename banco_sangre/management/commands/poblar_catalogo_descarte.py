from django.core.management.base import BaseCommand
from banco_sangre.models import CatalogoDescarte

class Command(BaseCommand):
    help = 'Pobla el catálogo de motivos de descarte con datos de prueba'

    def handle(self, *args, **options):
        motivos_descarte = [
            {
                'codigo': 'CONT',
                'nombre': 'Contaminación',
                'descripcion': 'Muestra contaminada durante el proceso de extracción o manipulación'
            },
            {
                'codigo': 'VENC',
                'nombre': 'Vencimiento',
                'descripcion': 'Muestra vencida o próxima a vencer'
            },
            {
                'codigo': 'VOL',
                'nombre': 'Volumen Insuficiente',
                'descripcion': 'Volumen de muestra insuficiente para realizar los análisis'
            },
            {
                'codigo': 'HEM',
                'nombre': 'Hemólisis',
                'descripcion': 'Muestra con signos de hemólisis que afecta los resultados'
            },
            {
                'codigo': 'COAG',
                'nombre': 'Coagulación',
                'descripcion': 'Muestra coagulada que impide el procesamiento'
            },
            {
                'codigo': 'TEMP',
                'nombre': 'Temperatura Inadecuada',
                'descripcion': 'Muestra expuesta a temperaturas inadecuadas durante transporte'
            },
            {
                'codigo': 'ETIQ',
                'nombre': 'Error de Etiquetado',
                'descripcion': 'Error en el etiquetado o identificación de la muestra'
            },
            {
                'codigo': 'CAL',
                'nombre': 'Calidad Insuficiente',
                'descripcion': 'Muestra con calidad insuficiente para análisis confiables'
            },
            {
                'codigo': 'REP',
                'nombre': 'Repetición de Análisis',
                'descripcion': 'Muestra descartada para repetir análisis con nueva muestra'
            },
            {
                'codigo': 'OTRO',
                'nombre': 'Otros',
                'descripcion': 'Otros motivos no especificados en el catálogo'
            }
        ]

        for motivo_data in motivos_descarte:
            motivo, created = CatalogoDescarte.objects.get_or_create(
                codigo=motivo_data['codigo'],
                defaults={
                    'nombre': motivo_data['nombre'],
                    'descripcion': motivo_data['descripcion'],
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Creado motivo de descarte: {motivo.codigo} - {motivo.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Motivo ya existe: {motivo.codigo} - {motivo.nombre}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Catálogo de descarte poblado exitosamente con {len(motivos_descarte)} motivos')
        )
