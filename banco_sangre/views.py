# banco_sangre/views.py
from rest_framework.decorators import action
from django.template.loader import render_to_string, get_template
from weasyprint import HTML
import barcode
from barcode.writer import ImageWriter
import base64
import os
import io
import hashlib
from django.conf import settings
from django.utils import timezone
from sistema.models import ConfiguracionLaboratorio

# ============ CONFIG ============
ENTREVISTA_TEMPLATE = 'banco_sangre/entrevista_pdf.html'  # ÚNICO template

def _si_no(d):
    """Devuelve dict con 'Sí'/'No' a partir de booleans sin tocar los originales."""
    return {k: ('Sí' if v is True else 'No' if v is False else '') for k, v in (d or {}).items()}

def _template_signature(template_name: str) -> str:
    """Hash corto del template; cambia si cambias el HTML/CSS."""
    try:
        tpl = get_template(template_name)
        src = getattr(tpl.template, "source", str(tpl.template))
        return hashlib.sha1(src.encode('utf-8')).hexdigest()[:8]
    except Exception:
        return "nosig"

def _resolve_pdf_path(pdf_field):
    if not pdf_field:
        return None
    try:
        if hasattr(pdf_field, 'path'):
            return pdf_field.path
    except Exception:
        pass
    rel = getattr(pdf_field, 'name', None) or str(pdf_field)
    return os.path.join(settings.MEDIA_ROOT, rel)

def _resolve_pdf_url(request, pdf_field):
    if not pdf_field:
        return None
    try:
        if hasattr(pdf_field, 'url'):
            return request.build_absolute_uri(pdf_field.url)
    except Exception:
        pass
    rel = getattr(pdf_field, 'name', None) or str(pdf_field)
    return request.build_absolute_uri(f'{settings.MEDIA_URL}{rel}')
# =================================

def estandarizar_datos_entrevista(entrevista):
    # (puedes dejarla; ya no la usamos para checks)
    respuestas_estandarizadas = {}
    for k, v in (entrevista.respuestas_entrevista or {}).items():
        if isinstance(v, bool):
            respuestas_estandarizadas[k] = 'Sí' if v else 'No'
        elif v is None:
            respuestas_estandarizadas[k] = 'No'
        else:
            respuestas_estandarizadas[k] = str(v)

    respuestas_adicionales_estandarizadas = {}
    for k, v in (entrevista.respuestas_adicionales_entrevista or {}).items():
        if isinstance(v, bool):
            respuestas_adicionales_estandarizadas[k] = 'Sí' if v else 'No'
        elif v is None:
            respuestas_adicionales_estandarizadas[k] = ''
        else:
            respuestas_adicionales_estandarizadas[k] = str(v)

    respuestas_medicas_estandarizadas = {}
    for k, v in (entrevista.respuestas_medicas_adicionales or {}).items():
        if isinstance(v, bool):
            respuestas_medicas_estandarizadas[k] = 'Sí' if v else 'No'
        elif v is None:
            respuestas_medicas_estandarizadas[k] = 'No'
        else:
            respuestas_medicas_estandarizadas[k] = str(v)

    respuestas_mujeres_estandarizadas = {}
    if getattr(entrevista, "respuestas_mujeres", None):
        for k, v in (entrevista.respuestas_mujeres or {}).items():
            if isinstance(v, bool):
                respuestas_mujeres_estandarizadas[k] = 'Sí' if v else 'No'
            elif v is None:
                respuestas_mujeres_estandarizadas[k] = 'No'
            else:
                respuestas_mujeres_estandarizadas[k] = str(v)

    return {
        'respuestas_entrevista': respuestas_estandarizadas,
        'respuestas_adicionales_entrevista': respuestas_adicionales_estandarizadas,
        'respuestas_medicas_adicionales': respuestas_medicas_estandarizadas,
        'respuestas_mujeres': respuestas_mujeres_estandarizadas
    }

def _stringify_bool_or_value(value):
    if isinstance(value, bool):
        return 'Sí' if value else 'No'
    if value is None:
        return ''
    return str(value)

def extraer_respuestas_clave(entrevista):
    """Devuelve valores seguros para preguntas clave aunque el JSON use claves humanas."""
    raw = entrevista.respuestas_entrevista or {}
    std_all = estandarizar_datos_entrevista(entrevista)
    std = std_all.get('respuestas_entrevista', {})

    def pick(keys, human_key=None, default_value=''):
        # probar en estandarizados por claves técnicas
        for k in keys:
            v = std.get(k)
            if v:
                return v
        # probar en crudos por claves técnicas
        for k in keys:
            if k in raw:
                return _stringify_bool_or_value(raw.get(k))
        # probar por clave humana en estandarizados
        if human_key and human_key in std and std.get(human_key):
            return std.get(human_key)
        # probar por clave humana en crudos
        if human_key and human_key in raw:
            return _stringify_bool_or_value(raw.get(human_key))
        return default_value

    q1_tipo_donacion = pick(
        keys=['tipo_donacion', 'tipo', 'entrevista_hoy_es'],
        human_key='¿Su entrevista de Sangre hoy es?',
        default_value='Voluntaria'
    )
    q6_salud_hoy = pick(
        keys=['salud_hoy', 'como_se_siente_hoy', 'como_se_siente_hoy_salud'],
        human_key='¿Cómo se siente hoy de Salud?',
        default_value='Bien'
    )
    q8_durmio_6_horas = pick(
        keys=['durmio_6_horas', 'durmio_seis_horas', 'durmio_min_6_horas'],
        human_key='¿Anoche, durmió mínimo 6 horas?',
        default_value='Sí'
    )
    q9_desayuno_grasa = pick(
        keys=['desayuno_grasa', 'desayuno_con_grasa', 'desayuno_con_grasa_hoy'],
        human_key='¿Desayunó alimentos con grasa hoy?',
        default_value='No'
    )
    q10_medicamento_semana = pick(
        keys=['medicamento_semana', 'tomo_medicamento_semana'],
        human_key='¿Ha tomado algún medicamento en la última semana incluso aspirina?',
        default_value='No'
    )

    return {
        'q1_tipo_donacion': q1_tipo_donacion,
        'q6_salud_hoy': q6_salud_hoy,
        'q8_durmio_6_horas': q8_durmio_6_horas,
        'q9_desayuno_grasa': q9_desayuno_grasa,
        'q10_medicamento_semana': q10_medicamento_semana,
    }

