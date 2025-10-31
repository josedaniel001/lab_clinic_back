# resultados/management/commands/listar_resultados.py

from django.core.management.base import BaseCommand
from resultados.models import Resultado


class Command(BaseCommand):
    help = 'Lista todos los resultados disponibles y muestra cuáles pueden ser revertidos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--solo-validados',
            action='store_true',
            help='Mostrar solo resultados validados (los que se pueden revertir)',
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Verificar un resultado específico por ID',
        )

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("📋 LISTADO DE RESULTADOS DE BANCO DE SANGRE"))
        self.stdout.write("="*80 + "\n")

        # Si se especifica un ID, solo mostrar ese
        if options['id']:
            try:
                resultado = Resultado.objects.get(id=options['id'])
                self.mostrar_resultado_detallado(resultado)
            except Resultado.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"\n❌ No existe el resultado con ID {options['id']}"))
                self.stdout.write("\n💡 Usa el comando sin --id para ver todos los resultados disponibles\n")
            return

        # Obtener resultados
        if options['solo_validados']:
            resultados = Resultado.objects.filter(estado='VALIDADO').select_related(
                'resultado__orden',
                'resultado__examen'
            ).order_by('-id')
            titulo = "RESULTADOS VALIDADOS (Pueden ser revertidos)"
        else:
            resultados = Resultado.objects.all().select_related(
                'resultado__orden',
                'resultado__examen'
            ).order_by('-id')
            titulo = "TODOS LOS RESULTADOS"

        total = resultados.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING("\n⚠️ No hay resultados en la base de datos\n"))
            return

        self.stdout.write(self.style.SUCCESS(f"\n{titulo}"))
        self.stdout.write(f"Total: {total} resultado(s)\n")
        self.stdout.write("-"*80 + "\n")

        # Contador por estado
        estados = {}
        for resultado in resultados:
            estados[resultado.estado] = estados.get(resultado.estado, 0) + 1

        # Mostrar cada resultado
        for resultado in resultados[:50]:  # Limitar a 50 para no llenar la pantalla
            self.mostrar_resultado(resultado)

        if total > 50:
            self.stdout.write(f"\n... y {total - 50} resultados más\n")

        # Resumen por estado
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN POR ESTADO"))
        self.stdout.write("="*80 + "\n")
        
        for estado, cantidad in estados.items():
            icono = "✅" if estado == "VALIDADO" else "⏳" if estado == "EN PROCESO" else "📋"
            puede_revertir = " (PUEDE REVERTIRSE)" if estado == "VALIDADO" else ""
            self.stdout.write(f"{icono} {estado}: {cantidad} resultado(s){puede_revertir}")

        self.stdout.write("\n" + "-"*80)
        self.stdout.write("\n💡 Comandos útiles:")
        self.stdout.write("   - Ver solo validados: python manage.py listar_resultados --solo-validados")
        self.stdout.write("   - Ver uno específico: python manage.py listar_resultados --id 5")
        self.stdout.write("\n")

    def mostrar_resultado(self, resultado):
        """Muestra un resultado de forma compacta"""
        try:
            orden = resultado.resultado.orden
            examen = resultado.resultado.examen
            
            # Icono según estado
            if resultado.estado == "VALIDADO":
                icono = "✅"
                color_fn = self.style.SUCCESS
            elif resultado.estado == "EN PROCESO":
                icono = "⏳"
                color_fn = self.style.WARNING
            elif resultado.estado == "COMPLETADO":
                icono = "✔️"
                color_fn = lambda x: x
            else:
                icono = "📋"
                color_fn = lambda x: x

            # Información del paciente/donante
            if orden.donante:
                paciente = f"{orden.donante.primer_nombre} {orden.donante.primer_apellido}"
            elif orden.paciente:
                paciente = f"{orden.paciente.nombres} {orden.paciente.apellidos}"
            else:
                paciente = "N/A"

            # Puede revertir?
            puede_revertir = " 🔄 [PUEDE REVERTIRSE]" if resultado.estado == "VALIDADO" else ""

            self.stdout.write(
                f"{icono} ID: {resultado.id:4d} | "
                f"Orden: {orden.codigo:20s} | "
                f"Estado: {color_fn(resultado.estado):15s} | "
                f"Examen: {examen.nombre[:30]:30s}"
                f"{puede_revertir}"
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error al mostrar resultado {resultado.id}: {str(e)}"))

    def mostrar_resultado_detallado(self, resultado):
        """Muestra un resultado con todos sus detalles"""
        self.stdout.write("\n" + "="*80)
        self.stdout.write(self.style.SUCCESS(f"DETALLES DEL RESULTADO ID: {resultado.id}"))
        self.stdout.write("="*80 + "\n")

        try:
            orden = resultado.resultado.orden
            examen = resultado.resultado.examen
            detalle = resultado.resultado

            # Información básica
            self.stdout.write(f"📊 ID Resultado: {resultado.id}")
            self.stdout.write(f"📋 Orden: {orden.codigo}")
            self.stdout.write(f"🔬 Examen: {examen.nombre}")
            
            # Estado con color
            if resultado.estado == "VALIDADO":
                estado_str = self.style.SUCCESS(f"✅ {resultado.estado}")
            elif resultado.estado == "EN PROCESO":
                estado_str = self.style.WARNING(f"⏳ {resultado.estado}")
            else:
                estado_str = f"📋 {resultado.estado}"
            self.stdout.write(f"🎯 Estado: {estado_str}")

            # Información del paciente/donante
            if orden.donante:
                self.stdout.write(f"👤 Donante: {orden.donante.primer_nombre} {orden.donante.primer_apellido}")
                self.stdout.write(f"   CUI: {orden.donante.cui}")
            elif orden.paciente:
                self.stdout.write(f"👤 Paciente: {orden.paciente.nombres} {orden.paciente.apellidos}")
                self.stdout.write(f"   Documento: {orden.paciente.numero_documento}")

            # Fechas
            self.stdout.write(f"📅 Fecha Resultado: {resultado.fecha_resultado}")
            if resultado.fecha_validacion:
                self.stdout.write(f"📅 Fecha Validación: {resultado.fecha_validacion}")
            if resultado.validado_por:
                self.stdout.write(f"👨‍⚕️ Validado por: {resultado.validado_por}")

            # Prioridad
            self.stdout.write(f"⚡ Prioridad: {resultado.prioridad}")

            # Observaciones
            if resultado.observaciones:
                self.stdout.write(f"\n📝 Observaciones:")
                self.stdout.write(f"   {resultado.observaciones}")

            # Valores
            valores = resultado.valores.all()
            if valores.exists():
                self.stdout.write(f"\n🔬 Valores del Examen ({valores.count()}):")
                for valor in valores:
                    self.stdout.write(
                        f"   • {valor.parametro}: {valor.valor} {valor.unidad} "
                        f"(Normal: {valor.rango_normal}) - Estado: {valor.estado}"
                    )

            # ¿Puede revertirse?
            self.stdout.write("\n" + "-"*80)
            if resultado.estado == "VALIDADO":
                self.stdout.write(self.style.SUCCESS("✅ ESTE RESULTADO PUEDE SER REVERTIDO"))
                self.stdout.write("\n💡 Para revertirlo, usa:")
                self.stdout.write(f"   POST /api/resultados/{resultado.id}/revertir-validacion/")
                self.stdout.write('\n   Body: {{"motivo_reversion": "...", "usuario_responsable": "..."}}')
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Este resultado NO puede ser revertido (Estado: {resultado.estado})"))
                self.stdout.write("   Solo se pueden revertir resultados en estado VALIDADO")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error al mostrar detalles: {str(e)}"))

        self.stdout.write("\n")

