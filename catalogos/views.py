from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import models
from .models import CatalogoUnidadParametro
from .serializers import CatalogoUnidadParametroSerializer

class CatalogoUnidadParametroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el catálogo de unidades de parámetros.
    Permite CRUD completo para las unidades de medida utilizadas en laboratorio.
    """
    queryset = CatalogoUnidadParametro.objects.all()
    serializer_class = CatalogoUnidadParametroSerializer
    
    def get_queryset(self):
        """Filtra por categoría y estado activo si se especifica"""
        queryset = CatalogoUnidadParametro.objects.all()
        
        # Filtro por categoría
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            queryset = queryset.filter(categoria__icontains=categoria)
        
        # Filtro por estado activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo_bool)
        
        return queryset.order_by('categoria', 'nombre')
    
    @action(detail=False, methods=['get'], url_path='categorias')
    def categorias(self, request):
        """
        Obtiene todas las categorías disponibles de unidades.
        """
        categorias = CatalogoUnidadParametro.objects.values_list(
            'categoria', flat=True
        ).distinct().order_by('categoria')
        
        return Response({
            'categorias': list(categorias)
        })
    
    @action(detail=False, methods=['get'], url_path='por-categoria')
    def por_categoria(self, request):
        """
        Agrupa las unidades por categoría.
        """
        from django.db.models import Count
        
        categorias = CatalogoUnidadParametro.objects.values('categoria').annotate(
            total_unidades=Count('id'),
            unidades_activas=Count('id', filter=models.Q(activo=True))
        ).order_by('categoria')
        
        return Response({
            'categorias': list(categorias)
        })
    
    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        """
        Busca unidades por nombre, símbolo o código.
        """
        termino = request.query_params.get('q', '')
        if not termino:
            return Response({'error': 'Se requiere el parámetro "q" para buscar'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        queryset = CatalogoUnidadParametro.objects.filter(
            models.Q(nombre__icontains=termino) |
            models.Q(simbolo__icontains=termino) |
            models.Q(codigo__icontains=termino)
        ).filter(activo=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'termino': termino,
            'resultados': serializer.data,
            'total': queryset.count()
        })