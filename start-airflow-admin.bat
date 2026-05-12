@echo off
REM Script para iniciar Airflow en Windows
REM Este archivo debe ejecutarse como Administrador

setlocal enabledelayedexpansion

REM Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ❌ ERROR: Este archivo debe ejecutarse como ADMINISTRADOR
    echo.
    echo Pasos:
    echo  1. Click derecho en este archivo (.bat)
    echo  2. Selecciona "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Ejecutando como Administrador
echo.

REM Obtener la ruta donde está el script
cd /d "%~dp0"

REM Verificar que estamos en la raíz (debe existir carpeta docker)
if not exist "docker\" (
    echo ❌ ERROR: No se encuentra la carpeta docker/
    echo    Asegurate que el script está en la raíz del proyecto
    echo    Ruta actual: %cd%
    pause
    exit /b 1
)

cd docker

echo 🧹 Limpiando contenedores previos...
docker-compose -f docker-compose-airflow.yml down -v

timeout /t 3 /nobreak

echo.
echo 🚀 Levantando Airflow...
docker-compose -f docker-compose-airflow.yml up -d

echo.
echo ⏳ Esperando que Airflow esté listo (45 segundos)...
timeout /t 45 /nobreak

echo.
echo ✅ Verificando estado...
docker-compose -f docker-compose-airflow.yml ps

echo.
echo ==========================================
echo ✅ Airflow iniciado!
echo ==========================================
echo.
echo 🌐 Airflow UI: http://localhost:8080
echo    Usuario: airflow
echo    Contraseña: airflow
echo.
echo 📊 Flower: http://localhost:5555
echo.
echo ==========================================

start http://localhost:8080

pause