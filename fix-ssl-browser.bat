@echo off
echo.
echo ========================================
echo    SOLUCIONAR SSL EN NAVEGADOR
echo ========================================
echo.

echo 🔍 Verificando certificados existentes...
certutil -store My | findstr bioanalisis

echo.
echo 🗑️ Eliminando certificados antiguos...
certutil -delstore My bioanalisisadmin.com 2>nul
certutil -delstore My bioanalisis.com 2>nul

echo.
echo 🔧 Instalando certificados en el almacén de certificados raíz...
certutil -addstore -f ROOT ssl\nginx-selfsigned.crt
certutil -addstore -f ROOT ssl\bioanalisis.crt

echo.
echo 🔑 Instalando certificados en el almacén personal...
certutil -addstore -f My ssl\nginx-selfsigned.crt
certutil -addstore -f My ssl\bioanalisis.crt

echo.
echo 🔄 Limpiando caché DNS...
ipconfig /flushdns

echo.
echo ✅ Certificados instalados!
echo.
echo 📝 INSTRUCCIONES PARA EL NAVEGADOR:
echo 1. Cierra completamente el navegador
echo 2. Abre el navegador nuevamente
echo 3. Ve a https://bioanalisisadmin.com
echo 4. Si aparece advertencia: "Avanzado" → "Continuar"
echo 5. El certificado se confiará automáticamente
echo.
echo 🌐 URLs para probar:
echo - https://bioanalisisadmin.com
echo - https://bioanalisis.com
echo.
pause
