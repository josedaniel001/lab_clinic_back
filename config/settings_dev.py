"""
Configuración de desarrollo para runserver
Para usar: python manage.py runserver --settings=config.settings_dev
"""

from .settings import *

# Configuración de cache en memoria para desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session configuration (base de datos)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Configuración de base de datos PostgreSQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'labdb',
        'USER': 'labuser',
        'PASSWORD': 'labpass',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

print("🔧 Configuración de desarrollo activada")
print("📝 Cache: Memoria local")
print("💾 Sessions: Base de datos")
print("🗄️  Database: PostgreSQL local")
print("🚫 Redis: Deshabilitado")
print("🌐 Servidor: runserver") 