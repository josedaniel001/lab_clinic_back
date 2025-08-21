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
from .models import Donante, Entrevista, UnidadMuestra, Lote, SalidaUnidad, DetalleSalida
from .serializers import (
    DonanteSerializer, EntrevistaSerializer, UnidadMuestraSerializer, 
    LoteSerializer, ActualizarEstadoDonanteSerializer, SalidaUnidadSerializer,
    SalidaUnidadListSerializer, DetalleSalidaSerializer, DetalleSalidaListSerializer
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .filters import DonanteFilter, UnidadMuestraFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

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
    
    @action(detail=True, methods=['get'], url_path='historial-codigos')
    def historial_codigos(self, request, pk=None):
        """Obtener el historial completo de códigos del donante"""
        donante = self.get_object()
        
        historial = donante.historial_codigos or []
        
        return Response({
            'donante_id': donante.id,
            'donante_nombre': f"{donante.primer_nombre} {donante.primer_apellido}",
            'codigo_actual': donante.codigo_donante,
            'total_codigos': len(historial) + (1 if donante.codigo_donante else 0),
            'historial': historial,
            'fecha_ultima_donacion': donante.fecha_ultima_donacion,
            'puede_crear_nueva_orden': donante.puede_crear_nueva_orden(),
            'dias_restantes': donante.dias_restantes_para_nueva_orden()
        })
    
    @action(detail=True, methods=['post'], url_path='generar-nuevo-codigo')
    def generar_nuevo_codigo(self, request, pk=None):
        """Generar un nuevo código para el donante (solo para administradores)"""
        donante = self.get_object()
        
        # Verificar que el usuario sea administrador
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo los administradores pueden generar nuevos códigos manualmente'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            nuevo_codigo = donante.generar_nuevo_codigo_para_orden()
            
            return Response({
                'mensaje': 'Nuevo código generado exitosamente',
                'nuevo_codigo': nuevo_codigo,
                'donante': {
                    'id': donante.id,
                    'nombre': f"{donante.primer_nombre} {donante.primer_apellido}",
                    'codigo_actual': donante.codigo_donante,
                    'total_codigos_historial': len(donante.historial_codigos)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error generando nuevo código: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='actualizar-fecha-donacion')
    def actualizar_fecha_donacion(self, request, pk=None):
        """Actualizar la fecha de última donación (solo para administradores)"""
        donante = self.get_object()
        
        # Verificar que el usuario sea administrador
        if not request.user.is_staff:
            return Response(
                {'error': 'Solo los administradores pueden actualizar la fecha de donación'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        fecha_donacion = request.data.get('fecha_donacion')
        if not fecha_donacion:
            return Response(
                {'error': 'Se requiere la fecha de donación'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            fecha = datetime.strptime(fecha_donacion, '%Y-%m-%d').date()
            donante.actualizar_fecha_ultima_donacion(fecha)
            
            return Response({
                'mensaje': 'Fecha de última donación actualizada exitosamente',
                'donante': {
                    'id': donante.id,
                    'nombre': f"{donante.primer_nombre} {donante.primer_apellido}",
                    'fecha_ultima_donacion': donante.fecha_ultima_donacion,
                    'puede_crear_nueva_orden': donante.puede_crear_nueva_orden(),
                    'dias_restantes': donante.dias_restantes_para_nueva_orden()
                }
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error actualizando fecha: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
                    raise serializers.ValidationError("Error: Correlativo duplicado generado")
                
                # Agregar el correlativo a los datos
                data = request.data.copy()
                data['correlativo'] = nuevo_correlativo
                
                # Continuar con la creación normal
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                entrevista = serializer.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='generar-pdf')
    def generar_pdf(self, request, pk=None):
        """
        Genera un PDF de la entrevista
        """
        entrevista = self.get_object()
        config = ConfiguracionLaboratorio.objects.first()
        
        # Generar HTML de la entrevista
        html_string = render_to_string(
            'banco_sangre/entrevista_pdf.html',
            {
                'entrevista': entrevista,
                'config': config,
            }
        )

        # Crear directorio por donante si no existe
        donante_id = entrevista.donante.id if entrevista.donante else 'sin_donante'
        output_dir = os.path.join(settings.MEDIA_ROOT, 'entrevistas', str(donante_id))
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        pdf_filename = f'entrevista_{entrevista.correlativo}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        try:
            if WEASYPRINT_DOCKER:
                # Usar configuración Docker optimizada
                success, message = generate_pdf_docker_safe(html_string, pdf_path)
                if not success:
                    raise Exception(f"Error generando PDF: {message}")
            elif WEASYPRINT_SAFE:
                # Usar configuración segura de WeasyPrint
                success, message = generate_pdf_safe(html_string, pdf_path)
                if not success:
                    raise Exception(f"Error generando PDF: {message}")
            else:
                # Usar configuración por defecto
                HTML(string=html_string, base_url=None).write_pdf(pdf_path)
            
            # Guardar la ruta del PDF en la entrevista
            entrevista.pdf_entrevista = f'entrevistas/{donante_id}/{pdf_filename}'
            entrevista.save()
            
            # Configurar logging para WeasyPrint
            import logging
            logging.getLogger('weasyprint').setLevel(logging.ERROR)
            
            # Devolver la URL del archivo
            file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}entrevistas/{donante_id}/{pdf_filename}')
            return Response({
                'file_url': file_url,
                'mensaje': 'PDF generado exitosamente'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get', 'post'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        """
        Descarga el PDF de la entrevista si ya existe
        Acepta tanto GET como POST
        """
        entrevista = self.get_object()
        
        if not entrevista.pdf_entrevista:
            return Response(
                {'error': 'No hay PDF generado para esta entrevista. Use /generar-pdf/ primero.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el archivo existe
        pdf_path = os.path.join(settings.MEDIA_ROOT, entrevista.pdf_entrevista.name)
        if not os.path.exists(pdf_path):
            return Response(
                {'error': 'El archivo PDF no existe en el servidor'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Devolver la URL del archivo
        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{entrevista.pdf_entrevista.name}')
        return Response({
            'file_url': file_url,
            'mensaje': 'PDF disponible para descarga',
            'pdf_existe': True
        })

    @action(detail=True, methods=['get'], url_path='pdf-url')
    def pdf_url(self, request, pk=None):
        """
        Obtiene la URL del PDF de la entrevista (endpoint simple)
        """
        entrevista = self.get_object()
        
        if not entrevista.pdf_entrevista:
            return Response(
                {'error': 'No hay PDF generado para esta entrevista'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Devolver la URL del archivo
        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{entrevista.pdf_entrevista.name}')
        return Response({
            'file_url': file_url,
            'pdf_existe': True
        })

    @action(detail=True, methods=['get'], url_path='pdfs-donante')
    def pdfs_donante(self, request, pk=None):
        """
        Obtiene todos los PDFs de entrevistas del donante asociado
        """
        entrevista = self.get_object()
        
        if not entrevista.donante:
            return Response(
                {'error': 'Esta entrevista no tiene donante asociado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtener todas las entrevistas del mismo donante que tengan PDF
        entrevistas_con_pdf = Entrevista.objects.filter(
            donante=entrevista.donante,
            pdf_entrevista__isnull=False
        ).exclude(pdf_entrevista='')
        
        pdfs_info = []
        for ent in entrevistas_con_pdf:
            if ent.pdf_entrevista:
                file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{ent.pdf_entrevista.name}')
                pdfs_info.append({
                    'entrevista_id': ent.id,
                    'correlativo': ent.correlativo,
                    'fecha_creacion': ent.fecha_creacion,
                    'file_url': file_url,
                    'pdf_path': ent.pdf_entrevista.name
                })
        
        return Response({
            'donante_id': entrevista.donante.id,
            'donante_nombre': f"{entrevista.donante.primer_nombre} {entrevista.donante.primer_apellido}",
            'total_pdfs': len(pdfs_info),
            'pdfs': pdfs_info
        })

    @action(detail=True, methods=['post'], url_path='actualizar-estado-donante')
    def actualizar_estado_donante(self, request, pk=None):
        """
        Actualiza el estado del donante basado en la entrevista
        """
        entrevista = self.get_object()
        serializer = ActualizarEstadoDonanteSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                donante = entrevista.donante
                apto_donacion = serializer.validated_data['apto_donacion']
                tiene_entrevista_apro = serializer.validated_data['tiene_entrevista_apro']
                
                # Actualizar estado del donante
                donante.apto_donacion = apto_donacion
                donante.tiene_entrevista_apro = tiene_entrevista_apro
                donante.save()
                
                # Actualizar estado de la entrevista
                if apto_donacion:
                    entrevista.estado = 'aprobada'
                else:
                    entrevista.estado = 'rechazada'
                entrevista.save()
                
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
        else:
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
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
        
        # Usar el código del donante en lugar del ID para el código de barras
        codigo_etiqueta = unidad.correlativo
        if unidad.donante and unidad.donante.codigo_donante:
            codigo_etiqueta = unidad.donante.codigo_donante
        
        barcode_class = barcode.get_barcode_class('code128')
        barcode_image = barcode_class(codigo_etiqueta, writer=ImageWriter())
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
                'logo_path': logo_path,
                'codigo_etiqueta': codigo_etiqueta
            }
        )

        output_dir = os.path.join(settings.MEDIA_ROOT, 'etiquetas')
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f'etiqueta_unidad_{pk}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        HTML(string=html_string, base_url=None).write_pdf(pdf_path)

        # Devuelve la URL relativa
        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}etiquetas/{pdf_filename}')
        return Response({'file_url': file_url})
    
    @action(detail=True, methods=['post'], url_path='regenerar-etiqueta')
    def regenerar_etiqueta(self, request, pk=None):
        """Regenerar la etiqueta de la unidad"""
        unidad = self.get_object()
        
        try:
            # Limpiar etiqueta anterior si existe
            if unidad.etiqueta_pdf:
                # Eliminar archivo anterior
                try:
                    os.remove(os.path.join(settings.MEDIA_ROOT, unidad.etiqueta_pdf.name))
                except:
                    pass
                unidad.etiqueta_pdf = None
                unidad.save()
            
            # Generar nueva etiqueta
            unidad.generar_etiqueta_automatica()
            unidad.refresh_from_db()
            
            # Obtener URL de la nueva etiqueta
            if unidad.etiqueta_pdf:
                file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{unidad.etiqueta_pdf.name}')
                return Response({
                    'mensaje': 'Etiqueta regenerada exitosamente',
                    'file_url': file_url
                })
            else:
                return Response({
                    'error': 'No se pudo generar la etiqueta'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': f'Error regenerando etiqueta: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SalidaUnidadViewSet(viewsets.ModelViewSet):
    """ViewSet para manejar las salidas de unidades de muestra"""
    
    queryset = SalidaUnidad.objects.select_related(
        'tecnico_salida', 
        'aprobado_por'
    ).prefetch_related(
        'detalles__unidad',
        'detalles__unidad__donante',
        'detalles__unidad__lote'
    ).order_by('-fecha_creacion')
    filter_backends = [DjangoFilterBackend]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalidaUnidadListSerializer
        return SalidaUnidadSerializer
    
    def get_queryset(self):
        """Filtrar por estado si se especifica"""
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crear una nueva salida asegurando que se registre el usuario actual"""
        # Asegurar que el usuario esté autenticado
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Debe estar autenticado para crear una salida'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Crear una copia de los datos para no modificar el request original
        data = request.data.copy()
        
        # Agregar el usuario actual como técnico de salida si no se especifica
        if 'tecnico_salida' not in data:
            data['tecnico_salida'] = request.user.id
        
        # Crear un nuevo request con los datos modificados
        request._full_data = data
        
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'], url_path='aprobar')
    def aprobar(self, request, pk=None):
        """Aprobar una salida de unidades"""
        salida = self.get_object()
        
        if salida.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden aprobar salidas pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        salida.estado = 'APROBADA'
        salida.fecha_aprobacion = timezone.now()
        salida.aprobado_por = request.user
        salida.save()
        
        return Response({
            'mensaje': 'Salida aprobada exitosamente',
            'salida': SalidaUnidadSerializer(salida, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        """Rechazar una salida de unidades"""
        salida = self.get_object()
        
        if salida.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden rechazar salidas pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Revertir el estado de las unidades a DISPONIBLE
        for detalle in salida.detalles.all():
            if detalle.unidad.estado == 'ENTREGADA':
                detalle.unidad.estado = 'DISPONIBLE'
                detalle.unidad.save()
        
        salida.estado = 'RECHAZADA'
        salida.save()
        
        return Response({
            'mensaje': 'Salida rechazada exitosamente',
            'salida': SalidaUnidadSerializer(salida, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'], url_path='completar')
    def completar(self, request, pk=None):
        """Completar una salida (marcar como entregada)"""
        salida = self.get_object()
        
        if salida.estado != 'APROBADA':
            return Response(
                {'error': 'Solo se pueden completar salidas aprobadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        salida.estado = 'COMPLETADA'
        salida.save()
        
        return Response({
            'mensaje': 'Salida completada exitosamente',
            'salida': SalidaUnidadSerializer(salida, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'], url_path='generar-pdf')
    def generar_pdf(self, request, pk=None):
        """Generar PDF de la salida con firma"""
        salida = self.get_object()
        config = ConfiguracionLaboratorio.objects.first()
        
        # Generar HTML de la salida
        html_string = render_to_string(
            'banco_sangre/salida_pdf.html',
            {
                'salida': salida,
                'config': config,
                'detalles': salida.detalles.all(),
            }
        )

        # Crear directorio si no existe
        output_dir = os.path.join(settings.MEDIA_ROOT, 'salidas')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar nombre de archivo único
        pdf_filename = f'salida_{salida.correlativo}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        try:
            if WEASYPRINT_DOCKER:
                success, message = generate_pdf_docker_safe(html_string, pdf_path)
                if not success:
                    raise Exception(f"Error generando PDF: {message}")
            elif WEASYPRINT_SAFE:
                success, message = generate_pdf_safe(html_string, pdf_path)
                if not success:
                    raise Exception(f"Error generando PDF: {message}")
            else:
                HTML(string=html_string, base_url=None).write_pdf(pdf_path)
            
            # Guardar la ruta del PDF en la salida
            salida.pdf_salida = f'salidas/{pdf_filename}'
            salida.save()
            
            # Devolver la URL del archivo
            file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}salidas/{pdf_filename}')
            return Response({
                'file_url': file_url,
                'mensaje': 'PDF de salida generado exitosamente'
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='agregar-firma')
    def agregar_firma(self, request, pk=None):
        """Agregar firma a la salida"""
        salida = self.get_object()
        tipo_firma = request.data.get('tipo_firma')  # 'receptor' o 'tecnico'
        firma_data = request.data.get('firma')
        
        if not firma_data:
            return Response(
                {'error': 'Se requiere la firma'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if tipo_firma == 'receptor':
            salida.firma_receptor = firma_data
        elif tipo_firma == 'tecnico':
            salida.firma_tecnico = firma_data
        else:
            return Response(
                {'error': 'Tipo de firma inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        salida.save()
        
        return Response({
            'mensaje': f'Firma de {tipo_firma} agregada exitosamente',
            'salida': SalidaUnidadSerializer(salida, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'], url_path='unidades-disponibles')
    def unidades_disponibles(self, request):
        """Obtener unidades disponibles para salida"""
        unidades = UnidadMuestra.objects.filter(estado='DISPONIBLE').order_by('fecha_caducidad')
        
        # Filtrar por tipo si se especifica
        tipo_unidad = request.query_params.get('tipo_unidad', None)
        if tipo_unidad:
            unidades = unidades.filter(tipo_unidad=tipo_unidad)
        
        # Filtrar por tipo de sangre si se especifica
        tipo_sangre = request.query_params.get('tipo_sangre', None)
        if tipo_sangre:
            unidades = unidades.filter(tipo_sangre=tipo_sangre)
        
        serializer = UnidadMuestraSerializer(unidades, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='unidades')
    def unidades_salida(self, request, pk=None):
        """Obtener las unidades incluidas en una salida específica"""
        salida = self.get_object()
        detalles = salida.detalles.select_related('unidad').all()
        
        # Aplicar filtros si se especifican
        tipo_unidad = request.query_params.get('tipo_unidad')
        tipo_sangre = request.query_params.get('tipo_sangre')
        
        if tipo_unidad:
            detalles = detalles.filter(unidad__tipo_unidad=tipo_unidad)
        if tipo_sangre:
            detalles = detalles.filter(unidad__tipo_sangre=tipo_sangre)
        
        # Serializar los detalles con información completa de las unidades
        serializer = DetalleSalidaSerializer(detalles, many=True, context={'request': request})
        
        # Calcular estadísticas de las unidades filtradas
        total_unidades_filtradas = detalles.count()
        volumen_total = sum(detalle.unidad.volumen_ml for detalle in detalles)
        
        # Agregar información adicional
        response_data = {
            'salida_id': salida.id,
            'salida_correlativo': salida.correlativo,
            'total_unidades': salida.total_unidades,
            'total_unidades_filtradas': total_unidades_filtradas,
            'volumen_total_ml': volumen_total,
            'unidades': serializer.data,
            'resumen_por_tipo': salida.unidades_por_tipo,
            'filtros_aplicados': {
                'tipo_unidad': tipo_unidad,
                'tipo_sangre': tipo_sangre
            }
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'], url_path='detalle-completo')
    def detalle_completo(self, request, pk=None):
        """Obtener el detalle completo de una salida con todas sus unidades"""
        salida = self.get_object()
        
        # Usar el serializer completo que incluye todos los detalles
        serializer = SalidaUnidadSerializer(salida, context={'request': request})
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """Obtener estadísticas de las salidas"""
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Obtener fecha de inicio (por defecto último mes)
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if not fecha_inicio:
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not fecha_fin:
            fecha_fin = datetime.now().strftime('%Y-%m-%d')
        
        # Filtrar salidas por fecha
        salidas = SalidaUnidad.objects.filter(
            fecha_creacion__date__range=[fecha_inicio, fecha_fin]
        )
        
        # Estadísticas por estado
        estadisticas_estado = salidas.values('estado').annotate(
            cantidad=Count('id')
        )
        
        # Estadísticas por técnico
        estadisticas_tecnico = salidas.values(
            'tecnico_salida__username', 
            'tecnico_salida__first_name',
            'tecnico_salida__last_name'
        ).annotate(
            cantidad_salidas=Count('id'),
            total_unidades=Count('detalles')
        ).exclude(tecnico_salida__isnull=True)
        
        # Total de unidades entregadas
        total_unidades = sum(salida.total_unidades for salida in salidas)
        
        # Unidades por tipo
        unidades_por_tipo = {}
        for salida in salidas:
            for detalle in salida.detalles.all():
                tipo = detalle.unidad.tipo_unidad
                if tipo not in unidades_por_tipo:
                    unidades_por_tipo[tipo] = 0
                unidades_por_tipo[tipo] += 1
        
        return Response({
            'periodo': {
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'total_salidas': salidas.count(),
            'total_unidades': total_unidades,
            'estadisticas_por_estado': list(estadisticas_estado),
            'estadisticas_por_tecnico': list(estadisticas_tecnico),
            'unidades_por_tipo': unidades_por_tipo
        })
    
    @action(detail=False, methods=['get'], url_path='debug-usuario')
    def debug_usuario(self, request):
        """Endpoint de debug para verificar información del usuario actual"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Usuario no autenticado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Obtener información del usuario actual
        usuario_info = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'get_full_name': request.user.get_full_name(),
            'is_staff': request.user.is_staff,
            'is_superuser': request.user.is_superuser,
        }
        
        # Obtener las últimas 5 salidas del usuario
        salidas_usuario = SalidaUnidad.objects.filter(
            tecnico_salida=request.user
        ).order_by('-fecha_creacion')[:5]
        
        salidas_info = []
        for salida in salidas_usuario:
            salidas_info.append({
                'id': salida.id,
                'correlativo': salida.correlativo,
                'tecnico_salida_id': salida.tecnico_salida.id if salida.tecnico_salida else None,
                'tecnico_salida_username': salida.tecnico_salida.username if salida.tecnico_salida else None,
                'tecnico_salida_nombre': salida.tecnico_salida.get_full_name() if salida.tecnico_salida else None,
                'fecha_creacion': salida.fecha_creacion,
                'estado': salida.estado
            })
        
        return Response({
            'usuario_actual': usuario_info,
            'ultimas_salidas': salidas_info,
            'total_salidas_usuario': SalidaUnidad.objects.filter(tecnico_salida=request.user).count()
        })
    
    @action(detail=False, methods=['get'], url_path='listar-con-unidades')
    def listar_con_unidades(self, request):
        """Listar salidas con información básica de unidades"""
        queryset = self.get_queryset()
        
        # Aplicar paginación si es necesario
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SalidaUnidadListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = SalidaUnidadListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='estadisticas-codigos')
    def estadisticas_codigos(self, request):
        """Obtener estadísticas de códigos de donantes"""
        from django.db.models import Count, Q
        
        # Estadísticas generales
        total_donantes = Donante.objects.count()
        donantes_con_codigo = Donante.objects.filter(codigo_donante__isnull=False).count()
        donantes_sin_codigo = total_donantes - donantes_con_codigo
        
        # Donantes que pueden crear nueva orden
        donantes_pueden_orden = sum(1 for d in Donante.objects.all() if d.puede_crear_nueva_orden())
        donantes_no_pueden_orden = total_donantes - donantes_pueden_orden
        
        # Estadísticas de historial de códigos
        donantes_con_historial = Donante.objects.filter(historial_codigos__isnull=False).exclude(historial_codigos=[]).count()
        
        # Promedio de códigos por donante
        total_codigos_historial = sum(len(d.historial_codigos or []) for d in Donante.objects.all())
        promedio_codigos = total_codigos_historial / total_donantes if total_donantes > 0 else 0
        
        # Donantes con fecha de última donación
        donantes_con_fecha = Donante.objects.filter(fecha_ultima_donacion__isnull=False).count()
        
        return Response({
            'estadisticas_generales': {
                'total_donantes': total_donantes,
                'donantes_con_codigo': donantes_con_codigo,
                'donantes_sin_codigo': donantes_sin_codigo,
                'porcentaje_con_codigo': (donantes_con_codigo / total_donantes * 100) if total_donantes > 0 else 0
            },
            'estadisticas_ordenes': {
                'pueden_crear_orden': donantes_pueden_orden,
                'no_pueden_crear_orden': donantes_no_pueden_orden,
                'porcentaje_pueden_orden': (donantes_pueden_orden / total_donantes * 100) if total_donantes > 0 else 0
            },
            'estadisticas_historial': {
                'donantes_con_historial': donantes_con_historial,
                'total_codigos_historial': total_codigos_historial,
                'promedio_codigos_por_donante': round(promedio_codigos, 2)
            },
            'estadisticas_fechas': {
                'donantes_con_fecha_donacion': donantes_con_fecha,
                'donantes_sin_fecha_donacion': total_donantes - donantes_con_fecha
            }
        })