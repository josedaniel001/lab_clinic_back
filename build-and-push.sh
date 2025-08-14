#!/bin/bash

# Configuración
DOCKER_USERNAME="josedaniel001"  # Cambiar por tu usuario de Docker Hub
IMAGE_NAME="lab-clinic-backend"
VERSION=${1:-latest}

echo "🚀 Construyendo y subiendo imagen a Docker Hub..."

# Verificar que estás logueado en Docker Hub
if ! docker info | grep -q "Username"; then
    echo "❌ No estás logueado en Docker Hub. Ejecuta: docker login"
    exit 1
fi

# Construir la imagen
echo "🔨 Construyendo imagen: $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION .

if [ $? -ne 0 ]; then
    echo "❌ Error construyendo la imagen"
    exit 1
fi

# Etiquetar como latest si no es la versión por defecto
if [ "$VERSION" != "latest" ]; then
    echo "🏷️ Etiquetando como latest..."
    docker tag $DOCKER_USERNAME/$IMAGE_NAME:$VERSION $DOCKER_USERNAME/$IMAGE_NAME:latest
fi

# Subir la imagen
echo "📤 Subiendo imagen a Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION

if [ $? -ne 0 ]; then
    echo "❌ Error subiendo la imagen"
    exit 1
fi

# Subir latest si no es la versión por defecto
if [ "$VERSION" != "latest" ]; then
    echo "📤 Subiendo versión latest..."
    docker push $DOCKER_USERNAME/$IMAGE_NAME:latest
fi

echo "✅ Imagen subida exitosamente!"
echo "🐳 Imagen disponible en: $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo ""
echo "📋 Para usar en producción:"
echo "1. Actualizar docker-compose.prod.yml con tu imagen"
echo "2. Ejecutar: docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔧 Comandos útiles:"
echo "   docker pull $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
echo "   docker run -it $DOCKER_USERNAME/$IMAGE_NAME:$VERSION /bin/bash"
