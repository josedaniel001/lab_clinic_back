# 🏥 Lab Clinic Backend - Docker

Configuración Docker optimizada para tu proyecto Django con Redis, PostgreSQL local y Nginx.

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

### Básicos
```bash
# Iniciar servicios
./docker-scripts.sh start

# Parar servicios
./docker-scripts.sh stop

# Ver logs
./docker-scripts.sh logs

# Entrar al contenedor
./docker-scripts.sh shell
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

## 📁 Estructura de Archivos

```
C:\lab_clinic\
├── media\
│   ├── etiquetas\     # PDFs y etiquetas
│   ├── logos\         # Logos del sistema
│   └── uploads\       # Archivos subidos
├── staticfiles\       # Archivos estáticos
├── logs\              # Logs de la aplicación
└── ssl\               # Certificados SSL
```

## 🔧 Servicios

### **1. Redis (🔴)**
- **Puerto**: 6379
- **Uso**: Cache de Django y sesiones

### **2. Django (🐍)**
- **Puerto**: 8000
- **Servidor**: Gunicorn con 3 workers

### **3. Nginx (📊)**
- **Puerto**: 80
- **Funciones**: Archivos estáticos, media, proxy reverso

### **4. PostgreSQL (🗄️)**
- **Puerto**: 5432 (local)
- **Acceso**: pgAdmin4

## 📊 Beneficios de Redis

- **Cache automático** de consultas de base de datos
- **Sesiones en memoria** (más rápido)
- **Mejor rendimiento** general
- **Escalabilidad** para múltiples workers

## 🔍 Troubleshooting

### **Problema: Redis no conecta**
```bash
./docker-scripts.sh test-connections
./docker-scripts.sh redis-logs
```

### **Problema: PostgreSQL no conecta**
```bash
# Verificar PostgreSQL local
pg_isready -h localhost -p 5432
```

### **Problema: Puerto ocupado**
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000
```

## 📞 Soporte

Si tienes problemas:

1. **Verificar servicios**: `./docker-scripts.sh status`
2. **Ver logs**: `./docker-scripts.sh logs`
3. **Probar conexiones**: `./docker-scripts.sh test-connections`
4. **Reiniciar**: `./docker-scripts.sh restart`

---

¡Tu aplicación Django está lista con Redis para cache y sesiones! 🚀


