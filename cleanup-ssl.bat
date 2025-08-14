@echo off
echo.
echo ========================================
echo    LIMPIEZA DE CONFIGURACIÓN SSL
echo ========================================
echo.

echo 🗑️ Eliminando archivos de certificados SSL...
if exist ssl\*.crt del ssl\*.crt
if exist ssl\*.key del ssl\*.key
if exist ssl\*.pem del ssl\*.pem

echo.
echo 🔄 Limpiando caché DNS...
ipconfig /flushdns

echo.
echo 🔄 Limpiando caché del navegador...
echo Por favor, limpia manualmente la caché de tu navegador:
echo - Chrome/Edge: Ctrl+Shift+Delete
echo - Firefox: Ctrl+Shift+Delete

echo.
echo ✅ Limpieza completada!
echo.
echo 📝 CONFIGURACIÓN ACTUAL:
echo - Sistema funcionando con HTTP
echo - Sin certificados SSL
echo - Sin problemas de certificados autofirmados
echo.
echo 🌐 URLs para usar:
echo - http://bioanalisisadmin.com
echo - http://bioanalisis.com
echo.
echo ⚠️ NOTA: Si aún aparecen errores de certificados:
echo 1. Cierra completamente el navegador
echo 2. Abre el navegador nuevamente
echo 3. Limpia la caché (Ctrl+Shift+Delete)
echo 4. Accede a las URLs HTTP
echo.
pause
