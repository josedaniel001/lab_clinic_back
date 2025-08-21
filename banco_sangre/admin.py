from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Donante, Entrevista, UnidadMuestra, Lote, SalidaUnidad, DetalleSalida

@admin.register(Donante)
class DonanteAdmin(admin.ModelAdmin):
    list_display = [
        'cui', 'primer_nombre', 'primer_apellido', 'codigo_donante', 
        'apto_donacion', 'tiene_entrevista_apro', 'fecha_ultima_donacion',
        'puede_crear_orden', 'dias_restantes'
    ]
    list_filter = ['apto_donacion', 'tiene_entrevista_apro', 'activo', 'sexo', 'municipio']
    search_fields = ['cui', 'primer_nombre', 'primer_apellido', 'codigo_donante']
    readonly_fields = ['codigo_donante', 'historial_codigos', 'puede_crear_orden', 'dias_restantes']
    fieldsets = (
        ('Información Personal', {
            'fields': ('cui', 'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'celular', 'municipio')
        }),
        ('Información Médica', {
            'fields': ('sexo', 'fecha_nacimiento', 'edad', 'ocupacion')
        }),
        ('Estado de Donación', {
            'fields': ('apto_donacion', 'tiene_entrevista_apro', 'activo')
        }),
        ('Códigos y Fechas', {
            'fields': ('codigo_donante', 'historial_codigos', 'fecha_ultima_donacion'),
            'description': 'Información sobre códigos del donante y fechas de donación'
        }),
        ('Validaciones', {
            'fields': ('puede_crear_orden', 'dias_restantes'),
            'description': 'Información sobre si puede crear nuevas órdenes'
        }),
    )
    
    actions = ['generar_nuevo_codigo', 'actualizar_fecha_donacion_hoy']
    
    def puede_crear_orden(self, obj):
        """Muestra si puede crear nueva orden"""
        if obj.puede_crear_nueva_orden():
            return format_html('<span style="color: green;">✓ Sí</span>')
        else:
            dias = obj.dias_restantes_para_nueva_orden()
            return format_html('<span style="color: red;">✗ No ({} días restantes)</span>', dias)
    puede_crear_orden.short_description = 'Puede crear orden'
    
    def dias_restantes(self, obj):
        """Muestra días restantes para nueva orden"""
        dias = obj.dias_restantes_para_nueva_orden()
        if dias == 0:
            return "Puede crear orden"
        return f"{dias} días"
    dias_restantes.short_description = 'Días restantes'
    
    def historial_codigos(self, obj):
        """Muestra el historial de códigos de forma legible"""
        if not obj.historial_codigos:
            return "Sin historial"
        
        html = "<div style='max-height: 200px; overflow-y: auto;'>"
        for i, codigo_info in enumerate(obj.historial_codigos):
            html += f"<p><strong>Código {i+1}:</strong> {codigo_info.get('codigo', 'N/A')}<br>"
            html += f"<small>Generado: {codigo_info.get('fecha_generacion', 'N/A')}</small></p>"
        html += "</div>"
        return format_html(html)
    historial_codigos.short_description = 'Historial de Códigos'
    
    def generar_nuevo_codigo(self, request, queryset):
        """Acción para generar nuevo código"""
        count = 0
        for donante in queryset:
            try:
                donante.generar_nuevo_codigo_para_orden()
                count += 1
            except Exception as e:
                messages.error(request, f"Error con donante {donante.cui}: {str(e)}")
        
        if count > 0:
            messages.success(request, f"Se generaron {count} nuevos códigos exitosamente.")
        return HttpResponseRedirect(request.get_full_path())
    generar_nuevo_codigo.short_description = "Generar nuevo código para donantes seleccionados"
    
    def actualizar_fecha_donacion_hoy(self, request, queryset):
        """Acción para actualizar fecha de donación a hoy"""
        from django.utils import timezone
        count = 0
        for donante in queryset:
            try:
                donante.actualizar_fecha_ultima_donacion(timezone.now().date())
                count += 1
            except Exception as e:
                messages.error(request, f"Error con donante {donante.cui}: {str(e)}")
        
        if count > 0:
            messages.success(request, f"Se actualizaron {count} fechas de donación exitosamente.")
        return HttpResponseRedirect(request.get_full_path())
    actualizar_fecha_donacion_hoy.short_description = "Actualizar fecha de donación a hoy"

@admin.register(Entrevista)
class EntrevistaAdmin(admin.ModelAdmin):
    list_display = ['correlativo', 'donante', 'fecha', 'estado', 'nombre_entrevistador']
    list_filter = ['estado', 'fecha', 'tipo_sangre']
    search_fields = ['correlativo', 'donante__primer_nombre', 'donante__primer_apellido']
    readonly_fields = ['correlativo', 'fecha_creacion', 'pdf_entrevista']

@admin.register(UnidadMuestra)
class UnidadMuestraAdmin(admin.ModelAdmin):
    list_display = ['correlativo', 'donante', 'tipo_unidad', 'tipo_sangre', 'estado', 'fecha_extraccion']
    list_filter = ['tipo_unidad', 'tipo_sangre', 'estado', 'fecha_extraccion']
    search_fields = ['correlativo', 'donante__primer_nombre', 'donante__primer_apellido']
    readonly_fields = ['correlativo', 'creado']

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'descripcion', 'fecha_creacion', 'responsable']
    list_filter = ['fecha_creacion']
    search_fields = ['codigo', 'descripcion']

@admin.register(SalidaUnidad)
class SalidaUnidadAdmin(admin.ModelAdmin):
    list_display = ['correlativo', 'receptor', 'estado', 'fecha_salida', 'tecnico_salida']
    list_filter = ['estado', 'fecha_salida']
    search_fields = ['correlativo', 'receptor', 'medico_solicitante']
    readonly_fields = ['correlativo', 'fecha_salida', 'fecha_creacion']

@admin.register(DetalleSalida)
class DetalleSalidaAdmin(admin.ModelAdmin):
    list_display = ['salida', 'unidad', 'fecha_inclusion']
    list_filter = ['fecha_inclusion']
    search_fields = ['salida__correlativo', 'unidad__correlativo']
