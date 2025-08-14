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
from rest_framework import viewsets, status, serializers
from .models import Donante, Entrevista, UnidadMuestra,Lote
from .serializers import DonanteSerializer,  EntrevistaSerializer, UnidadMuestraSerializer, LoteSerializer, ActualizarEstadoDonanteSerializer
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .filters import DonanteFilter, UnidadMuestraFilter
from django_filters.rest_framework import DjangoFilterBackend

# Importar configuración segura de WeasyPrint
try:
    from weasyprint_docker_config import generate_pdf_docker_safe, generate_pdf_with_fallback
    WEASYPRINT_DOCKER = True
except ImportError:
    try:
        from weasyprint_config import generate_pdf_safe
        WEASYPRINT_DOCKER = False
        WEASYPRINT_SAFE = True
    except ImportError:
        WEASYPRINT_DOCKER = False
        WEASYPRINT_SAFE = False
        print("⚠️ Configuraciones de WeasyPrint no encontradas, usando configuración por defecto")

class DonantePagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class DonanteViewSet(viewsets.ModelViewSet):
    queryset = Donante.objects.all().order_by('id')  # Agregado ordenamiento para evitar warning de paginación
    serializer_class = DonanteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DonanteFilter
    pagination_class = DonantePagination


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
    ).order_by('-fecha_creacion')  # Agregado ordenamiento
    serializer_class = EntrevistaSerializer

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva entrevista con correlativo único.
        Maneja registros simultáneos sin duplicados.
        """
        from django.db import transaction
        from django.utils import timezone
        from datetime import datetime
        import threading
        
        # Usar un lock para evitar duplicados en registros simultáneos
        lock = threading.Lock()
        
        with lock:
            with transaction.atomic():
                # Generar correlativo único
                fecha_actual = timezone.now().date()
                formato_fecha = fecha_actual.strftime('%Y%m%d')
                
                # Buscar el último correlativo del día
                ultimo_correlativo = Entrevista.objects.filter(
                    correlativo__startswith=f'ENT-{formato_fecha}'
                ).order_by('-correlativo').first()
                
                if ultimo_correlativo:
                    # Extraer el número del último correlativo
                    try:
                        ultimo_numero = int(ultimo_correlativo.correlativo.split('-')[-1])
                        nuevo_numero = ultimo_numero + 1
                    except (ValueError, IndexError):
                        nuevo_numero = 1
                else:
                    nuevo_numero = 1
                
                # Crear el nuevo correlativo
                nuevo_correlativo = f'ENT-{formato_fecha}-{nuevo_numero:04d}'
                
                # Verificar que no exista (doble verificación)
                if Entrevista.objects.filter(correlativo=nuevo_correlativo).exists():
                    raise serializers.ValidationError(
                        f"Error: El correlativo {nuevo_correlativo} ya existe."
                    )
                
                # Agregar el correlativo al request data
                data = request.data.copy()
                data['correlativo'] = nuevo_correlativo
                
                # Procesar campos de fecha y hora
                if 'fecha' in data:
                    fecha_str = data['fecha']
                    if isinstance(fecha_str, str):
                        if 'T' in fecha_str:
                            # Formato ISO con tiempo
                            fecha_obj = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            data['fecha'] = fecha_obj.date()
                        else:
                            # Solo fecha
                            data['fecha'] = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                
                if 'fecha_creacion' in data:
                    fecha_creacion_str = data['fecha_creacion']
                    if isinstance(fecha_creacion_str, str):
                        if 'T' in fecha_creacion_str:
                            # Formato ISO con tiempo
                            fecha_creacion_obj = datetime.fromisoformat(fecha_creacion_str.replace('Z', '+00:00'))
                            data['fecha_creacion'] = fecha_creacion_obj
                        else:
                            # Solo fecha
                            data['fecha_creacion'] = datetime.strptime(fecha_creacion_str, '%Y-%m-%d')
                else:
                    data['fecha_creacion'] = timezone.now()
                
                # Procesar campos de hora
                for campo_hora in ['hora_inicio_flebotomia', 'hora_finalizacion_flebotomia']:
                    if campo_hora in data and data[campo_hora]:
                        hora_str = data[campo_hora]
                        if isinstance(hora_str, str):
                            try:
                                # Formato HH:MM
                                hora_obj = datetime.strptime(hora_str, '%H:%M').time()
                                data[campo_hora] = hora_obj
                            except ValueError:
                                # Si no es formato HH:MM, usar hora actual
                                data[campo_hora] = timezone.now().time()
                
                # Procesar cantidad_sangre
                if 'cantidad_sangre' in data:
                    cantidad = data['cantidad_sangre']
                    if isinstance(cantidad, str):
                        try:
                            data['cantidad_sangre'] = int(cantidad)
                        except ValueError:
                            data['cantidad_sangre'] = 350  # Valor por defecto
                
                # Crear la entrevista
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                entrevista = serializer.save()
                
                # Actualizar la orden para marcar que se generó entrevista
                if entrevista.orden:
                    entrevista.orden.genero_entrevista = True
                    entrevista.orden.save(update_fields=['genero_entrevista'])
                    print(f"✅ Orden {entrevista.orden.id} actualizada: genero_entrevista = True")
                
                # Generar PDF de la entrevista
                try:
                    config = ConfiguracionLaboratorio.objects.first()
                    
                    # Obtener la ruta absoluta del logo si existe
                    logo_path = None
                    if config and config.logo:
                        logo_path = os.path.join(settings.MEDIA_ROOT, config.logo.name)
                    
                    html_string = render_to_string(
                        'banco_sangre/entrevista_pdf.html',
                        {
                            'entrevista': entrevista,
                            'config': config,
                            'logo_path': logo_path
                        }
                    )
                    
                    # Crear directorio para el donante
                    donante_dir = os.path.join(settings.MEDIA_ROOT, 'entrevistas', str(entrevista.donante.id))
                    os.makedirs(donante_dir, exist_ok=True)
                    
                    # Generar nombre del archivo PDF
                    pdf_filename = f'entrevista_{entrevista.correlativo}.pdf'
                    pdf_path = os.path.join(donante_dir, pdf_filename)
                    
                    # Generar PDF con configuración mejorada para evitar errores de fuentes
                    try:
                        if WEASYPRINT_DOCKER:
                            # Usar configuración específica para Docker
                            success, message = generate_pdf_with_fallback(
                                html_string=html_string,
                                output_path=pdf_path,
                                base_url=None  # No usar base_url para evitar peticiones HTTP
                            )
                            
                            if success:
                                # Guardar la ruta en la base de datos
                                relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                                entrevista.pdf_entrevista = relative_path
                                entrevista.save(update_fields=['pdf_entrevista'])
                                print(f"✅ {message}")
                            else:
                                print(f"⚠️ {message}")
                        elif WEASYPRINT_SAFE:
                            # Usar configuración segura de WeasyPrint
                            success, message = generate_pdf_safe(
                                html_string=html_string,
                                output_path=pdf_path,
                                base_url=None  # No usar base_url para evitar peticiones HTTP
                            )
                            
                            if success:
                                # Guardar la ruta en la base de datos
                                relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                                entrevista.pdf_entrevista = relative_path
                                entrevista.save(update_fields=['pdf_entrevista'])
                                print(f"✅ {message}")
                            else:
                                print(f"⚠️ {message}")
                        else:
                            # Configuración por defecto con manejo de errores
                            import logging
                            logging.getLogger('weasyprint').setLevel(logging.ERROR)
                            
                            # Generar PDF con configuración mínima
                            HTML(
                                string=html_string, 
                                base_url=None  # No usar base_url para evitar peticiones HTTP
                            ).write_pdf(
                                pdf_path,
                                optimize_size=('fonts', 'images'),
                                font_config=None  # Usar configuración por defecto
                            )
                            
                            # Guardar la ruta en la base de datos
                            relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                            entrevista.pdf_entrevista = relative_path
                            entrevista.save(update_fields=['pdf_entrevista'])
                            
                            print(f"✅ PDF generado: {pdf_path}")
                        
                    except Exception as pdf_error:
                        print(f"⚠️ Error específico generando PDF: {pdf_error}")
                        # Continuar sin PDF si hay error
                        pass
                    
                except Exception as e:
                    print(f"⚠️ Error general en proceso de PDF: {e}")
                    # Continuar sin PDF si hay error
                    pass
                
                print(f"✅ Entrevista creada con correlativo: {nuevo_correlativo}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        """
        Descarga el PDF de la entrevista
        """
        entrevista = self.get_object()
        
        if not entrevista.pdf_entrevista:
            return Response(
                {"error": "No se ha generado el PDF para esta entrevista."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Construir la URL completa del archivo
        file_url = request.build_absolute_uri(entrevista.pdf_entrevista.url)
        
        return Response({
            "pdf_url": file_url,
            "correlativo": entrevista.correlativo,
            "donante": f"{entrevista.primer_nombre} {entrevista.primer_apellido}"
        })

    @action(detail=True, methods=['post'], url_path='actualizar-estado-donante')
    def actualizar_estado_donante(self, request, pk=None):
        """
        Actualiza el estado del donante basado en la entrevista.
        Permite aprobar o denegar la aptitud para donación.
        """
        entrevista = self.get_object()
        donante = entrevista.donante
        
        # Validar datos con el serializer
        serializer = ActualizarEstadoDonanteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener datos validados
            apto_donacion = serializer.validated_data['apto_donacion']
            tiene_entrevista_apro = serializer.validated_data['tiene_entrevista_apro']
            
            # Actualizar el donante
            donante.apto_donacion = apto_donacion
            donante.tiene_entrevista_apro = tiene_entrevista_apro
            donante.save(update_fields=['apto_donacion', 'tiene_entrevista_apro'])
            
            # Actualizar el estado de la entrevista
            nuevo_estado = "aprobada" if apto_donacion else "rechazada"
            entrevista.estado = nuevo_estado
            entrevista.save(update_fields=['estado'])
            
            return Response({
                "mensaje": f"Estado del donante actualizado exitosamente",
                "donante": {
                    "id": donante.id,
                    "cui": donante.cui,
                    "nombre": f"{donante.primer_nombre} {donante.primer_apellido}",
                    "apto_donacion": donante.apto_donacion,
                    "tiene_entrevista_apro": donante.tiene_entrevista_apro
                },
                "entrevista": {
                    "id": entrevista.id,
                    "correlativo": entrevista.correlativo,
                    "estado": entrevista.estado
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error al actualizar el estado del donante: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UnidadMuestraPagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class UnidadMuestraViewSet(viewsets.ModelViewSet):
    queryset = UnidadMuestra.objects.all().order_by('-creado')  # Agregado ordenamiento para evitar warning de paginación
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

        # Obtener la ruta absoluta del logo si existe
        logo_path = None
        if config and config.logo:
            logo_path = os.path.join(settings.MEDIA_ROOT, config.logo.name)

        html_string = render_to_string(
            'banco_sangre/etiqueta_uni.html',
            {
                'unidad': unidad,
                'config': config,
                'barcode_base64': barcode_base64,
                'serologias': serologias,
                'logo_path': logo_path
            }
        )

        output_dir = os.path.join(settings.MEDIA_ROOT, 'etiquetas')
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f'etiqueta_unidad_{pk}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        HTML(string=html_string, base_url=None).write_pdf(pdf_path)  # No usar base_url para evitar peticiones HTTP

        # Devuelve la URL relativa
        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}etiquetas/{pdf_filename}')
        return Response({'file_url': file_url})