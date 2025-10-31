from django.contrib import admin
from django.utils.html import format_html
from .models import Pais, Departamento, Municipio

@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'total_departamentos']
    list_display_links = ['id']
    search_fields = ['nombre']
    ordering = ['nombre']
    list_per_page = 25
    list_editable = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre',)
        }),
    )
    
    def total_departamentos(self, obj):
        count = obj.departamentos.count()
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{}</span> departamentos',
            count
        )
    total_departamentos.short_description = 'Total Departamentos'
    total_departamentos.admin_order_field = 'departamentos__count'

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'pais', 'total_municipios']
    list_display_links = ['id']
    list_filter = ['pais']
    search_fields = ['nombre', 'pais__nombre']
    ordering = ['pais__nombre', 'nombre']
    list_per_page = 25
    autocomplete_fields = ['pais']
    list_editable = ['nombre']
    
    fieldsets = (
        ('Información del Departamento', {
            'fields': ('nombre', 'pais')
        }),
    )
    
    def total_municipios(self, obj):
        count = obj.municipios.count()
        return format_html(
            '<span style="color: #17a2b8; font-weight: bold;">{}</span> municipios',
            count
        )
    total_municipios.short_description = 'Total Municipios'
    total_municipios.admin_order_field = 'municipios__count'

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'departamento', 'pais', 'info_completa']
    list_display_links = ['id']
    list_filter = ['departamento__pais', 'departamento']
    search_fields = ['nombre', 'departamento__nombre', 'departamento__pais__nombre']
    ordering = ['departamento__pais__nombre', 'departamento__nombre', 'nombre']
    list_per_page = 25
    autocomplete_fields = ['departamento']
    list_editable = ['nombre']
    
    fieldsets = (
        ('Información del Municipio', {
            'fields': ('nombre', 'departamento')
        }),
        ('Información Geográfica', {
            'fields': ('pais_info',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['pais_info']
    
    def pais(self, obj):
        return obj.departamento.pais.nombre
    pais.short_description = 'País'
    pais.admin_order_field = 'departamento__pais__nombre'
    
    def pais_info(self, obj):
        if obj.departamento:
            return format_html(
                '<strong>País:</strong> {}<br>'
                '<strong>Departamento:</strong> {}',
                obj.departamento.pais.nombre,
                obj.departamento.nombre
            )
        return 'Sin información'
    pais_info.short_description = 'Información Geográfica'
    
    def info_completa(self, obj):
        return format_html(
            '<span style="color: #6c757d; font-size: 0.9em;">{}</span><br>'
            '<span style="color: #495057; font-size: 0.8em;">{}</span>',
            obj.departamento.nombre,
            obj.departamento.pais.nombre
        )
    info_completa.short_description = 'Ubicación Completa'
