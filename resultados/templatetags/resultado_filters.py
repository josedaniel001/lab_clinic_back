# resultados/templatetags/resultado_filters.py
import re
from django import template

register = template.Library()


@register.filter(name='sin_observaciones_reversion')
def sin_observaciones_reversion(value):
    """
    Filtro que elimina las observaciones de reversión del texto.
    Las observaciones de reversión tienen el formato:
    [REVERTIDO] fecha - Usuario: usuario - Motivo: motivo
    
    Mantiene solo las observaciones normales del resultado.
    """
    if not value:
        return value
    
    if not isinstance(value, str):
        value = str(value)
    
    # Patrón para encontrar observaciones de reversión
    # Formato: \n[REVERTIDO] fecha - Usuario: usuario - Motivo: motivo
    # También puede estar al inicio del texto
    # Busca líneas que comiencen con [REVERTIDO] y todo lo que siga hasta el final de la línea
    patron = r'\n?\[REVERTIDO\][^\n]*(?:\n|$)'
    
    # Eliminar todas las observaciones de reversión (puede haber múltiples)
    texto_limpio = re.sub(patron, '', value, flags=re.MULTILINE)
    
    # Limpiar líneas vacías múltiples y espacios en blanco al inicio y final
    texto_limpio = re.sub(r'\n\s*\n+', '\n', texto_limpio)  # Reemplazar múltiples saltos de línea por uno solo
    texto_limpio = texto_limpio.strip()
    
    # Si quedó vacío después de limpiar, retornar cadena vacía
    return texto_limpio if texto_limpio else ""

