# Configuración SSL/HTTPS - BioAnalisis

## ✅ Estado Actual: FUNCIONANDO

### 🌐 Dominios Configurados
- **Frontend**: `bioanalisis.com` → Puerto 3000 (aplicación React/Next.js)
- **Backend**: `bioanalisisadmin.com` → Puerto 8000 (Django REST API)

### 🔒 Certificados SSL
- **Tipo**: Autofirmados para desarrollo local
- **Ubicación**: `./ssl/`
- **Archivos**:
  - `bioanalisis.crt` - Certificado para bioanalisis.com
  - `nginx-selfsigned.crt` - Certificado para bioanalisisadmin.com
  - `nginx-selfsigned.key` - Clave privada
  - `dhparam.pem` - Parámetros Diffie-Hellman

### 🐳 Docker Services
```bash
# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs nginx
docker-compose logs web

# Reiniciar servicios
docker-compose restart
```

### 📝 Archivo Hosts (C:\Windows\System32\drivers\etc\hosts)
```
127.0.0.1    bioanalisis.com
127.0.0.1    www.bioanalisis.com
127.0.0.1    bioanalisisadmin.com
127.0.0.1    www.bioanalisisadmin.com
```

### 🔧 Puertos
- **80**: HTTP (redirige a HTTPS)
- **443**: HTTPS
- **8000**: Django (directo)
- **3000**: Frontend (directo)

### 🚀 Cómo Usar

#### 1. Acceder al Backend (Django Admin)
```
https://bioanalisisadmin.com
```
- Si aparece advertencia de seguridad: "Avanzado" → "Continuar"
- El certificado se confiará automáticamente

#### 2. Acceder al Frontend
```
https://bioanalisis.com
```
- Redirige desde HTTP automáticamente

#### 3. API Endpoints
```
https://bioanalisisadmin.com/api/
https://bioanalisisadmin.com/admin/
```

### 🔄 Comandos Útiles

#### Regenerar Certificados
```bash
.\create-ssl-certs.bat
```

#### Instalar Certificados en Windows
```bash
.\install-cert-windows.bat
```

#### Probar Conectividad
```bash
.\test-ssl.bat
```

#### Reiniciar Todo
```bash
docker-compose down
docker-compose up -d
```

### ⚠️ Notas Importantes

1. **Certificados Autofirmados**: Solo para desarrollo local
2. **Producción**: Usar Let's Encrypt o certificados comerciales
3. **Navegador**: La primera vez mostrará advertencia de seguridad
4. **Frontend**: Asegúrate de que esté corriendo en puerto 3000

### 🐛 Troubleshooting

#### Si no funciona HTTPS:
1. Verificar que los certificados existan: `dir ssl`
2. Verificar que Nginx esté corriendo: `docker-compose ps`
3. Verificar logs: `docker-compose logs nginx`
4. Reiniciar servicios: `docker-compose restart`

#### Si no se resuelven los dominios:
1. Verificar archivo hosts
2. Limpiar caché DNS: `ipconfig /flushdns`

#### Si hay errores de certificado:
1. Regenerar certificados: `.\create-ssl-certs.bat`
2. Instalar en Windows: `.\install-cert-windows.bat`
3. Reiniciar navegador

### 📊 Estado de Servicios
```bash
# Verificar todos los servicios
docker-compose ps

# Verificar puertos
netstat -an | findstr :80
netstat -an | findstr :443
```

---
**Última actualización**: 9 de Agosto, 2025
**Estado**: ✅ Funcionando correctamente
