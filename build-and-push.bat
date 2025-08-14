@echo off
setlocal enabledelayedexpansion

REM Configuración
set DOCKER_USERNAME=josedaniel001
set IMAGE_NAME=lab-clinic-backend
set VERSION=%1
if "%VERSION%"=="" set VERSION=latest

echo 🚀 Construyendo y subiendo imagen a Docker Hub...

REM Verificar que estás logueado en Docker Hub
docker info | findstr "Username" >nul
if errorlevel 1 (
    echo ❌ No estás logueado en Docker Hub. Ejecuta: docker login
    pause
    exit /b 1
)

REM Construir la imagen
echo 🔨 Construyendo imagen: %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
docker build -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% .

if errorlevel 1 (
    echo ❌ Error construyendo la imagen
    pause
    exit /b 1
)

REM Etiquetar como latest si no es la versión por defecto
if not "%VERSION%"=="latest" (
    echo 🏷️ Etiquetando como latest...
    docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:latest
)

REM Subir la imagen
echo 📤 Subiendo imagen a Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%

if errorlevel 1 (
    echo ❌ Error subiendo la imagen
    pause
    exit /b 1
)

REM Subir latest si no es la versión por defecto
if not "%VERSION%"=="latest" (
    echo 📤 Subiendo versión latest...
    docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest
)

echo ✅ Imagen subida exitosamente!
echo 🐳 Imagen disponible en: %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo.
echo 📋 Para usar en producción:
echo 1. Actualizar docker-compose.prod.yml con tu imagen
echo 2. Ejecutar: docker-compose -f docker-compose.prod.yml up -d
echo.
echo 🔧 Comandos útiles:
echo    docker pull %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
echo    docker run -it %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% /bin/bash

pause
