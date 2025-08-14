@echo off
echo.
echo ========================================
echo    LIMPIAR CACHÉ DEL NAVEGADOR
echo ========================================
echo.

echo 🔄 Limpiando caché DNS...
ipconfig /flushdns

echo.
echo 🔄 Limpiando caché de Chrome/Edge...
taskkill /f /im chrome.exe 2>nul
taskkill /f /im msedge.exe 2>nul
taskkill /f /im firefox.exe 2>nul

echo.
echo 🗑️ Eliminando datos de navegación...
if exist "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" (
    rmdir /s /q "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" 2>nul
    echo Chrome cache eliminada
)

if exist "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" (
    rmdir /s /q "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" 2>nul
    echo Edge cache eliminada
)

if exist "%APPDATA%\Mozilla\Firefox\Profiles" (
    for /d %%i in ("%APPDATA%\Mozilla\Firefox\Profiles\*") do (
        if exist "%%i\cache2" rmdir /s /q "%%i\cache2" 2>nul
    )
    echo Firefox cache eliminada
)

echo.
echo ✅ Limpieza completada!
echo.
echo 📝 INSTRUCCIONES:
echo 1. Abre el navegador
echo 2. Ve a http://bioanalisisadmin.com (NO https)
echo 3. Ve a http://bioanalisis.com (NO https)
echo 4. Si aún redirige, presiona Ctrl+Shift+R para recargar sin caché
echo.
echo 🌐 URLs correctas:
echo - http://bioanalisisadmin.com
echo - http://bioanalisis.com
echo.
pause
