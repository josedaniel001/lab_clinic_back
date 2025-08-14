@echo off
echo 🔐 Instalando certificados SSL en Windows...

REM Verificar que los certificados existen
if not exist ssl\nginx-selfsigned.crt (
    echo ❌ No se encontró el certificado ssl\nginx-selfsigned.crt
    echo 💡 Ejecuta primero: create-ssl-certs.bat
    pause
    exit /b 1
)

REM Instalar certificado en el almacén de certificados de Windows
echo 📋 Instalando certificado en el almacén de certificados...
certutil -addstore -f "ROOT" ssl\nginx-selfsigned.crt

if %errorlevel% equ 0 (
    echo ✅ Certificado instalado exitosamente!
    echo 🌐 Ahora puedes acceder a:
    echo    - https://bioanalisis.com
    echo    - https://bioanalisisadmin.com
    echo.
    echo ⚠️  Si el navegador sigue mostrando advertencias:
    echo    1. Abre https://bioanalisisadmin.com
    echo    2. Haz clic en "Avanzado"
    echo    3. Haz clic en "Continuar a bioanalisisadmin.com (no seguro)"
    echo    4. El certificado se confiará automáticamente
) else (
    echo ❌ Error al instalar el certificado
    echo 💡 Intenta ejecutar como administrador
)

pause
