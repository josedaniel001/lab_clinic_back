from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Medico
from .serializers import MedicoSerializer
from .filters import MedicoFilter

class MedicoPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all().order_by('-fecha_registro')
    serializer_class = MedicoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MedicoFilter
    pagination_class = MedicoPagination

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
        medico = serializer.save()
        return Response({
            "id": medico.id,
            "message": "Medico/a creado exitosamente"
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        medico = self.get_object()
        medico.activo = False
        medico.save()
        return Response({"message": "Medico/a eliminado exitosamente"}, status=status.HTTP_200_OK)
    
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
            "message": "Medico/a actualizado exitosamente"
        })