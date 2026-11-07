@echo off
:: Script de desinstalación - Traducción SIMULACRA al español latinoamericano
:: Ejecutar como administrador

echo ============================================
echo  SIMULACRA - Desinstalador de parche es-LATAM
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
)

echo [INFO] Juego encontrado en: %GAME_DIR%

:: Restaurar archivos originales
echo.
echo [INFO] Restaurando archivos originales...
if exist "%GAME_DIR%\core.assets.bak" (
    copy /Y "%GAME_DIR%\core.assets.bak" "%GAME_DIR%\core.assets"
    echo [OK] core.assets restaurado
) else (
    echo [WARN] core.assets.bak no encontrado
)

if exist "%GAME_DIR%\support.assets.bak" (
    copy /Y "%GAME_DIR%\support.assets.bak" "%GAME_DIR%\support.assets"
    echo [OK] support.assets restaurado
) else (
    echo [WARN] support.assets.bak no encontrado
)

echo.
echo ============================================
echo  Parche desinstalado correctamente
echo ============================================
echo.
echo El juego ha vuelto al idioma original (inglés).
echo.
pause
