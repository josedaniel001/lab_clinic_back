@echo off
echo.
echo ========================================
echo    PRUEBA DE ENDPOINTS API CON CURL
echo ========================================
echo.

echo 🔍 Probando endpoint health (HTTP)...
curl -I http://bioanalisisadmin.com/api/health

echo.
echo 🔒 Probando endpoint health (HTTPS)...
curl -I https://bioanalisisadmin.com/api/health

echo.
echo 🔑 Probando endpoint token (HTTP)...
curl -I http://bioanalisisadmin.com/api/token/

echo.
echo 🔐 Probando endpoint token (HTTPS)...
curl -I https://bioanalisisadmin.com/api/token/

echo.
echo 🌐 Probando directamente Django (puerto 8000)...
curl -I http://localhost:8000/api/health

echo.
echo ✅ Pruebas completadas!
echo.
echo 📝 INTERPRETACIÓN:
echo - Si HTTP devuelve 301: Redirección a HTTPS (normal)
echo - Si HTTPS devuelve 200: Funciona correctamente
echo - Si HTTPS devuelve error de certificado: Normal para autofirmados
echo - Si puerto 8000 devuelve 200: Django funciona correctamente
echo.
pause
