#!/bin/bash

# Aplicar migraciones
python manage.py migrate

# Crear superusuario automáticamente (solo si no existe)
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'admin@example.com', 'Admin1234')" \
| python manage.py shell

# Iniciar Gunicorn
gunicorn config.wsgi:application
