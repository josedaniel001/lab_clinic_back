# Configuración HTTP - BioAnalisis (Desarrollo)

## ✅ Estado Actual: FUNCIONANDO CON HTTP

### 🌐 Dominios Configurados
- **Frontend**: `http://bioanalisis.com` → Puerto 3000 (aplicación React/Next.js)
- **Backend**: `http://bioanalisisadmin.com` → Puerto 8000 (Django REST API)

### 🔧 Configuración Actual
- **SSL**: Deshabilitado para desarrollo
- **Protocolo**: HTTP únicamente
- **CORS**: Configurado para HTTP
- **Certificados**: No necesarios

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
- **80**: HTTP (Nginx proxy)
- **8000**: Django (directo)
- **3000**: Frontend (directo)

### 🚀 Cómo Usar

#### 1. Acceder al Backend (Django Admin)
```
http://bioanalisisadmin.com
```

#### 2. Acceder al Frontend
```
http://bioanalisis.com
```

#### 3. API Endpoints
```
http://bioanalisisadmin.com/api/
http://bioanalisisadmin.com/admin/
```

### 🔄 Comandos Útiles

#### Probar Conectividad
```bash
.\test-http.bat
```

#### Reiniciar Todo
```bash
docker-compose down
docker-compose up -d
```

#### Ver Logs
```bash
docker-compose logs web
docker-compose logs nginx
```

### ⚠️ Notas Importantes

1. **HTTP para Desarrollo**: Esta configuración es solo para desarrollo local
2. **Sin SSL**: No hay problemas de certificados autofirmados
3. **CORS Funcionando**: Las peticiones entre frontend y backend funcionan correctamente
4. **Producción**: Para producción, habilitar SSL con certificados válidos

### 🐛 Troubleshooting

#### Si no funciona:
1. Verificar que los contenedores estén corriendo: `docker-compose ps`
2. Verificar logs: `docker-compose logs nginx`
3. Limpiar caché del navegador: `Ctrl+Shift+Delete`
4. Reiniciar servicios: `docker-compose restart`

#### Si hay errores de CORS:
1. Verificar configuración CORS en `config/settings.py`
2. Reiniciar contenedor Django: `docker-compose restart web`

#### Si no se resuelven los dominios:
1. Verificar archivo hosts
2. Limpiar caché DNS: `ipconfig /flushdns`

### 📊 Estado de Servicios
```bash
# Verificar todos los servicios
docker-compose ps

# Verificar puertos
netstat -an | findstr :80
netstat -an | findstr :8000
```

### 🔄 Para Habilitar SSL en Producción

1. **Descomentar configuración SSL** en `nginx.conf`
2. **Generar certificados válidos** (Let's Encrypt, etc.)
3. **Actualizar CORS** para incluir URLs HTTPS
4. **Actualizar docker-compose.yml** con variables HTTPS

---
**Última actualización**: 9 de Agosto, 2025
**Estado**: ✅ Funcionando con HTTP
**Modo**: Desarrollo
