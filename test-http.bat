@echo off
echo.
echo ========================================
echo    PRUEBA DE CONECTIVIDAD HTTP
echo ========================================
echo.

echo 🔍 Probando endpoint health (HTTP)...
curl -I http://bioanalisisadmin.com/api/health

echo.
echo 🔑 Probando endpoint token (HTTP)...
curl -I http://bioanalisisadmin.com/api/token/

echo.
echo 🌐 Probando frontend (HTTP)...
curl -I http://bioanalisis.com

echo.
echo ✅ Pruebas completadas!
echo.
echo 📝 INSTRUCCIONES:
echo 1. Abre tu navegador
echo 2. Ve a http://bioanalisisadmin.com
echo 3. Ve a http://bioanalisis.com
echo 4. No deberían aparecer errores SSL
echo.
pause
