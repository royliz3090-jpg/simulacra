@echo off
:: Script de aplicación de parche - Traducción SIMULACRA al español latinoamericano
:: Ejecutar como administrador

echo ============================================
echo  SIMULACRA - Parche de traducción es-LATAM
echo ============================================
echo.

:: Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ejecutándose como administrador
) else (
    echo [ERROR] Este script debe ejecutarse como administrador
    pause
    exit /b 1
)

:: Detectar carpeta del juego
set "GAME_DIR="
if exist "C:\Program Files (x86)\Steam\steamapps\common\SIMULACRA\core.assets" set "GAME_DIR=C:\Program Files (x86)\Steam\steamapps\common\SIMULACRA"
if exist "C:\GOG Games\SIMULACRA\core.assets" set "GAME_DIR=C:\GOG Games\SIMULACRA"
if exist "C:\Program Files\SIMULACRA\core.assets" set "GAME_DIR=C:\Program Files\SIMULACRA"

if "%GAME_DIR%"=="" (
    echo [ERROR] No se encontró la carpeta del juego SIMULACRA
    echo.
    echo Especifica la ruta manualmente:
    set /p GAME_DIR="Ruta del juego: "
    if not exist "%GAME_DIR%\core.assets" (
        echo [ERROR] core.assets no encontrado en %GAME_DIR%
        pause
        exit /b 1
    )
)

echo [INFO] Juego encontrado en: %GAME_DIR%

:: Crear copias de seguridad
echo.
echo [INFO] Creando copias de seguridad...
if not exist "%GAME_DIR%\core.assets.bak" copy "%GAME_DIR%\core.assets" "%GAME_DIR%\core.assets.bak"
if exist "%GAME_DIR%\support.assets" if not exist "%GAME_DIR%\support.assets.bak" copy "%GAME_DIR%\support.assets" "%GAME_DIR%\support.assets.bak"
echo [OK] Copias de seguridad creadas

:: Aplicar archivos traducidos
echo.
echo [INFO] Aplicando traducción...
copy /Y "core.assets" "%GAME_DIR%\core.assets"
if exist "support.assets" copy /Y "support.assets" "%GAME_DIR%\support.assets"
echo [OK] Archivos traducidos aplicados

echo.
echo ============================================
echo  Parche aplicado correctamente
echo ============================================
echo.
echo Inicia el juego para ver los textos en español.
echo Para desinstalar, ejecuta desinstalar_parche.bat
echo.
pause