def get_logo_data(config, request=None):
    if not config or not getattr(config, "logo", None) or not getattr(config, "mostrar_logo", False):
        return None
    try:
        logo_data = None
        if hasattr(config.logo, 'path') and os.path.exists(config.logo.path):
            with open(config.logo.path, 'rb') as f:
                logo_data = f.read()
        if not logo_data and hasattr(config.logo, 'read'):
            try:
                config.logo.seek(0)
                logo_data = config.logo.read()
            except Exception:
                logo_data = None
        if logo_data:
            b64 = base64.b64encode(logo_data).decode('utf-8')
            ext = os.path.splitext(config.logo.name)[1].lower()
            mime = 'image/png' if ext == '.png' else 'image/gif' if ext == '.gif' else 'image/jpeg'
            return f"data:{mime};base64,{b64}"
        else:
            if request and hasattr(config.logo, 'url'):
                return request.build_absolute_uri(config.logo.url)
            elif hasattr(config.logo, 'url'):
                return f"{request.scheme}://{request.get_host()}{config.logo.url}" if request else config.logo.url
            return None
    except Exception as e:
        print(f"Error al procesar logo: {e}")
        return None

def generate_pdf_with_fallback(html_string, output_path, base_url=None):
    try:
        import logging
        logging.getLogger('weasyprint').setLevel(logging.ERROR)
        HTML(string=html_string, base_url=base_url).write_pdf(
            output_path, optimize_size=('fonts', 'images'), font_config=None
        )
        return True, f"PDF generado: {output_path}"
    except Exception as e:
        print(f"Error en generate_pdf_with_fallback: {e}")
        return False, f"Error generando PDF: {str(e)}"

def generate_pdf_safe(html_string, output_path, base_url=None):
    try:
        import logging
        logging.getLogger('weasyprint').setLevel(logging.ERROR)
        HTML(string=html_string, base_url=base_url).write_pdf(
            output_path, optimize_size=('fonts', 'images'), font_config=None
        )
        return True, f"PDF generado: {output_path}"
    except Exception as e:
        print(f"Error en generate_pdf_safe: {e}")
        return False, f"Error generando PDF: {str(e)}"

# ==== imports DRF y vistas que ya tenías (sin cambios funcionales, salvo Entrevista) ====
from rest_framework import viewsets, status, serializers
from rest_framework.permissions import AllowAny
from .models import Donante, Entrevista, UnidadMuestra, Lote, CodigoDonante, CatalogoDescarte, DescarteMuestra, SalidaUnidad, DetalleaSalidaUnidad
from .serializers import (
    DonanteSerializer, EntrevistaSerializer, UnidadMuestraSerializer, LoteSerializer,
    CodigoDonanteSerializer, CatalogoDescarteSerializer, DescarteMuestraSerializer,
    DescarteMuestraCreateSerializer, ValidarDescarteSerializer, ActualizarEstadoDonanteSerializer,
    SalidaUnidadSerializer
)
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .filters import DonanteFilter, UnidadMuestraFilter
from django_filters.rest_framework import DjangoFilterBackend

try:
    from weasyprint_docker_config import generate_pdf_docker_safe, generate_pdf_with_fallback as docker_fallback
    WEASYPRINT_DOCKER = True
except ImportError:
    try:
        from weasyprint_config import generate_pdf_safe as safe_writer
        WEASYPRINT_DOCKER = False
        WEASYPRINT_SAFE = True
    except ImportError:
        WEASYPRINT_DOCKER = False
        WEASYPRINT_SAFE = False
        print("⚠️ Config de WeasyPrint no encontrada, usando por defecto")

class DonantePagination(PageNumberPagination):
    page_size = 10000
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 10000

class DonanteViewSet(viewsets.ModelViewSet):
    queryset = Donante.objects.all().order_by('id')
    serializer_class = DonanteSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DonanteFilter
    pagination_class = DonantePagination

class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer

class CodigoDonanteViewSet(viewsets.ModelViewSet):
    queryset = CodigoDonante.objects.all().order_by('-fecha_creacion')
    serializer_class = CodigoDonanteSerializer
    # (resto de métodos sin cambios)

class CatalogoDescarteViewSet(viewsets.ModelViewSet):
    queryset = CatalogoDescarte.objects.all().order_by('codigo')
    serializer_class = CatalogoDescarteSerializer
    # (resto sin cambios)

class DescarteMuestraViewSet(viewsets.ModelViewSet):
    queryset = DescarteMuestra.objects.all().order_by('-fecha_descarte')
    serializer_class = DescarteMuestraSerializer
    # (resto sin cambios)

