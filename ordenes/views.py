from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Orden
from .serializers import OrdenSerializer
from .filters import OrdenesFilter

class OrdenesPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 1000

class OrdenViewSet(viewsets.ModelViewSet):
    queryset = Orden.objects.all().order_by('-fecha', '-hora')
    serializer_class = OrdenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrdenesFilter
    pagination_class = OrdenesPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
