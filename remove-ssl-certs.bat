@echo off
echo.
echo ========================================
echo    ELIMINAR CERTIFICADOS SSL
echo ========================================
echo.

echo 🔍 Verificando certificados existentes...
certutil -store My | findstr bioanalisis

echo.
echo 🗑️ Eliminando certificados del almacén personal...
certutil -delstore My bioanalisisadmin.com 2>nul
certutil -delstore My bioanalisis.com 2>nul

echo.
echo 🗑️ Eliminando certificados del almacén raíz...
certutil -delstore ROOT bioanalisisadmin.com 2>nul
certutil -delstore ROOT bioanalisis.com 2>nul

echo.
echo 🔄 Limpiando caché DNS...
ipconfig /flushdns

echo.
echo ✅ Certificados eliminados!
echo.
echo 📝 NOTAS:
echo - Los certificados SSL han sido eliminados
echo - Ahora el sistema funciona completamente con HTTP
echo - No hay problemas de certificados autofirmados
echo.
echo 🌐 URLs actuales:
echo - http://bioanalisisadmin.com
echo - http://bioanalisis.com
echo.
pause
