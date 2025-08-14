# Usar Python 3.11 con Alpine (como funcionaba originalmente)
FROM python:3.11-alpine

# Instalar dependencias del sistema necesarias
RUN apk add --no-cache \
    postgresql-client \
    postgresql-dev \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    cairo-dev \
    pango-dev \
    gdk-pixbuf-dev \
    jpeg-dev \
    zlib-dev \
    libxml2-dev \
    libxslt-dev \
    openssl-dev \
    curl \
    # Fuentes para WeasyPrint
    fontconfig \
    ttf-dejavu \
    ttf-liberation

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    # Configuración para WeasyPrint
    WEASYPRINT_FONTS=/usr/share/fonts \
    FONTCONFIG_PATH=/etc/fonts

# Crear usuario no-root para seguridad
RUN addgroup -g 1000 django && adduser -D -s /bin/sh -u 1000 -G django django

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios y cambiar permisos
RUN mkdir -p /app/media /app/staticfiles /app/logs && \
    chown -R django:django /app

# Configurar fuentes para WeasyPrint
RUN fc-cache -fv

# Cambiar al usuario no-root
USER django

# Exponer puerto
EXPOSE 8000

# Comando por defecto (será sobrescrito por docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "config.wsgi:application"] 