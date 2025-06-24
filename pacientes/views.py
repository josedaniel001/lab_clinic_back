from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Paciente
from .serializers import PacienteSerializer
from .filters import PacienteFilter

class PacientePagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all().order_by('-fecha_registro')
    serializer_class = PacienteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PacienteFilter
    pagination_class = PacientePagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        paciente = serializer.save()
        return Response({
            "id": paciente.id,
            "message": "Paciente creado exitosamente"
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        paciente = self.get_object()
        paciente.activo = False
        paciente.save()
        return Response({"message": "Paciente eliminado exitosamente"}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Convertimos el request a un diccionario mutable
        data = request.data.copy()

        # Evitar que se actualicen estos campos
        data.pop('numero_documento', None)
        data.pop('tipo_documento', None)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "id": serializer.instance.id,
            "message": "Paciente actualizado exitosamente"
        })