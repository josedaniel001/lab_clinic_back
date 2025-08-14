#!/usr/bin/env python
"""
Configuración para WeasyPrint que evita errores de fuentes
"""
import os
import logging
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Configurar logging para WeasyPrint
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)

def get_weasyprint_config():
    """Obtener configuración optimizada para WeasyPrint"""
    # Configuración de fuentes que evita errores
    font_config = FontConfiguration()
    
    # CSS básico para evitar problemas de fuentes
    base_css = CSS(string='''
        @page {
            size: A4;
            margin: 1cm;
        }
        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
            line-height: 1.4;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: Arial, Helvetica, sans-serif;
            font-weight: bold;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
    ''')
    
    return {
        'font_config': font_config,
        'base_css': base_css,
        'optimize_size': ('fonts', 'images'),
    }

def generate_pdf_safe(html_string, output_path, base_url=None):
    """
    Generar PDF de forma segura evitando errores de fuentes
    
    Args:
        html_string (str): Contenido HTML
        output_path (str): Ruta donde guardar el PDF
        base_url (str): URL base para recursos externos
    """
    try:
        config = get_weasyprint_config()
        
        # Crear HTML con configuración segura
        html = HTML(
            string=html_string,
            base_url=base_url
        )
        
        # Generar PDF con configuración optimizada
        html.write_pdf(
            output_path,
            font_config=config['font_config'],
            optimize_size=config['optimize_size']
        )
        
        return True, f"PDF generado exitosamente: {output_path}"
        
    except Exception as e:
        error_msg = f"Error generando PDF: {str(e)}"
        print(f"⚠️ {error_msg}")
        return False, error_msg

def generate_pdf_with_css(html_string, output_path, css_string=None, base_url=None):
    """
    Generar PDF con CSS personalizado
    
    Args:
        html_string (str): Contenido HTML
        output_path (str): Ruta donde guardar el PDF
        css_string (str): CSS personalizado (opcional)
        base_url (str): URL base para recursos externos
    """
    try:
        config = get_weasyprint_config()
        
        # Crear HTML
        html = HTML(
            string=html_string,
            base_url=base_url
        )
        
        # Preparar CSS
        css_list = [config['base_css']]
        if css_string:
            css_list.append(CSS(string=css_string))
        
        # Generar PDF
        html.write_pdf(
            output_path,
            stylesheets=css_list,
            font_config=config['font_config'],
            optimize_size=config['optimize_size']
        )
        
        return True, f"PDF generado exitosamente: {output_path}"
        
    except Exception as e:
        error_msg = f"Error generando PDF: {str(e)}"
        print(f"⚠️ {error_msg}")
        return False, error_msg
