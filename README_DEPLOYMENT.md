# 🚀 Flujo de Deployment con Docker Hub

## 📋 Resumen del Flujo

1. **Desarrollo Local** → Construir imagen → Subir a Docker Hub
2. **Producción** → Descargar imagen → Levantar con docker-compose

## 🔧 Configuración Inicial

### 1. Configurar Docker Hub
```bash
# Loguearse en Docker Hub
docker login

# Verificar que estás logueado
docker info | grep Username
```

### 2. Actualizar configuración
Editar `build-and-push.bat` (Windows) o `build-and-push.sh` (Linux/Mac):
```bash
DOCKER_USERNAME="tu-usuario-real"  # Cambiar por tu usuario de Docker Hub
IMAGE_NAME="lab-clinic-backend"
```

### 3. Actualizar docker-compose.prod.yml
```yaml
web:
  image: tu-usuario-real/lab-clinic-backend:latest  # Cambiar por tu imagen
```

## 🏗️ Desarrollo Local

### Construir y subir imagen
```bash
# Windows
build-and-push.bat

# Linux/Mac
./build-and-push.sh

# Con versión específica
build-and-push.bat v1.0.0
./build-and-push.sh v1.0.0
```

### Probar imagen localmente
```bash
# Construir imagen local
docker build -t lab-clinic-backend:test .

# Probar con docker-compose local
docker-compose up -d

# Ver logs
docker-compose logs -f web
```

## 🚀 Producción

### 1. Preparar servidor
```bash
# Crear directorios necesarios
mkdir -p media staticfiles logs

# Crear certificados SSL (desarrollo local)
# Windows:
create-ssl-certs.bat

# Linux/Mac:
chmod +x create-ssl-certs.sh
./create-ssl-certs.sh

# Instalar certificados en el sistema
# Windows (ejecutar como administrador):
install-cert-windows.bat

# macOS:
chmod +x install-cert-mac.sh
./install-cert-mac.sh

# Descargar archivos de configuración
# - docker-compose.prod.yml
# - nginx.conf (configurado para SSL)
# - .env (variables de entorno)
# - ssl/ (certificados SSL)
```

### 2. Configurar variables de entorno
Crear archivo `.env`:
```env
DEBUG=False
SECRET_KEY=tu-secret-key-super-seguro
DATABASE_URL=postgresql://usuario:password@host:5432/database
CORS_ALLOWED_ORIGINS=http://tu-dominio.com,http://www.tu-dominio.com
JWT_SECRET_KEY=tu-jwt-secret-key
TIME_ZONE=America/Guatemala
```

### 3. Levantar aplicación
```bash
# Descargar imagen
docker pull tu-usuario/lab-clinic-backend:latest

# Levantar servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f web
```

## 📁 Estructura de Archivos en Producción

```
servidor/
├── docker-compose.prod.yml
├── nginx.conf
├── .env
├── ssl/
│   ├── nginx-selfsigned.key
│   ├── nginx-selfsigned.crt
│   ├── bioanalisis.crt
│   └── dhparam.pem
├── media/
├── staticfiles/
└── logs/
```

## 🔄 Actualizaciones

### 1. Desarrollo
```bash
# Hacer cambios en el código
# Construir nueva versión
build-and-push.bat v1.1.0

# O actualizar latest
build-and-push.bat
```

### 2. Producción
```bash
# Detener servicios
docker-compose -f docker-compose.prod.yml down

# Descargar nueva imagen
docker pull tu-usuario/lab-clinic-backend:latest

# Levantar con nueva imagen
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose -f docker-compose.prod.yml logs -f web
```

## 🛠️ Comandos Útiles

### Verificar estado
```bash
# Estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f web

# Logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs
```

### Ejecutar comandos en el contenedor
```bash
# Migraciones
docker exec -it lab_clinic_web python manage.py migrate

# Recolectar archivos estáticos
docker exec -it lab_clinic_web python manage.py collectstatic --noinput

# Shell de Django
docker exec -it lab_clinic_web python manage.py shell

# Crear superusuario
docker exec -it lab_clinic_web python manage.py createsuperuser
```

### Backup y restore
```bash
# Backup de base de datos (desde host)
pg_dump -h host -U usuario database > backup.sql

# Restore de base de datos
psql -h host -U usuario database < backup.sql
```

## 🔍 Troubleshooting

### Problemas comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar variables de entorno
   docker exec -it lab_clinic_web env | grep DATABASE
   
   # Probar conexión
   docker exec -it lab_clinic_web python manage.py check --database default
   ```

2. **Error de permisos en volúmenes**
   ```bash
   # Verificar permisos
   ls -la media/ staticfiles/ logs/
   
   # Corregir permisos si es necesario
   chmod 755 media/ staticfiles/ logs/
   ```

3. **Imagen no se actualiza**
   ```bash
   # Forzar descarga
   docker pull tu-usuario/lab-clinic-backend:latest
   
   # Limpiar imágenes antiguas
   docker image prune -f
   ```

### Logs detallados
```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs

# Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs redis
docker-compose -f docker-compose.prod.yml logs nginx
```

## 📊 Monitoreo

### Health check
```bash
# Verificar que la aplicación responde
curl http://localhost:8000/api/health/

# Verificar admin
curl http://localhost:8000/admin/

# Verificar HTTPS
curl -k https://bioanalisisadmin.com/api/health/
curl -k https://bioanalisisadmin.com/admin/
```

### Recursos del sistema
```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df
```

## 🔐 Seguridad

### Variables de entorno críticas
- `SECRET_KEY`: Cambiar en producción
- `JWT_SECRET_KEY`: Cambiar en producción
- `DATABASE_URL`: Usar credenciales seguras
- `DEBUG`: Siempre False en producción

### Firewall
```bash
# Solo exponer puertos necesarios
# 8000: API
# 80: Nginx (si usas)
# 6379: Redis (solo local si es posible)
```

## 📞 Soporte

Si encuentras problemas:

1. Verificar logs: `docker-compose -f docker-compose.prod.yml logs web`
2. Verificar configuración: `docker exec -it lab_clinic_web env`
3. Probar imagen localmente antes de subir
4. Verificar que todas las variables de entorno estén configuradas
