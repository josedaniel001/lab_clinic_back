from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from datetime import datetime

class HealthCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "status": "ok",
            "version": "1.0.0",
            "message": "API funcionando correctamente",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
