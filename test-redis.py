#!/usr/bin/env python3
"""
Script para probar la conexión a Redis
"""

import redis
import os
import sys

def test_redis_connection():
    """Prueba la conexión a Redis"""
    try:
        # Obtener URL de Redis desde variables de entorno
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        print(f"🔗 Conectando a Redis: {redis_url}")
        
        # Crear conexión a Redis
        r = redis.from_url(redis_url)
        
        # Probar conexión
        r.ping()
        print("✅ Conexión a Redis exitosa!")
        
        # Probar operaciones básicas
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        print(f"✅ Test de escritura/lectura: {value}")
        
        # Limpiar
        r.delete('test_key')
        print("✅ Test completado exitosamente")
        
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Error de conexión a Redis: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_django_cache():
    """Prueba el cache de Django"""
    try:
        import django
        from django.conf import settings
        from django.core.cache import cache
        
        print("🔗 Probando cache de Django...")
        
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
        
        # Probar cache
        cache.set('django_test', 'django_value', timeout=60)
        value = cache.get('django_test')
        print(f"✅ Test de cache Django: {value}")
        
        # Limpiar
        cache.delete('django_test')
        print("✅ Test de Django cache completado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en cache de Django: {e}")
        return False

def test_postgres_connection():
    """Prueba la conexión a PostgreSQL"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Obtener URL de PostgreSQL desde variables de entorno
        database_url = os.environ.get('DATABASE_URL', 'postgresql://labuser:labpass@localhost:5432/labdb')
        
        print(f"🔗 Conectando a PostgreSQL: {database_url}")
        
        # Parsear URL
        parsed = urlparse(database_url)
        
        # Conectar
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        # Probar conexión
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        print(f"✅ Conexión a PostgreSQL exitosa! Versión: {version[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de conexión...")
    print("=" * 50)
    
    # Probar Redis
    print("\n1️⃣ Probando Redis...")
    redis_ok = test_redis_connection()
    
    # Probar cache de Django
    print("\n2️⃣ Probando cache de Django...")
    django_cache_ok = test_django_cache()
    
    # Probar PostgreSQL
    print("\n3️⃣ Probando PostgreSQL...")
    postgres_ok = test_postgres_connection()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 Resumen de pruebas:")
    print(f"   Redis: {'✅ OK' if redis_ok else '❌ FALLÓ'}")
    print(f"   Django Cache: {'✅ OK' if django_cache_ok else '❌ FALLÓ'}")
    print(f"   PostgreSQL: {'✅ OK' if postgres_ok else '❌ FALLÓ'}")
    
    if redis_ok and django_cache_ok and postgres_ok:
        print("\n🎉 ¡Todas las conexiones funcionan correctamente!")
        return 0
    else:
        print("\n⚠️  Algunas conexiones fallaron. Revisa la configuración.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 