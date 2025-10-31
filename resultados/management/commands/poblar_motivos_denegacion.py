# resultados/management/commands/poblar_motivos_denegacion.py

from django.core.management.base import BaseCommand
from resultados.models import CatalogoMotivoDenegacion


class Command(BaseCommand):
    help = 'Pobla el catálogo de motivos de denegación con motivos comunes'

    def handle(self, *args, **kwargs):
        motivos = [
            # 🔴 DENEGACIONES PERMANENTES (nunca podrá donar)
            {
                'codigo': 'DENE-001',
                'nombre': 'Hepatitis B Reactivo (HBsAg)',
                'descripcion': 'Resultado positivo para antígeno de superficie de Hepatitis B (HBsAg). Indica infección activa o portador crónico.',
                'tipo_denegacion': 'PERMANENTE',
                'tiempo_diferimiento_dias': None,
            },
            {
                'codigo': 'DENE-002',
                'nombre': 'Hepatitis C Reactivo (Anti-HCV)',
                'descripcion': 'Resultado positivo para anticuerpos contra el virus de Hepatitis C (Anti-HCV). Indica exposición o infección.',
                'tipo_denegacion': 'PERMANENTE',
                'tiempo_diferimiento_dias': None,
            },
            {
                'codigo': 'DENE-003',
                'nombre': 'VIH Reactivo (HIV Ab/Ag)',
                'descripcion': 'Resultado positivo para anticuerpos y/o antígenos del Virus de Inmunodeficiencia Humana (VIH). Indica infección.',
                'tipo_denegacion': 'PERMANENTE',
                'tiempo_diferimiento_dias': None,
            },
            {
                'codigo': 'DENE-005',
                'nombre': 'Chagas Reactivo',
                'descripcion': 'Resultado positivo para anticuerpos contra Trypanosoma cruzi. Indica enfermedad de Chagas.',
                'tipo_denegacion': 'PERMANENTE',
                'tiempo_diferimiento_dias': None,
            },
            {
                'codigo': 'DENE-016',
                'nombre': 'HTLV Reactivo',
                'descripcion': 'Resultado positivo para Virus Linfotrópico T Humano (HTLV-I/II). Contraindica la donación.',
                'tipo_denegacion': 'PERMANENTE',
                'tiempo_diferimiento_dias': None,
            },
            
            # 🟡 DENEGACIONES TEMPORALES (puede donar después)
            {
                'codigo': 'DENE-004',
                'nombre': 'Sífilis Reactivo',
                'descripcion': 'Resultado positivo para pruebas treponémicas o no treponémicas de sífilis. Indica infección activa o previa. Requiere tratamiento completo.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 365,  # 1 año después de tratamiento
            },
            {
                'codigo': 'DENE-006',
                'nombre': 'Hemoglobina Baja',
                'descripcion': 'Nivel de hemoglobina por debajo del mínimo requerido para donación. Hombres: <13.5 g/dL, Mujeres: <12.5 g/dL.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # 3 meses
            },
            {
                'codigo': 'DENE-007',
                'nombre': 'Hematocrito Bajo',
                'descripcion': 'Nivel de hematocrito por debajo del mínimo requerido para donación. Hombres: <41%, Mujeres: <38%.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # 3 meses
            },
            {
                'codigo': 'DENE-008',
                'nombre': 'Glóbulos Rojos Bajos',
                'descripcion': 'Conteo de glóbulos rojos (eritrocitos) por debajo del rango normal. Indica posible anemia.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # 3 meses
            },
            {
                'codigo': 'DENE-009',
                'nombre': 'Glóbulos Blancos Anormales',
                'descripcion': 'Conteo de glóbulos blancos (leucocitos) fuera del rango normal. Puede indicar infección o trastorno hematológico.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # 1 mes
            },
            {
                'codigo': 'DENE-010',
                'nombre': 'Plaquetas Bajas (Trombocitopenia)',
                'descripcion': 'Conteo de plaquetas por debajo del nivel seguro para donación (<150,000/μL). Riesgo de sangrado.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # 3 meses
            },
            {
                'codigo': 'DENE-011',
                'nombre': 'Presión Arterial Elevada',
                'descripcion': 'Presión arterial por encima de 180/100 mmHg. Contraindica la donación por riesgo cardiovascular.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # 1 mes
            },
            {
                'codigo': 'DENE-012',
                'nombre': 'Presión Arterial Baja',
                'descripcion': 'Presión arterial por debajo de 90/50 mmHg. Riesgo de hipotensión durante o después de la donación.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 7,  # 1 semana
            },
            {
                'codigo': 'DENE-013',
                'nombre': 'Temperatura Elevada (Fiebre)',
                'descripcion': 'Temperatura corporal mayor a 37.5°C. Puede indicar proceso infeccioso activo.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 14,  # 2 semanas
            },
            {
                'codigo': 'DENE-014',
                'nombre': 'Pulso Anormal',
                'descripcion': 'Frecuencia cardíaca fuera del rango normal (50-100 lpm). Indica posible arritmia o condición cardiovascular.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # 1 mes
            },
            {
                'codigo': 'DENE-015',
                'nombre': 'Transaminasas Elevadas (ALT/AST)',
                'descripcion': 'Niveles elevados de enzimas hepáticas. Puede indicar daño hepático o hepatitis.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 180,  # 6 meses
            },
            {
                'codigo': 'DENE-017',
                'nombre': 'Malaria/Paludismo',
                'descripcion': 'Historia de malaria o resultado positivo en pruebas de detección. Requiere período de diferimiento.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 1095,  # 3 años
            },
            {
                'codigo': 'DENE-018',
                'nombre': 'Brucelosis',
                'descripcion': 'Resultado positivo para anticuerpos contra Brucella. Indica infección activa o reciente.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 365,  # 1 año
            },
            {
                'codigo': 'DENE-019',
                'nombre': 'CMV (Citomegalovirus) Reactivo',
                'descripcion': 'Resultado positivo para Citomegalovirus en población de riesgo (donación para neonatos/inmunodeprimidos).',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 180,  # 6 meses
            },
            {
                'codigo': 'DENE-020',
                'nombre': 'Factor Rh Incompatible',
                'descripcion': 'Incompatibilidad en el factor Rh para propósito específico de la donación.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': None,  # Depende del caso
            },
            {
                'codigo': 'DENE-021',
                'nombre': 'Peso Insuficiente',
                'descripcion': 'Peso corporal menor a 50 kg (110 lbs). Riesgo de complicaciones por volumen de sangre extraído.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # Hasta alcanzar peso adecuado
            },
            {
                'codigo': 'DENE-022',
                'nombre': 'Medicación Contraindica Donación',
                'descripcion': 'Uso de medicamentos que contraindican la donación temporal o permanentemente.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # Varía según medicamento
            },
            {
                'codigo': 'DENE-023',
                'nombre': 'Consumo de Alcohol Reciente',
                'descripcion': 'Consumo de bebidas alcohólicas en las últimas 12 horas. Diferir hasta eliminar el alcohol.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 1,  # 24 horas
            },
            {
                'codigo': 'DENE-024',
                'nombre': 'Tatuaje o Piercing Reciente',
                'descripcion': 'Tatuaje, perforación o acupuntura en los últimos 12 meses sin condiciones estériles certificadas.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 365,  # 12 meses
            },
            {
                'codigo': 'DENE-025',
                'nombre': 'Comportamiento de Riesgo',
                'descripcion': 'Comportamientos de alto riesgo identificados en la entrevista que contraindican la donación.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 365,  # 12 meses
            },
            {
                'codigo': 'DENE-026',
                'nombre': 'Período de Ventana Inmunológica',
                'descripcion': 'Exposición reciente a riesgo con período de ventana inmunológica insuficiente para detección.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # 3 meses
            },
            {
                'codigo': 'DENE-027',
                'nombre': 'Enfermedad Crónica Descompensada',
                'descripcion': 'Enfermedad crónica (diabetes, hipertensión, etc.) sin control adecuado.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 90,  # Hasta control
            },
            {
                'codigo': 'DENE-028',
                'nombre': 'Condición Médica Temporal',
                'descripcion': 'Condición médica temporal que requiere diferimiento (gripe, infección, cirugía reciente, etc.).',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # Varía según condición
            },
            {
                'codigo': 'DENE-029',
                'nombre': 'Muestra Hemolizada',
                'descripcion': 'Muestra de sangre hemolizada que impide realizar análisis confiables.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 7,  # Repetir muestra
            },
            {
                'codigo': 'DENE-030',
                'nombre': 'Muestra Insuficiente',
                'descripcion': 'Volumen insuficiente de muestra para completar todas las pruebas requeridas.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 7,  # Repetir muestra
            },
            {
                'codigo': 'DENE-031',
                'nombre': 'Resultado Indeterminado',
                'descripcion': 'Resultado de prueba indeterminado que requiere confirmación. Por precaución, se difiere la donación.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 30,  # Hasta confirmación
            },
            {
                'codigo': 'DENE-032',
                'nombre': 'Donación Muy Reciente',
                'descripcion': 'Donación previa hace menos de 8 semanas (hombres) o 12 semanas (mujeres).',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': 56,  # 8 semanas para hombres
            },
            {
                'codigo': 'DENE-999',
                'nombre': 'Otro Motivo Médico',
                'descripcion': 'Otros motivos médicos no especificados que contraindican la donación.',
                'tipo_denegacion': 'TEMPORAL',
                'tiempo_diferimiento_dias': None,  # Varía según caso
            },
        ]

        creados = 0
        actualizados = 0

        for motivo_data in motivos:
            motivo, created = CatalogoMotivoDenegacion.objects.update_or_create(
                codigo=motivo_data['codigo'],
                defaults={
                    'nombre': motivo_data['nombre'],
                    'descripcion': motivo_data['descripcion'],
                    'tipo_denegacion': motivo_data['tipo_denegacion'],
                    'tiempo_diferimiento_dias': motivo_data.get('tiempo_diferimiento_dias'),
                    'activo': True
                }
            )
            
            tipo_emoji = "🔴" if motivo.tipo_denegacion == 'PERMANENTE' else "🟡"
            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'{tipo_emoji} Creado: {motivo.codigo} - {motivo.nombre} ({motivo.tipo_denegacion})')
                )
            else:
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(f'{tipo_emoji} Actualizado: {motivo.codigo} - {motivo.nombre} ({motivo.tipo_denegacion})')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Proceso completado:\n'
                f'   • {creados} motivos creados\n'
                f'   • {actualizados} motivos actualizados\n'
                f'   • Total: {creados + actualizados} motivos en el catálogo\n\n'
                f'📊 Clasificación:\n'
                f'   🔴 PERMANENTES: {CatalogoMotivoDenegacion.objects.filter(tipo_denegacion="PERMANENTE").count()}\n'
                f'   🟡 TEMPORALES: {CatalogoMotivoDenegacion.objects.filter(tipo_denegacion="TEMPORAL").count()}'
            )
        )
