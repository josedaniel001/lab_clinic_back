@echo off
echo.
echo ========================================
echo    PRUEBA DE CONECTIVIDAD SSL
echo ========================================
echo.

echo 🔍 Probando HTTP (deberia redirigir a HTTPS)...
curl -I http://bioanalisisadmin.com

echo.
echo 🔒 Probando HTTPS (puede mostrar advertencia de certificado)...
curl -I https://bioanalisisadmin.com

echo.
echo 🌐 Probando frontend...
curl -I http://bioanalisis.com

echo.
echo ✅ Pruebas completadas!
echo.
echo 📝 INSTRUCCIONES:
echo 1. Abre tu navegador
echo 2. Ve a https://bioanalisisadmin.com
echo 3. Si aparece advertencia de seguridad, haz clic en "Avanzado"
echo 4. Haz clic en "Continuar a bioanalisisadmin.com (no seguro)"
echo 5. El certificado se confiara automaticamente
echo.
pause
