from rest_framework import viewsets,status
from .models import Examen
from .serializers import ExamenSerializer
from .filters import ExamenesFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

class ExamenesPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class ExamenViewSet(viewsets.ModelViewSet):
    queryset = Examen.objects.all().order_by('-fecha_creacion')
    serializer_class = ExamenSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExamenesFilter
    pagination_class = ExamenesPagination

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
        examen = serializer.save()
        return Response({
            "id": examen.id,
            "message": "Examen creado exitosamente"
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "id": serializer.instance.id,
            "message": "Examen actualizado exitosamente"
        })
    
    def destroy(self, request, *args, **kwargs):
        examen = self.get_object()
        examen.activo = False
        examen.save()
        return Response({"message": "Examen eliminado exitosamente"}, status=status.HTTP_200_OK)