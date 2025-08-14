#!/bin/bash

echo "🔐 Creando certificados SSL autofirmados para desarrollo local..."

# Crear directorio para certificados
mkdir -p ssl

# Generar certificado privado
openssl genrsa -out ssl/nginx-selfsigned.key 2048

# Generar certificado público
openssl req -new -x509 -key ssl/nginx-selfsigned.key -out ssl/nginx-selfsigned.crt -days 365 -subj "/C=GT/ST=Guatemala/L=Guatemala/O=BioAnalisis/OU=IT/CN=bioanalisisadmin.com"

# Generar certificado para bioanalisis.com también
openssl req -new -x509 -key ssl/nginx-selfsigned.key -out ssl/bioanalisis.crt -days 365 -subj "/C=GT/ST=Guatemala/L=Guatemala/O=BioAnalisis/OU=IT/CN=bioanalisis.com"

# Generar archivo de configuración de Diffie-Hellman (opcional, para mayor seguridad)
openssl dhparam -out ssl/dhparam.pem 2048

echo "✅ Certificados SSL creados exitosamente!"
echo "📁 Archivos generados:"
echo "   - ssl/nginx-selfsigned.key (clave privada)"
echo "   - ssl/nginx-selfsigned.crt (certificado para bioanalisisadmin.com)"
echo "   - ssl/bioanalisis.crt (certificado para bioanalisis.com)"
echo "   - ssl/dhparam.pem (parámetros Diffie-Hellman)"
echo ""
echo "⚠️  IMPORTANTE: Estos son certificados autofirmados para desarrollo."
echo "   En producción, usa certificados de una autoridad certificadora (Let's Encrypt, etc.)"
