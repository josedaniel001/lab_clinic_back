#!/usr/bin/env python
"""
Configuración específica de WeasyPrint para Docker
"""
import os
import logging
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

# Configurar logging para suprimir warnings
logging.getLogger('weasyprint').setLevel(logging.ERROR)
logging.getLogger('PIL').setLevel(logging.ERROR)
logging.getLogger('fontTools').setLevel(logging.ERROR)

def get_docker_weasyprint_config():
    """Obtener configuración optimizada para Docker"""
    
    # Configuración de fuentes específica para Docker
    font_config = FontConfiguration()
    
    # CSS básico que funciona bien en Docker
    base_css = CSS(string='''
        @page {
            size: A4;
            margin: 1cm;
        }
        body {
            font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            color: #000;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
            font-weight: bold;
            margin: 10px 0;
        }
        h1 { font-size: 18px; }
        h2 { font-size: 16px; }
        h3 { font-size: 14px; }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 10px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            font-size: 11px;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .section {
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        .footer {
            margin-top: 20px;
            text-align: center;
            font-size: 10px;
        }
    ''')
    
    return {
        'font_config': font_config,
        'base_css': base_css,
        'optimize_size': ('fonts', 'images'),
    }

def generate_pdf_docker_safe(html_string, output_path, base_url=None):
    """
    Generar PDF de forma segura en Docker
    
    Args:
        html_string (str): Contenido HTML
        output_path (str): Ruta donde guardar el PDF
        base_url (str): URL base para recursos externos
    """
    try:
        config = get_docker_weasyprint_config()
        
        # Crear HTML con configuración segura
        html = HTML(
            string=html_string,
            base_url=base_url
        )
        
        # Generar PDF con configuración optimizada para Docker
        html.write_pdf(
            output_path,
            font_config=config['font_config'],
            optimize_size=config['optimize_size'],
            # Configuraciones adicionales para Docker
            presentational_hints=True,
            zoom=1.0
        )
        
        return True, f"PDF generado exitosamente en Docker: {output_path}"
        
    except Exception as e:
        error_msg = f"Error generando PDF en Docker: {str(e)}"
        print(f"⚠️ {error_msg}")
        return False, error_msg

def generate_pdf_with_fallback(html_string, output_path, base_url=None):
    """
    Generar PDF con múltiples intentos y fallbacks
    """
    # Primer intento: configuración Docker optimizada
    success, message = generate_pdf_docker_safe(html_string, output_path, base_url)
    if success:
        return success, message
    
    # Segundo intento: configuración mínima
    try:
        print("🔄 Intentando configuración mínima...")
        html = HTML(string=html_string, base_url=base_url)
        html.write_pdf(output_path)
        return True, f"PDF generado con configuración mínima: {output_path}"
    except Exception as e:
        error_msg = f"Error con configuración mínima: {str(e)}"
        print(f"⚠️ {error_msg}")
        return False, error_msg

def test_weasyprint_docker():
    """Probar WeasyPrint en Docker"""
    try:
        # HTML de prueba simple
        test_html = '''
        <html>
        <head>
            <title>Test WeasyPrint Docker</title>
        </head>
        <body>
            <h1>Test WeasyPrint en Docker</h1>
            <p>Este es un test para verificar que WeasyPrint funciona correctamente en Docker.</p>
            <table>
                <tr><th>Columna 1</th><th>Columna 2</th></tr>
                <tr><td>Dato 1</td><td>Dato 2</td></tr>
            </table>
        </body>
        </html>
        '''
        
        # Generar PDF de prueba
        success, message = generate_pdf_docker_safe(
            test_html, 
            '/tmp/test_weasyprint_docker.pdf'
        )
        
        if success:
            print("✅ WeasyPrint funciona correctamente en Docker")
            return True
        else:
            print("❌ WeasyPrint no funciona en Docker")
            return False
            
    except Exception as e:
        print(f"❌ Error probando WeasyPrint en Docker: {e}")
        return False

if __name__ == '__main__':
    test_weasyprint_docker()
