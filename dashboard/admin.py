from django.contrib import admin
from django.utils.html import format_html
from .models import DashboardMetric, DashboardWidget, DashboardConfig


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'valor', 'categoria', 'activo', 'fecha_actualizacion']
    list_display_links = ['nombre']
    list_filter = ['categoria', 'activo', 'fecha_actualizacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']
    list_per_page = 25
    list_editable = ['valor', 'activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'valor', 'categoria', 'activo')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
    )
    
    readonly_fields = ['fecha_actualizacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'usuario', 'posicion', 'activo', 'fecha_creacion']
    list_display_links = ['nombre']
    list_filter = ['tipo', 'activo', 'usuario', 'fecha_creacion']
    search_fields = ['nombre', 'configuracion']
    ordering = ['posicion_y', 'posicion_x', 'nombre']
    list_per_page = 25
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'usuario', 'activo')
        }),
        ('Configuración', {
            'fields': ('configuracion',)
        }),
        ('Posición y Tamaño', {
            'fields': ('posicion_x', 'posicion_y', 'ancho', 'alto')
        }),
    )
    
    readonly_fields = ['fecha_creacion']
    
    def posicion(self, obj):
        return f"({obj.posicion_x}, {obj.posicion_y}) - {obj.ancho}x{obj.alto}"
    posicion.short_description = 'Posición y Tamaño'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(DashboardConfig)
class DashboardConfigAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tema', 'actualizacion_automatica', 'intervalo_actualizacion', 'fecha_ultima_actualizacion']
    list_display_links = ['usuario']
    list_filter = ['tema', 'actualizacion_automatica', 'fecha_ultima_actualizacion']
    search_fields = ['usuario__username', 'usuario__email']
    ordering = ['usuario__username']
    list_per_page = 25
    list_editable = ['tema', 'actualizacion_automatica', 'intervalo_actualizacion']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Configuración Visual', {
            'fields': ('tema',)
        }),
        ('Configuración de Actualización', {
            'fields': ('actualizacion_automatica', 'intervalo_actualizacion')
        }),
        ('Configuración Avanzada', {
            'fields': ('configuracion',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_ultima_actualizacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