# =======================
# ENTREVISTAS (CRUD + PDF)
# =======================
class EntrevistaViewSet(viewsets.ModelViewSet):
    queryset = Entrevista.objects.select_related('donante', 'orden').prefetch_related(
        'orden__detalleorden_set', 'orden__detalleorden_set__examen'
    ).order_by('-fecha_creacion')
    serializer_class = EntrevistaSerializer

    def create(self, request, *args, **kwargs):
        from django.db import transaction
        from datetime import datetime
        import threading

        lock = threading.Lock()
        with lock:
            with transaction.atomic():
                # correlativo
                fecha_actual = timezone.now().date()
                formato_fecha = fecha_actual.strftime('%Y%m%d')
                ultimo = Entrevista.objects.filter(
                    correlativo__startswith=f'ENT-{formato_fecha}'
                ).order_by('-correlativo').first()
                if ultimo:
                    try:
                        ultimo_num = int(ultimo.correlativo.split('-')[-1])
                        nuevo_num = ultimo_num + 1
                    except Exception:
                        nuevo_num = 1
                else:
                    nuevo_num = 1
                nuevo_corr = f'ENT-{formato_fecha}-{nuevo_num:04d}'

                if Entrevista.objects.filter(correlativo=nuevo_corr).exists():
                    raise serializers.ValidationError(f"Error: El correlativo {nuevo_corr} ya existe.")

                data = request.data.copy()
                data['correlativo'] = nuevo_corr

                if 'fecha' in data and isinstance(data['fecha'], str):
                    if 'T' in data['fecha']:
                        data['fecha'] = datetime.fromisoformat(data['fecha'].replace('Z', '+00:00')).date()
                    else:
                        data['fecha'] = datetime.strptime(data['fecha'], '%Y-%m-%d').date()

                if 'fecha_creacion' in data and isinstance(data['fecha_creacion'], str):
                    if 'T' in data['fecha_creacion']:
                        data['fecha_creacion'] = datetime.fromisoformat(data['fecha_creacion'].replace('Z', '+00:00'))
                    else:
                        data['fecha_creacion'] = datetime.strptime(data['fecha_creacion'], '%Y-%m-%d')
                else:
                    data['fecha_creacion'] = timezone.now()

                for campo in ['hora_inicio_flebotomia', 'hora_finalizacion_flebotomia']:
                    if data.get(campo) and isinstance(data[campo], str):
                        try:
                            data[campo] = datetime.strptime(data[campo], '%H:%M').time()
                        except ValueError:
                            data[campo] = timezone.now().time()

                if 'cantidad_sangre' in data and isinstance(data['cantidad_sangre'], str):
                    try:
                        data['cantidad_sangre'] = int(data['cantidad_sangre'])
                    except ValueError:
                        data['cantidad_sangre'] = 350

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                entrevista = serializer.save()

                if entrevista.orden:
                    entrevista.orden.genero_entrevista = True
                    entrevista.orden.save(update_fields=['genero_entrevista'])

                # ====== GENERAR PDF ======
                try:
                    config = ConfiguracionLaboratorio.objects.first()
                    logo_data = get_logo_data(config, request)

                    # Dicts crudos (booleans) + versiones texto
                    respuestas = entrevista.respuestas_entrevista or {}
                    respuestas_detalle = entrevista.respuestas_adicionales_entrevista or {}
                    medicas = entrevista.respuestas_medicas_adicionales or {}
                    respuestas_mujeres = getattr(entrevista, 'respuestas_mujeres', None) or {}

                    html_string = render_to_string(
                        ENTREVISTA_TEMPLATE,
                        {
                            'entrevista': entrevista,
                            'config': config,
                            'logo_data': logo_data,
                            'datos_estandarizados': estandarizar_datos_entrevista(entrevista),
                            **extraer_respuestas_clave(entrevista),
                            'respuestas': respuestas,
                            'respuestas_txt': _si_no(respuestas),
                            'respuestas_detalle': respuestas_detalle,
                            'medicas': medicas,
                            'medicas_txt': _si_no(medicas),
                            'respuestas_mujeres': respuestas_mujeres,
                            'respuestas_mujeres_txt': _si_no(respuestas_mujeres),
                        }
                    )

                    donante_dir = os.path.join(settings.MEDIA_ROOT, 'entrevistas', str(entrevista.donante.id))
                    os.makedirs(donante_dir, exist_ok=True)

                    # Siempre generar con nombre único para evitar caché del navegador/servidor
                    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                    pdf_filename = f'entrevista_{entrevista.correlativo}_{timestamp}.pdf'
                    pdf_path = os.path.join(donante_dir, pdf_filename)

                    # Eliminar PDF anterior si existe para no acumular
                    try:
                        if entrevista.pdf_entrevista:
                            old_path = _resolve_pdf_path(entrevista.pdf_entrevista)
                            if old_path and os.path.exists(old_path):
                                os.remove(old_path)
                    except Exception:
                        pass

                    if WEASYPRINT_DOCKER:
                        success, message = generate_pdf_with_fallback(html_string, pdf_path, base_url=None)
                    elif 'WEASYPRINT_SAFE' in globals() and WEASYPRINT_SAFE:
                        success, message = generate_pdf_safe(html_string, pdf_path, base_url=None)
                    else:
                        HTML(string=html_string, base_url=None).write_pdf(
                            pdf_path, optimize_size=('fonts', 'images'), font_config=None
                        )
                        success, message = True, f"PDF generado: {pdf_path}"

                    if success:
                        relative = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                        entrevista.pdf_entrevista = relative
                        entrevista.save(update_fields=['pdf_entrevista'])
                        print(f"✅ {message}")
                    else:
                        print(f"⚠️ {message}")

                except Exception as e:
                    print(f"⚠️ Error general en proceso de PDF: {e}")
                # =========================

                return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='descargar-pdf')
    def descargar_pdf(self, request, pk=None):
        """Descarga el PDF. Si no existe o ?forzar=1, lo regenera."""
        entrevista = self.get_object()
        forzar = request.query_params.get('forzar') in ('1', 'true', 'True')

        # Siempre regenerar el PDF con nombre único para evitar caché
        if True:
            try:
                config = ConfiguracionLaboratorio.objects.first()
                logo_data = get_logo_data(config, request)

                respuestas = entrevista.respuestas_entrevista or {}
                respuestas_detalle = entrevista.respuestas_adicionales_entrevista or {}
                medicas = entrevista.respuestas_medicas_adicionales or {}
                respuestas_mujeres = getattr(entrevista, 'respuestas_mujeres', None) or {}

                html_string = render_to_string(
                    ENTREVISTA_TEMPLATE,
                    {
                        'entrevista': entrevista,
                        'config': config,
                        'logo_data': logo_data,
                        'datos_estandarizados': estandarizar_datos_entrevista(entrevista),
                        **extraer_respuestas_clave(entrevista),
                        'respuestas': respuestas,
                        'respuestas_txt': _si_no(respuestas),
                        'respuestas_detalle': respuestas_detalle,
                        'medicas': medicas,
                        'medicas_txt': _si_no(medicas),
                        'respuestas_mujeres': respuestas_mujeres,
                        'respuestas_mujeres_txt': _si_no(respuestas_mujeres),
                    }
                )

                donante_dir = os.path.join(settings.MEDIA_ROOT, 'entrevistas', str(entrevista.donante.id))
                os.makedirs(donante_dir, exist_ok=True)

                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                pdf_filename = f'entrevista_{entrevista.correlativo}_{timestamp}.pdf'
                pdf_path = os.path.join(donante_dir, pdf_filename)

                # Eliminar PDF anterior si existe para no acumular
                try:
                    if entrevista.pdf_entrevista:
                        old_path = _resolve_pdf_path(entrevista.pdf_entrevista)
                        if old_path and os.path.exists(old_path):
                            os.remove(old_path)
                except Exception:
                    pass

                if WEASYPRINT_DOCKER:
                    success, message = generate_pdf_with_fallback(html_string, pdf_path, base_url=None)
                elif 'WEASYPRINT_SAFE' in globals() and WEASYPRINT_SAFE:
                    success, message = generate_pdf_safe(html_string, pdf_path, base_url=None)
                else:
                    HTML(string=html_string, base_url=None).write_pdf(
                        pdf_path, optimize_size=('fonts', 'images'), font_config=None
                    )
                    success, message = True, f"PDF regenerado: {pdf_path}"

                if success:
                    relative = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                    entrevista.pdf_entrevista = relative
                    entrevista.save(update_fields=['pdf_entrevista'])
                    print(f"✅ {message}")
                else:
                    return Response({"error": f"No se pudo regenerar el PDF: {message}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"Error al regenerar el PDF: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not entrevista.pdf_entrevista:
            return Response({"error": "No se pudo generar el PDF para esta entrevista."},
                            status=status.HTTP_404_NOT_FOUND)

        file_url = _resolve_pdf_url(request, entrevista.pdf_entrevista)
        return Response({
            "pdf_url": file_url,
            "correlativo": entrevista.correlativo,
            "donante": f"{entrevista.primer_nombre} {entrevista.primer_apellido}",
            "regenerado": True
        })

# … el resto de tus viewsets (UnidadMuestraViewSet, etc.) permanece igual salvo cambios menores ya presentes …


    @action(detail=True, methods=['post'], url_path='generar-pdf-fresh')
    def generar_pdf_fresh(self, request, pk=None):
        """
        Genera el PDF de la entrevista desde cero, sin usar cache.
        Fuerza la regeneración completa del template.
        """
        entrevista = self.get_object()
        
        try:
            print(f"🔄 Generando PDF fresco para entrevista {entrevista.correlativo}")
            
            # Obtener configuración del laboratorio
            config = ConfiguracionLaboratorio.objects.first()
            
            # Obtener logo usando función helper
            logo_data = get_logo_data(config, request)
            
            # Estandarizar datos de la entrevista
            datos_estandarizados = estandarizar_datos_entrevista(entrevista)
            
            # Debug: Mostrar contenido completo de los JSONFields
            print(f"🔍 JSON respuestas_entrevista: {entrevista.respuestas_entrevista}")
            print(f"🔍 JSON respuestas_adicionales_entrevista: {entrevista.respuestas_adicionales_entrevista}")
            print(f"🔍 JSON respuestas_medicas_adicionales: {entrevista.respuestas_medicas_adicionales}")
            print(f"🔍 JSON respuestas_mujeres: {entrevista.respuestas_mujeres}")
            
            print(f"🔍 Datos estandarizados - salud_hoy: {datos_estandarizados['respuestas_entrevista'].get('salud_hoy', 'NO_ENCONTRADO')}")
            print(f"🔍 Datos estandarizados - tipo_donacion: {datos_estandarizados['respuestas_entrevista'].get('tipo_donacion', 'NO_ENCONTRADO')}")
            print(f"🔍 Datos estandarizados - durmio_6_horas: {datos_estandarizados['respuestas_entrevista'].get('durmio_6_horas', 'NO_ENCONTRADO')}")
            
            # Renderizar template desde cero
            print(f"🔍 Usando template: banco_sangre/entrevista_pdf.html (FRESH)")
            html_string = render_to_string(
                'banco_sangre/entrevista_pdf.html',
                {
                    'entrevista': entrevista,
                    'config': config,
                    'logo_data': logo_data,
                    'datos_estandarizados': datos_estandarizados,
                    **extraer_respuestas_clave(entrevista)
                }
            )
            print(f"🔍 Template renderizado, longitud HTML: {len(html_string)}")
            
            # Crear directorio para el donante
            donante_dir = os.path.join(settings.MEDIA_ROOT, 'entrevistas', str(entrevista.donante.id))
            os.makedirs(donante_dir, exist_ok=True)
            
            # Generar nombre del archivo PDF con timestamp para evitar cache
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f'entrevista_{entrevista.correlativo}_fresh_{timestamp}.pdf'
            pdf_path = os.path.join(donante_dir, pdf_filename)
            
            # Eliminar PDF anterior si existe
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ PDF anterior eliminado: {pdf_path}")
            
            # Generar PDF con configuración mejorada
            try:
                if WEASYPRINT_DOCKER:
                    # Usar configuración específica para Docker
                    success, message = generate_pdf_with_fallback(
                        html_string=html_string,
                        output_path=pdf_path,
                        base_url=None
                    )
                    
                    if success:
                        # Guardar la ruta en la base de datos
                        relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                        entrevista.pdf_entrevista = relative_path
                        entrevista.save(update_fields=['pdf_entrevista'])
                        print(f"✅ PDF fresco generado: {message}")
                    else:
                        print(f"⚠️ Error generando PDF fresco: {message}")
                        return Response(
                            {"error": f"No se pudo generar el PDF fresco: {message}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                elif WEASYPRINT_SAFE:
                    # Usar configuración segura de WeasyPrint
                    success, message = generate_pdf_safe(
                        html_string=html_string,
                        output_path=pdf_path,
                        base_url=None
                    )
                    
                    if success:
                        # Guardar la ruta en la base de datos
                        relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                        entrevista.pdf_entrevista = relative_path
                        entrevista.save(update_fields=['pdf_entrevista'])
                        print(f"✅ PDF fresco generado: {message}")
                    else:
                        print(f"⚠️ Error generando PDF fresco: {message}")
                        return Response(
                            {"error": f"No se pudo generar el PDF fresco: {message}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                else:
                    # Configuración por defecto
                    import logging
                    logging.getLogger('weasyprint').setLevel(logging.ERROR)
                    
                    HTML(
                        string=html_string, 
                        base_url=None
                    ).write_pdf(
                        pdf_path,
                        optimize_size=('fonts', 'images'),
                        font_config=None
                    )
                    
                    # Guardar la ruta en la base de datos
                    relative_path = f'entrevistas/{entrevista.donante.id}/{pdf_filename}'
                    entrevista.pdf_entrevista = relative_path
                    entrevista.save(update_fields=['pdf_entrevista'])
                    
                    print(f"✅ PDF fresco generado: {pdf_path}")
                
            except Exception as pdf_error:
                print(f"⚠️ Error específico generando PDF fresco: {pdf_error}")
                return Response(
                    {"error": f"Error al generar el PDF fresco: {str(pdf_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Construir la URL completa del archivo
            file_url = request.build_absolute_uri(entrevista.pdf_entrevista.url)
            
            return Response({
                "mensaje": "PDF generado desde cero exitosamente",
                "pdf_url": file_url,
                "correlativo": entrevista.correlativo,
                "donante": f"{entrevista.primer_nombre} {entrevista.primer_apellido}",
                "archivo": pdf_filename,
                "timestamp": timestamp,
                "fresh_generation": True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"⚠️ Error general generando PDF fresco: {e}")
            return Response(
                {"error": f"Error al generar el PDF fresco: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
    queryset = UnidadMuestra.objects.all().order_by('-creado')  # Ordenamiento
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

        # Obtener logo
        logo_data = get_logo_data(config, request)

        html_string = render_to_string(
            'banco_sangre/etiqueta_uni.html',
            {
                'unidad': unidad,
                'config': config,
                'barcode_base64': barcode_base64,
                'serologias': serologias,
                'logo_data': logo_data
            }
        )

        output_dir = os.path.join(settings.MEDIA_ROOT, 'etiquetas')
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f'etiqueta_unidad_{pk}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)

        HTML(string=html_string, base_url=None).write_pdf(pdf_path)  # Base local

        file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}etiquetas/{pdf_filename}')
        return Response({'file_url': file_url})

    @action(detail=False, methods=['post'], url_path='crear-para-orden')
    def crear_para_orden(self, request):
        """
        Crea unidades de muestra para una orden específica.
        Automáticamente usa el código de donante de la orden.
        """
        from ordenes.models import Orden

        orden_id = request.data.get('orden_id')
        if not orden_id:
            return Response(
                {"error": "Se requiere orden_id para crear muestras"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            orden = Orden.objects.get(id=orden_id)
        except Orden.DoesNotExist:
            return Response(
                {"error": f"No se encontró la orden con ID {orden_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que la orden tenga un donante
        if not orden.donante:
            return Response(
                {"error": f"La orden {orden.codigo} no tiene un donante asociado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Agregar el donante a los datos (el código se asigna automáticamente)
        data = request.data.copy()
        if isinstance(data, list):
            for item in data:
                item['donante_id'] = orden.donante.id
        else:
            data['donante_id'] = orden.donante.id

        # Usar el método create existente
        is_many = isinstance(data, list)
        serializer = self.get_serializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)

        unidades = serializer.save()

        # Refrescar para cada unidad
        if is_many:
            for unidad in unidades:
                unidad.refresh_from_db()
        else:
            unidades.refresh_from_db()

        response_serializer = self.get_serializer(unidades, many=is_many)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='por-codigo-donante/(?P<codigo_donante_id>[^/.]+)')
    def por_codigo_donante(self, request, codigo_donante_id=None):
        """
        Obtiene todas las unidades de muestra asociadas a un código de donante específico.
        """
        try:
            codigo_donante = CodigoDonante.objects.get(id=codigo_donante_id)
        except CodigoDonante.DoesNotExist:
            return Response(
                {"error": f"No se encontró el código de donante con ID {codigo_donante_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener todas las muestras de este código de donante
        muestras = UnidadMuestra.objects.filter(codigo_donante=codigo_donante).order_by('-creado')

        # Aplicar filtros si existen
        queryset = self.filter_queryset(muestras)

        # Aplicar paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='descartar')
    def descartar_muestra(self, request, pk=None):
        """
        Descarta una muestra específica con motivo y observaciones.
        """
        muestra = self.get_object()

        # Validar que la muestra se puede descartar
        if muestra.esta_descartada:
            return Response(
                {"error": "La muestra ya está descartada"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if muestra.estado not in ['DISPONIBLE', 'RESERVADO']:
            return Response(
                {"error": f"No se puede descartar una muestra en estado {muestra.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar datos del descarte
        serializer = DescarteMuestraCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Crear el descarte usando el método del modelo
            descarte = muestra.descartar(
                motivo_id=serializer.validated_data['motivo_id'].id,
                observaciones=serializer.validated_data.get('observaciones', ''),
                responsable=request.user if request.user.is_authenticated else None
            )

            # Refrescar la muestra para obtener el estado actualizado
            muestra.refresh_from_db()

            # Retornar la muestra actualizada con información del descarte
            response_serializer = self.get_serializer(muestra)
            return Response({
                "mensaje": "Muestra descartada exitosamente",
                "muestra": response_serializer.data,
                "descarte": {
                    "id": descarte.id,
                    "motivo": descarte.motivo.nombre,
                    "fecha_descarte": descarte.fecha_descarte,
                    "validado": descarte.validado
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='generar-informe-resultados/(?P<orden_id>[^/.]+)')
    def generar_informe_resultados(self, request, orden_id=None):
        """
        Genera el PDF del informe de resultados para los exámenes de una orden validada.
        """
        from ordenes.models import Orden
        from resultados.models import Resultado

        # Buscar la orden
        try:
            orden = Orden.objects.get(id=orden_id)
        except Orden.DoesNotExist:
            return Response(
                {"error": f"No se encontró la orden {orden_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Obtener los resultados validados
        resultados = Resultado.objects.filter(
            resultado__orden=orden,
            estado='VALIDADO'
        ).select_related(
            'resultado__examen',
            'resultado__orden__donante',
            'resultado__orden__medico'
        ).prefetch_related('valores')

        if not resultados.exists():
            return Response(
                {"error": "No se encontraron resultados validados para esta orden"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            config = ConfiguracionLaboratorio.objects.first()
            logo_data = get_logo_data(config, request)

            # Obtener el código del donante si existe
            codigo_donante_str = orden.codigo
            if orden.donante:
                from banco_sangre.models import CodigoDonante
                try:
                    codigo_donante = CodigoDonante.objects.filter(
                        orden=orden,
                        donante=orden.donante,
                        activo=True
                    ).first()
                    if codigo_donante:
                        codigo_donante_str = codigo_donante.codigo
                except:
                    pass
            
            # Agregar el código del donante a la orden para que esté disponible en el template
            orden.codigo_donante = codigo_donante_str

            context = {
                'orden': orden,
                'config': config,
                'logo_data': logo_data,
                'resultados': resultados,
                'fecha_actual': timezone.now(),
            }

            html_string = render_to_string(
                'banco_sangre/informe_resultados_pdf.html',
                context
            )

            informe_dir = os.path.join(settings.MEDIA_ROOT, 'informes_resultados', str(orden.donante.id))
            os.makedirs(informe_dir, exist_ok=True)

            pdf_filename = f'informe_resultados_{orden.codigo}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            pdf_path = os.path.join(informe_dir, pdf_filename)

            # Generar PDF
            try:
                if WEASYPRINT_DOCKER:
                    success, message = generate_pdf_with_fallback(
                        html_string=html_string,
                        output_path=pdf_path,
                        base_url=None
                    )
                elif WEASYPRINT_SAFE:
                    success, message = generate_pdf_safe(
                        html_string=html_string,
                        output_path=pdf_path,
                        base_url=None
                    )
                else:
                    import logging
                    logging.getLogger('weasyprint').setLevel(logging.ERROR)
                    HTML(
                        string=html_string,
                        base_url=None
                    ).write_pdf(
                        pdf_path,
                        optimize_size=('fonts', 'images'),
                        font_config=None
                    )
                    success, message = True, f"PDF generado: {pdf_path}"

                if success:
                    relative_path = f'informes_resultados/{orden.donante.id}/{pdf_filename}'
                    file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{relative_path}')

                    return Response({
                        "mensaje": "Informe de resultados generado exitosamente",
                        "pdf_url": file_url,
                        "archivo": pdf_filename,
                        "orden": {
                            "codigo": orden.codigo,
                            "donante": f"{orden.donante.primer_nombre} {orden.donante.primer_apellido}",
                            "medico": f"{orden.medico.nombres} {orden.medico.apellidos}" if orden.medico else "No asignado",
                            "fecha": orden.fecha,
                            "total_resultados": len(resultados)
                        }
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": f"Error generando PDF: {message}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            except Exception as pdf_error:
                return Response(
                    {"error": f"Error específico generando PDF: {pdf_error}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return Response(
                {"error": f"Error general generando informe: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='transformar')
    def transformar_muestra(self, request, pk=None):
        """
        Transforma una muestra creando una nueva muestra hija con formato de correlativo:
        <Correlativo_padre>/0001<ascendente>
        
        Ejemplo: PLM-0001/0001, PLM-0001/0002, etc.
        """
        from .serializers import TransformarMuestraSerializer
        
        muestra = self.get_object()
        
        # Validar que la muestra se pueda transformar
        if muestra.estado not in ['DISPONIBLE', 'RESERVADO']:
            return Response(
                {"error": f"No se puede transformar una muestra en estado {muestra.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if muestra.es_transformacion:
            return Response(
                {"error": "No se puede transformar una muestra que ya es resultado de una transformación"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de entrada
        serializer = TransformarMuestraSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        nuevo_tipo_unidad = serializer.validated_data['nuevo_tipo_unidad']
        volumen_ml = serializer.validated_data['volumen_ml']
        observaciones = serializer.validated_data.get('observaciones', '')
        
        try:
            # Realizar la transformación
            muestra_transformada = muestra.transformar(
                nuevo_tipo_unidad=nuevo_tipo_unidad,
                volumen_ml=volumen_ml,
                responsable=request.user,
                observaciones=observaciones
            )
            
            # Serializar la respuesta
            response_serializer = self.get_serializer(muestra_transformada)
            
            return Response({
                "mensaje": "Muestra transformada exitosamente",
                "muestra_original": {
                    "id": muestra.id,
                    "correlativo": muestra.correlativo,
                    "estado": muestra.estado
                },
                "muestra_transformada": response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error transformando la muestra: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='transformar-multiple')
    def transformar_multiple(self, request, pk=None):
        """
        Transforma UNA unidad padre en MÚLTIPLES unidades hijas en una sola operación.
        
        Body esperado:
        {
            "transformaciones": [
                {
                    "nuevo_tipo_unidad": "PLASMA",
                    "volumen_ml": 100,
                    "observaciones": "Fracción 1"
                },
                {
                    "nuevo_tipo_unidad": "PLASMA",
                    "volumen_ml": 100,
                    "observaciones": "Fracción 2"
                },
                {
                    "nuevo_tipo_unidad": "PLAQUETAS",
                    "volumen_ml": 150,
                    "observaciones": "Fracción 3"
                }
            ]
        }
        
        Respuesta:
        {
            "mensaje": "Unidad padre transformada en 3 unidades hijas",
            "muestra_padre": {...},
            "muestras_hijas": [...]
        }
        """
        from .serializers import TransformarMultipleSerializer
        from django.db import transaction
        
        muestra_padre = self.get_object()
        
        # Validar que la muestra se pueda transformar
        if muestra_padre.estado not in ['DISPONIBLE', 'RESERVADO']:
            return Response(
                {"error": f"No se puede transformar una muestra en estado {muestra_padre.estado}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if muestra_padre.es_transformacion:
            return Response(
                {"error": "No se puede transformar una muestra que ya es resultado de una transformación"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de entrada
        serializer = TransformarMultipleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transformaciones_data = serializer.validated_data['transformaciones']
        
        try:
            with transaction.atomic():
                # Obtener la muestra con lock para evitar condiciones de carrera
                muestra_padre = UnidadMuestra.objects.select_for_update().get(pk=muestra_padre.pk)
                
                # Crear todas las muestras hijas SIN marcar como transformada
                muestras_hijas = []
                for item in transformaciones_data:
                    nuevo_tipo_unidad = item['nuevo_tipo_unidad']
                    volumen_ml = item['volumen_ml']
                    observaciones = item.get('observaciones', '')
                    
                    # Usar el método transformar del modelo sin marcar como transformada aún
                    muestra_hija = muestra_padre.transformar(
                        nuevo_tipo_unidad=nuevo_tipo_unidad,
                        volumen_ml=volumen_ml,
                        responsable=request.user,
                        observaciones=observaciones,
                        marcar_como_transformada=False  # No marcar aún, lo haremos al final
                    )
                    
                    muestras_hijas.append(muestra_hija)
                
                # Marcar la muestra padre como transformada SOLO al final
                if muestra_padre.estado != 'TRANSFORMADA':
                    muestra_padre.estado = 'TRANSFORMADA'
                    muestra_padre.save(update_fields=['estado'])
                
                # Recargar la muestra padre para obtener el estado actualizado
                muestra_padre.refresh_from_db()
                
                # Serializar resultados
                padre_serializer = self.get_serializer(muestra_padre)
                hijas_serializer = self.get_serializer(muestras_hijas, many=True)
                
                return Response({
                    "mensaje": f"Unidad padre transformada en {len(muestras_hijas)} unidades hijas exitosamente",
                    "muestra_padre": {
                        "id": muestra_padre.id,
                        "correlativo": muestra_padre.correlativo,
                        "estado": muestra_padre.estado,
                        "tipo_unidad": muestra_padre.tipo_unidad,
                        "volumen_original_ml": muestra_padre.volumen_ml
                    },
                    "muestras_hijas": [
                        {
                            "id": hija.id,
                            "correlativo": hija.correlativo,
                            "tipo_unidad": hija.tipo_unidad,
                            "volumen_ml": hija.volumen_ml,
                            "estado": hija.estado,
                            "observaciones": hija.observaciones
                        }
                        for hija in muestras_hijas
                    ],
                    "total_muestras_hijas": len(muestras_hijas),
                    "volumen_total_hijas": sum(h.volumen_ml for h in muestras_hijas)
                }, status=status.HTTP_201_CREATED)
                
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error transformando la muestra: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='transformaciones')
    def obtener_transformaciones(self, request, pk=None):
        """
        Obtiene todas las transformaciones de una muestra (si es original)
        o la muestra padre y hermanas (si es transformación)
        """
        muestra = self.get_object()
        
        if muestra.es_transformacion:
            # Si es una transformación, mostrar la muestra padre y todas sus transformaciones
            muestra_padre = muestra.muestra_padre
            transformaciones = muestra_padre.muestras_hijas.all().order_by('correlativo')
            
            padre_serializer = self.get_serializer(muestra_padre)
            transformaciones_serializer = self.get_serializer(transformaciones, many=True)
            
            return Response({
                "muestra_padre": padre_serializer.data,
                "transformaciones": transformaciones_serializer.data,
                "total_transformaciones": transformaciones.count()
            })
        else:
            # Si es una muestra original, mostrar sus transformaciones
            transformaciones = muestra.muestras_hijas.all().order_by('correlativo')
            transformaciones_serializer = self.get_serializer(transformaciones, many=True)
            
            return Response({
                "muestra_original": self.get_serializer(muestra).data,
                "transformaciones": transformaciones_serializer.data,
                "total_transformaciones": transformaciones.count()
            })
    
    @action(detail=False, methods=['post'], url_path='transformar-lote')
    def transformar_lote_muestras(self, request):
        """
        Transforma múltiples muestras en una sola petición.
        
        Body esperado:
        {
            "transformaciones": [
                {
                    "id": 123,
                    "nuevo_tipo_unidad": "PLASMA",
                    "volumen_ml": 250,
                    "observaciones": "Observación opcional"
                },
                {
                    "id": 124,
                    "nuevo_tipo_unidad": "PLAQUETAS",
                    "volumen_ml": 200,
                    "observaciones": ""
                }
            ]
        }
        
        Respuesta:
        {
            "exitosas": [...],
            "fallidas": [...],
            "total_exitosas": 2,
            "total_fallidas": 0
        }
        """
        from .serializers import TransformarLoteMuestrasSerializer
        from django.db import transaction
        
        # Validar datos de entrada
        serializer = TransformarLoteMuestrasSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        transformaciones_data = serializer.validated_data['transformaciones']
        
        resultados_exitosos = []
        resultados_fallidos = []
        
        # Procesar cada transformación
        for item in transformaciones_data:
            muestra_id = item['id']
            nuevo_tipo_unidad = item['nuevo_tipo_unidad']
            volumen_ml = item['volumen_ml']
            observaciones = item.get('observaciones', '')
            
            try:
                with transaction.atomic():
                    # Obtener la muestra
                    muestra = UnidadMuestra.objects.select_for_update().get(id=muestra_id)
                    
                    # Validar que la muestra se pueda transformar
                    if muestra.estado not in ['DISPONIBLE', 'RESERVADO']:
                        raise ValueError(f"No se puede transformar una muestra en estado {muestra.estado}")
                    
                    if muestra.es_transformacion:
                        raise ValueError("No se puede transformar una muestra que ya es resultado de una transformación")
                    
                    # Realizar la transformación
                    muestra_transformada = muestra.transformar(
                        nuevo_tipo_unidad=nuevo_tipo_unidad,
                        volumen_ml=volumen_ml,
                        responsable=request.user,
                        observaciones=observaciones
                    )
                    
                    # Agregar a resultados exitosos
                    resultados_exitosos.append({
                        "id_original": muestra.id,
                        "correlativo_original": muestra.correlativo,
                        "estado_original": muestra.estado,
                        "muestra_transformada": {
                            "id": muestra_transformada.id,
                            "correlativo": muestra_transformada.correlativo,
                            "tipo_unidad": muestra_transformada.tipo_unidad,
                            "volumen_ml": muestra_transformada.volumen_ml,
                            "estado": muestra_transformada.estado
                        }
                    })
                    
            except UnidadMuestra.DoesNotExist:
                resultados_fallidos.append({
                    "id": muestra_id,
                    "error": f"No se encontró la muestra con ID {muestra_id}"
                })
            except ValueError as e:
                resultados_fallidos.append({
                    "id": muestra_id,
                    "error": str(e)
                })
            except Exception as e:
                resultados_fallidos.append({
                    "id": muestra_id,
                    "error": f"Error inesperado: {str(e)}"
                })
        
        # Determinar código de estado de la respuesta
        if len(resultados_fallidos) == 0:
            status_code = status.HTTP_201_CREATED
        elif len(resultados_exitosos) == 0:
            status_code = status.HTTP_400_BAD_REQUEST
        else:
            status_code = status.HTTP_207_MULTI_STATUS
        
        return Response({
            "mensaje": f"Proceso completado: {len(resultados_exitosos)} exitosas, {len(resultados_fallidos)} fallidas",
            "exitosas": resultados_exitosos,
            "fallidas": resultados_fallidos,
            "total_exitosas": len(resultados_exitosos),
            "total_fallidas": len(resultados_fallidos)
        }, status=status_code)


class SalidaUnidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las salidas de unidades de muestra
    """
    queryset = SalidaUnidad.objects.all().order_by('-fecha_salida')
    serializer_class = SalidaUnidadSerializer
    
    def create(self, request, *args, **kwargs):
        """Crear una salida de unidades y generar el PDF"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Guardar la salida
        salida = serializer.save()
        
        # Generar el PDF
        try:
            self._generar_pdf_salida(salida, request)
        except Exception as e:
            print(f"❌ Error generando PDF de salida: {e}")
        
        # Refrescar para obtener los detalles
        salida.refresh_from_db()
        
        response_serializer = self.get_serializer(salida)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def _generar_pdf_salida(self, salida, request):
        """Genera el PDF de la salida"""
        from sistema.models import ConfiguracionLaboratorio
        
        config = ConfiguracionLaboratorio.objects.first()
        
        # Obtener las unidades
        unidades = [detalle.unidad_muestra for detalle in salida.detalles.all()]
        
        # Obtener logo
        logo_data = get_logo_data(config, request)
        
        # Renderizar HTML
        html_string = render_to_string(
            'banco_sangre/salida_pdf.html',
            {
                'salida': salida,
                'unidades': unidades,
                'config': config,
                'logo_data': logo_data
            }
        )
        
        # Generar PDF
        output_dir = os.path.join(settings.MEDIA_ROOT, 'salidas')
        os.makedirs(output_dir, exist_ok=True)
        pdf_filename = f'salida_{salida.correlativo}.pdf'
        pdf_path = os.path.join(output_dir, pdf_filename)
        
        success, message = generate_pdf_safe(html_string, pdf_path, base_url=request.build_absolute_uri('/'))
        
        if success:
            # Actualizar el campo pdf_salida
            salida.pdf_salida.name = f'salidas/{pdf_filename}'
            salida.save(update_fields=['pdf_salida'])
            print(f"✅ PDF de salida generado: {pdf_filename}")
        else:
            print(f"❌ Error generando PDF: {message}")