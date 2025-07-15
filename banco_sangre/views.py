# banco_sangre/views.py
from rest_framework.decorators import action
from django.template.loader import render_to_string
from weasyprint import HTML
import barcode
from barcode.writer import ImageWriter
import base64
import os
import io
from django.conf import settings
from sistema.models import ConfiguracionLaboratorio
from rest_framework import viewsets,status
from .models import Donante, Entrevista, UnidadMuestra,Lote
from .serializers import DonanteSerializer,  EntrevistaSerializer, UnidadMuestraSerializer, LoteSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .filters import UnidadMuestraFilter
from django_filters.rest_framework import DjangoFilterBackend

class DonanteViewSet(viewsets.ModelViewSet):
    queryset = Donante.objects.all()
    serializer_class = DonanteSerializer


class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer
# banco_sangre/views.py

class EntrevistaViewSet(viewsets.ModelViewSet):
    queryset = Entrevista.objects.select_related(
        'donante', 'orden'
    ).prefetch_related(
        'orden__detalleorden_set',
        'orden__detalleorden_set__examen'
    )
    serializer_class = EntrevistaSerializer

class UnidadMuestraPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class UnidadMuestraViewSet(viewsets.ModelViewSet):
    queryset = UnidadMuestra.objects.all()
    serializer_class = UnidadMuestraSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UnidadMuestraFilter
    pagination_class = UnidadMuestraPagination

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)

        unidades = serializer.save()

        # Refrescar para cada unidad (correlativo)
        if is_many:
            for unidad in unidades:
                unidad.refresh_from_db()
        else:
            unidades.refresh_from_db()

        response_serializer = self.get_serializer(unidades, many=is_many)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='generar-etiqueta')   
    def generar_etiqueta(self, request, pk=None):
        unidad = self.get_object()
        config = ConfiguracionLaboratorio.objects.first()
        serologias = unidad.serologias or {}
        
        if not serologias:
            serologias = {
                "Syphilis": "No Reactivo",
                "HIV Ab/Ag": "No Reactivo",
                "Chagas": "No Reactivo",
                "Anti-HBc": "No Reactivo",
                "HBsAg": "No Reactivo",
                "Anti-HCV": "No Reactivo"
            }
        barcode_class = barcode.get_barcode_class('code128')
        barcode_image = barcode_class(unidad.correlativo, writer=ImageWriter())

        buffer = io.BytesIO()
        barcode_image.write(buffer)
        barcode_base64 = base64.b64encode(buffer.getvalue()).decode()

        html_string = render_to_string(
            'banco_sangre/etiqueta_uni.html',
            {
                'unidad': unidad,
                'config': config,
                'barcode_base64': barcode_base64,
                'serologias': serologias
            }
        )

        output_dir = os.path.join(settings.MEDIA_ROOT, 'etiquetas')
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f'etiqueta_unidad_{pk}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(pdf_path)

        # Devuelve la URL relativa
        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}etiquetas/{pdf_filename}')
        return Response({'file_url': file_url})