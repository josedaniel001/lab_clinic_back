from django.contrib import admin
from .models import CatalogoUnidadParametro

@admin.register(CatalogoUnidadParametro)
class CatalogoUnidadParametroAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el catálogo de unidades de parámetros.
    """
    list_display = [
        'codigo', 'simbolo', 'nombre', 'categoria', 
        'activo', 'fecha_creacion'
    ]
    list_filter = [
        'categoria', 'activo', 'fecha_creacion'
    ]
    search_fields = [
        'codigo', 'nombre', 'simbolo', 'categoria'
    ]
    list_editable = ['activo']
    ordering = ['categoria', 'nombre']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'simbolo', 'categoria')
        }),
        ('Detalles', {
            'fields': ('descripcion', 'activo'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimiza las consultas del admin"""
        return super().get_queryset(request).select_related()