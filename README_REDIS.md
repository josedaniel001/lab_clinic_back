# 🔴 Configuración con Redis - Lab Clinic Backend

Esta configuración incluye **Redis** para cache y sesiones, **PostgreSQL local** con pgAdmin4, y **Nginx** para servir archivos estáticos.

## 🚀 Características

- **🔴 Redis**: Cache y sesiones de Django
- **🗄️ PostgreSQL**: Base de datos local con pgAdmin4
- **📊 Nginx**: Servidor web para archivos estáticos
- **🐳 Docker**: Contenedores optimizados con Alpine Linux
- **📁 Almacenamiento**: Archivos en `C:\lab_clinic\`

## 📋 Prerrequisitos

- Docker Desktop para Windows
- PostgreSQL instalado localmente con pgAdmin4
- Git

## 🛠️ Configuración Inicial

### 1. Crear carpetas en Windows
```cmd
# Ejecutar el script automático
setup-windows-folders.bat
```

### 2. Configurar PostgreSQL local
Asegúrate de que PostgreSQL esté corriendo con:
- **Host**: localhost
- **Puerto**: 5432
- **Base de datos**: labdb
- **Usuario**: labuser
- **Contraseña**: labpass

### 3. Crear archivo de variables de entorno
```bash
cp env.example .env
```

## 🚀 Comandos de Uso

### Desarrollo
```bash
# Iniciar servicios
./docker-scripts.sh dev-start

# Ver logs
./docker-scripts.sh dev-logs

# Entrar al contenedor
./docker-scripts.sh dev-shell

# Parar servicios
./docker-scripts.sh dev-stop
```

### Redis
```bash
# Entrar a Redis CLI
./docker-scripts.sh redis-cli

# Ver logs de Redis
./docker-scripts.sh redis-logs

# Probar conexiones
./docker-scripts.sh test-connections
```

### Utilidades
```bash
# Crear superusuario
./docker-scripts.sh superuser

# Ejecutar migraciones
./docker-scripts.sh migrate

# Abrir carpeta de archivos
./docker-scripts.sh open-media

# Ver estado de servicios
./docker-scripts.sh status
```

## 📁 Estructura de Servicios

### **1. Redis (🔴)**
- **Puerto**: 6379
- **Imagen**: redis:7-alpine
- **Uso**: Cache de Django y sesiones
- **Acceso**: `localhost:6379`

### **2. Django (🐍)**
- **Puerto**: 8000
- **Base**: Python 3.11 Alpine
- **Servidor**: Gunicorn con 3 workers
- **Archivos**: `C:\lab_clinic\media\`

### **3. Nginx (📊)**
- **Puerto**: 80
- **Imagen**: nginx:alpine
- **Funciones**: Archivos estáticos, media, proxy reverso

### **4. PostgreSQL (🗄️)**
- **Puerto**: 5432 (local)
- **Acceso**: pgAdmin4
- **Base de datos**: labdb

## 🔧 Configuración de Redis

### **Cache de Django:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
    }
}
```

### **Sesiones:**
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## 📊 Beneficios de Redis

### **1. Cache de Django:**
- **Consultas de base de datos**: Cache automático
- **Templates**: Cache de templates compilados
- **Sesiones**: Sesiones en memoria (más rápido)

### **2. Mejor Rendimiento:**
- **Respuestas más rápidas**: Cache de datos frecuentes
- **Menos carga en PostgreSQL**: Consultas cacheadas
- **Sesiones persistentes**: Entre reinicios de contenedores

### **3. Escalabilidad:**
- **Múltiples workers**: Comparten cache
- **Balanceo de carga**: Cache centralizado
- **Monitoreo**: Métricas de cache

## 🛠️ Comandos de Redis

### **Entrar a Redis CLI:**
```bash
./docker-scripts.sh redis-cli
```

### **Comandos útiles en Redis CLI:**
```redis
# Ver todas las claves
KEYS *

# Ver información del servidor
INFO

# Ver estadísticas de memoria
INFO memory

# Limpiar cache
FLUSHALL

# Ver claves de Django
KEYS django*

# Ver sesiones
KEYS django.contrib.sessions*
```

### **Monitorear Redis:**
```bash
# Ver logs en tiempo real
./docker-scripts.sh redis-logs

# Ver estadísticas
docker-compose -f docker-compose.simple.yml exec redis redis-cli INFO
```

## 🔍 Troubleshooting

### **Problema: Redis no conecta**
```bash
# Verificar que Redis esté corriendo
docker-compose -f docker-compose.simple.yml ps

# Ver logs de Redis
./docker-scripts.sh redis-logs

# Probar conexión
./docker-scripts.sh test-connections
```

### **Problema: PostgreSQL no conecta**
```bash
# Verificar PostgreSQL local
pg_isready -h localhost -p 5432

# Verificar credenciales
psql -h localhost -U labuser -d labdb
```

### **Problema: Cache no funciona**
```bash
# Verificar configuración de cache
docker-compose -f docker-compose.simple.yml exec web python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

## 📈 Monitoreo

### **Ver estadísticas de Redis:**
```bash
# Entrar a Redis CLI
./docker-scripts.sh redis-cli

# Ver estadísticas
INFO
INFO memory
INFO stats
```

### **Ver logs de Django:**
```bash
# Ver logs en tiempo real
./docker-scripts.sh dev-logs

# Ver logs específicos
docker-compose -f docker-compose.simple.yml logs -f web
```

## 🔄 Actualizaciones

### **Actualizar código:**
```bash
git pull
./docker-scripts.sh dev-stop
./docker-scripts.sh dev-start
```

### **Actualizar dependencias:**
```bash
# Editar requirements.txt
./docker-scripts.sh dev-stop
docker-compose -f docker-compose.simple.yml build --no-cache
./docker-scripts.sh dev-start
```

## 📞 Soporte

Si tienes problemas:

1. **Verificar servicios**: `./docker-scripts.sh status`
2. **Ver logs**: `./docker-scripts.sh dev-logs`
3. **Probar conexiones**: `./docker-scripts.sh test-connections`
4. **Reiniciar**: `./docker-scripts.sh dev-restart`

## 🎯 Ventajas de esta Configuración

### **✅ Rendimiento:**
- Cache automático de consultas
- Sesiones en memoria
- Archivos estáticos servidos por Nginx

### **✅ Escalabilidad:**
- Redis compartido entre workers
- Cache centralizado
- Fácil escalado horizontal

### **✅ Desarrollo:**
- PostgreSQL local con pgAdmin4
- Redis para testing
- Archivos persistentes en C:\lab_clinic\

### **✅ Producción:**
- Configuración optimizada
- Headers de seguridad
- Logs centralizados

---

¡Tu aplicación Django está lista con Redis para cache y sesiones! 🚀 