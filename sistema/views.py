
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from datetime import datetime
from .models import ConfiguracionLaboratorio
from .serializers import ConfiguracionLaboratorioSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
            "version": "1.0.0",
            "message": "API funcionando correctamente",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
class ConfiguracionLaboratorioViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionLaboratorio.objects.all()
    serializer_class = ConfiguracionLaboratorioSerializer
    parser_classes = [MultiPartParser, FormParser]  # Para subir logo

    def get_object(self):
        # Asumimos solo 1 registro de configuración
        obj, _ = ConfiguracionLaboratorio.objects.get_or_create(pk=1)
        return obj

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        # Si llega logo, va en request.FILES y DRF lo maneja.
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return Response({"detail": "Use update instead."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
