from django.contrib import admin
from .models import CatalogoMotivoDenegacion, HistorialDenegacion

@admin.register(CatalogoMotivoDenegacion)
class CatalogoMotivoDenegacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el catálogo de motivos de denegación.
    """
    list_display = [
        'codigo', 'nombre', 'tipo_denegacion', 'tiempo_diferimiento_dias', 
        'activo', 'fecha_creacion'
    ]
    list_filter = [
        'tipo_denegacion', 'activo', 'fecha_creacion'
    ]
    search_fields = [
        'codigo', 'nombre', 'descripcion'
    ]
    list_editable = ['activo']
    ordering = ['tipo_denegacion', 'codigo']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion')
        }),
        ('Configuración de Denegación', {
            'fields': ('tipo_denegacion', 'tiempo_diferimiento_dias', 'activo'),
            'description': 'Configura si es permanente o temporal y el tiempo de diferimiento'
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimiza las consultas del admin"""
        return super().get_queryset(request).select_related()

@admin.register(HistorialDenegacion)
class HistorialDenegacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el historial de denegaciones.
    """
    list_display = [
        'donante', 'motivo_denegacion', 'resultado_examen', 
        'usuario_deniego', 'fecha_denegacion'
    ]
    list_filter = [
        'motivo_denegacion__tipo_denegacion', 'fecha_denegacion', 
        'motivo_denegacion', 'usuario_deniego'
    ]
    search_fields = [
        'donante__primer_nombre', 'donante__primer_apellido', 
        'donante__cui', 'resultado_examen', 'usuario_deniego'
    ]
    readonly_fields = ['fecha_denegacion']
    ordering = ['-fecha_denegacion']
    
    fieldsets = (
        ('Información de la Denegación', {
            'fields': ('donante', 'resultado', 'orden', 'resultado_examen')
        }),
        ('Motivo y Observaciones', {
            'fields': ('motivo_denegacion', 'observaciones')
        }),
        ('Usuario y Fecha', {
            'fields': ('usuario_deniego', 'fecha_denegacion')
        }),
        ('Valores Críticos', {
            'fields': ('valores_criticos',),
            'classes': ('collapse',),
            'description': 'Valores que motivaron la denegación (formato JSON)'
        }),
    )
    
    def get_queryset(self, request):
        """Optimiza las consultas del admin"""
        return super().get_queryset(request).select_related(
            'donante', 'motivo_denegacion', 'resultado', 'orden'
        )
    
    def has_add_permission(self, request):
        """No permitir crear registros manualmente desde el admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo permitir lectura - no edición"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar registros del historial"""
        return False
