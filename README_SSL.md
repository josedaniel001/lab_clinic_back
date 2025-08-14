# 🔐 Configuración SSL/HTTPS

## 📋 Resumen

Esta configuración permite usar HTTPS con certificados SSL autofirmados para desarrollo local. En producción, se recomienda usar certificados de una autoridad certificadora (Let's Encrypt, etc.).

## 🚀 Configuración Rápida

### 1. Generar certificados SSL

**Windows:**
```bash
create-ssl-certs.bat
```

**Linux/Mac:**
```bash
chmod +x create-ssl-certs.sh
./create-ssl-certs.sh
```

### 2. Instalar certificados en el sistema

**Windows (ejecutar como administrador):**
```bash
install-cert-windows.bat
```

**macOS:**
```bash
chmod +x install-cert-mac.sh
./install-cert-mac.sh
```

### 3. Levantar servicios
```bash
docker-compose up -d
```

## 🌐 URLs Disponibles

Una vez configurado, puedes acceder a:

- **Frontend:** https://bioanalisis.com
- **Backend API:** https://bioanalisisadmin.com/api/
- **Admin:** https://bioanalisisadmin.com/admin/
- **PDFs:** https://bioanalisisadmin.com/media/entrevistas/1/entrevista_ENT-20250810-0001.pdf

## ⚠️ Advertencias del Navegador

Los certificados autofirmados generarán advertencias de seguridad. Para confiar en ellos:

1. Abre https://bioanalisisadmin.com
2. Haz clic en "Avanzado"
3. Haz clic en "Continuar a bioanalisisadmin.com (no seguro)"
4. El certificado se confiará automáticamente

## 📁 Archivos de Certificados

```
ssl/
├── nginx-selfsigned.key    # Clave privada
├── nginx-selfsigned.crt    # Certificado para bioanalisisadmin.com
├── bioanalisis.crt         # Certificado para bioanalisis.com
└── dhparam.pem            # Parámetros Diffie-Hellman
```

## 🔧 Configuración de Nginx

El archivo `nginx.conf` está configurado para:

- Redirigir HTTP a HTTPS automáticamente
- Usar TLS 1.2 y 1.3
- Configurar headers de seguridad
- Servir archivos estáticos y media por HTTPS

## 🛠️ Troubleshooting

### Error: "SSL certificate is not trusted"

1. Verifica que instalaste el certificado correctamente
2. Reinicia el navegador
3. Limpia la caché del navegador
4. Acepta manualmente el certificado la primera vez

### Error: "Connection refused" en puerto 443

1. Verifica que nginx esté corriendo:
   ```bash
   docker-compose ps nginx
   ```

2. Verifica que el puerto 443 esté expuesto:
   ```bash
   docker-compose logs nginx
   ```

### Error: "Certificate file not found"

1. Verifica que los certificados existen:
   ```bash
   ls -la ssl/
   ```

2. Verifica que el volumen está montado correctamente:
   ```bash
   docker exec lab_clinic_nginx ls -la /etc/nginx/ssl/
   ```

## 🔄 Renovar Certificados

Los certificados expiran en 365 días. Para renovarlos:

1. Eliminar certificados antiguos:
   ```bash
   rm -rf ssl/
   ```

2. Generar nuevos certificados:
   ```bash
   ./create-ssl-certs.sh  # o create-ssl-certs.bat en Windows
   ```

3. Instalar nuevos certificados:
   ```bash
   ./install-cert-mac.sh  # o install-cert-windows.bat en Windows
   ```

4. Reiniciar nginx:
   ```bash
   docker-compose restart nginx
   ```

## 🚀 Producción

Para producción, reemplaza los certificados autofirmados con certificados de una autoridad certificadora:

1. **Let's Encrypt (gratuito):**
   ```bash
   certbot certonly --webroot -w /var/www/html -d bioanalisisadmin.com
   ```

2. **Actualizar nginx.conf:**
   ```nginx
   ssl_certificate /etc/letsencrypt/live/bioanalisisadmin.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/bioanalisisadmin.com/privkey.pem;
   ```

3. **Renovación automática:**
   ```bash
   crontab -e
   # Agregar: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

## 🔐 Seguridad

- Los certificados autofirmados son solo para desarrollo
- En producción, usa certificados de autoridades certificadoras
- Mantén las claves privadas seguras
- Renueva los certificados antes de que expiren
- Usa HSTS para forzar HTTPS
- Configura headers de seguridad apropiados
