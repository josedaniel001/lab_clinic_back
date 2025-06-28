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
    medico_nombre = serializers.CharField(source='medico.__str__', read_only=True)
    detalles = DetalleOrdenSerializer(source='detalleorden_set', many=True, read_only=True)
    total_examenes = serializers.IntegerField(read_only=True)
    codigo = serializers.CharField(read_only=True)

    # Este campo vendrá del frontend como lista de IDs
    examenes = serializers.PrimaryKeyRelatedField(
        queryset=Examen.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Orden
        fields = [
            'id', 'codigo', 'paciente', 'paciente_nombre',
            'medico', 'medico_nombre', 'fecha', 'hora',
            'estado', 'detalles', 'total_examenes', 'examenes','prioridad'
        ]

    def create(self, validated_data):
        examenes = validated_data.pop("examenes", [])
        validated_data['codigo'] = self.generate_codigo()
        orden = Orden.objects.create(**validated_data)

        for examen in examenes:
            DetalleOrden.objects.create(orden=orden, examen=examen)

        orden.refresh_from_db()  # 🔥 Esto actualiza los detalles y total_examenes
        return orden

    def generate_codigo(self):
        fecha_hoy = now().strftime('%Y%m%d')
        ultimo = Orden.objects.order_by('id').last()
        nuevo_id = (ultimo.id + 1) if ultimo else 1
        return f"ORD-{fecha_hoy}-{nuevo_id:04d}"
