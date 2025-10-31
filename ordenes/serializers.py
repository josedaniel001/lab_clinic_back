from rest_framework import serializers
from .models import Orden, DetalleOrden, Examen
from examenes.serializers import ExamenSerializer
from django.utils.timezone import now

class DetalleOrdenSerializer(serializers.ModelSerializer):
    examen = ExamenSerializer(read_only=True)
    examen_id = serializers.PrimaryKeyRelatedField(
        queryset=Examen.objects.all(), write_only=True, source="examen"
    )

    class Meta:
        model = DetalleOrden
        fields = ['id', 'examen', 'examen_id', 'estado', 'observaciones', 'resultado']

class OrdenSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.CharField(source='paciente.nombre_completo', read_only=True)
    donante_nombre = serializers.CharField(source='donante.__str__', read_only=True)
    medico_nombre = serializers.CharField(source='medico.__str__', read_only=True)
    detalles = DetalleOrdenSerializer(source='detalleorden_set', many=True, read_only=True)
    total_examenes = serializers.IntegerField(read_only=True)
    codigo = serializers.CharField(read_only=True)
    codigo_donante = serializers.CharField(read_only=True)
    historial_denegaciones = serializers.SerializerMethodField(read_only=True)

    # Este campo vendrá del frontend como lista de IDs
    examenes = serializers.PrimaryKeyRelatedField(
        queryset=Examen.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Orden
        fields = [
            'id', 'codigo', 'paciente', 'paciente_nombre',
            'donante', 'donante_nombre', 'codigo_donante', 'genero_entrevista','continuar_entrevista',
            'medico', 'medico_nombre', 'fecha', 'hora',
            'estado', 'detalles', 'total_examenes', 'examenes','prioridad',
            'historial_denegaciones'
        ]
    
    def get_historial_denegaciones(self, obj):
        """
        Obtiene el historial de denegaciones asociadas a esta orden.
        """
        try:
            from resultados.models import HistorialDenegacion
            from resultados.serializers import HistorialDenegacionSerializer
            
            # Obtener las denegaciones de esta orden
            denegaciones = HistorialDenegacion.objects.filter(
                orden=obj
            ).select_related(
                'motivo_denegacion',
                'resultado'
            ).order_by('-fecha_denegacion')
            
            return HistorialDenegacionSerializer(denegaciones, many=True).data
        except Exception as e:
            print(f"Error obteniendo historial de denegaciones: {e}")
            return []

    def validate(self, data):
        """
        Valida que el paciente o donante no tenga órdenes pendientes de resolver.
        También valida que donantes con denegación permanente no puedan crear órdenes.
        """
        paciente = data.get('paciente')
        donante = data.get('donante')
        
        # Estados que se consideran "pendientes de resolver"
        estados_pendientes = ['PENDIENTE', 'EN PROCESO']
        
        # Validar si es paciente
        if paciente:
            ordenes_pendientes = Orden.objects.filter(
                paciente=paciente,
                estado__in=estados_pendientes
            )
            if ordenes_pendientes.exists():
                raise serializers.ValidationError({
                    'paciente': f'El paciente {paciente.nombre_completo} ya tiene una orden pendiente de resolver. '
                               f'Por favor, complete o cancele la orden anterior antes de crear una nueva.'
                })
        
        # Validar si es donante
        if donante:
            # 🔴 VALIDACIÓN NUEVA: Verificar si el donante tiene denegación permanente
            if donante.denegado_permanente:
                raise serializers.ValidationError({
                    'donante': f'🔴 El donante "{donante}" tiene una DENEGACIÓN PERMANENTE y no puede crear órdenes de examen. '
                              f'Motivo: {donante.motivo_denegacion_permanente or "No especificado"}. '
                              f'Fecha: {donante.fecha_denegacion_permanente.strftime("%d/%m/%Y") if donante.fecha_denegacion_permanente else "No registrada"}.'
                })
            
            # Validar órdenes pendientes (solo si no está permanentemente denegado)
            ordenes_pendientes = Orden.objects.filter(
                donante=donante,
                estado__in=estados_pendientes
            )
            if ordenes_pendientes.exists():
                raise serializers.ValidationError({
                    'donante': f'El donante {donante} ya tiene una orden pendiente de resolver. '
                              f'Por favor, complete o cancele la orden anterior antes de crear una nueva.'
                })
        
        return data

    def create(self, validated_data):
        examenes = validated_data.pop("examenes", [])
        validated_data['codigo'] = self.generate_codigo()
        orden = Orden.objects.create(**validated_data)

        for examen in examenes:
            DetalleOrden.objects.create(orden=orden, examen=examen)

        # Resetear los flags del donante para que pase por el proceso de entrevista nuevamente
        if orden.donante:
            orden.donante.tiene_entrevista_apro = False
            orden.donante.apto_donacion = False
            orden.donante.save(update_fields=['tiene_entrevista_apro', 'apto_donacion'])

        orden.refresh_from_db()  # 🔥 Esto actualiza los detalles y total_examenes
        return orden

    def generate_codigo(self):
        fecha_hoy = now().strftime('%Y%m%d')
        ultimo = Orden.objects.order_by('id').last()
        nuevo_id = (ultimo.id + 1) if ultimo else 1
        return f"ORD-{fecha_hoy}-{nuevo_id:04d}"
