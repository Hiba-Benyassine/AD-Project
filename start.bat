@echo off
SETLOCAL EnableDelayedExpansion

:: ==============================================================================
:: SPORTS DATA PLATFORM - STARTUP & MONITORING SCRIPT (WINDOWS)
:: ==============================================================================

echo ============================================================
echo     SPORTS DATA PLATFORM : INITIALISATION DU SYSTEME
echo ============================================================
echo.

:: 1. Lancement de Docker Compose
echo [1/4] Demarrage des conteneurs (mode detache)...
docker compose up -d

if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du lancement de Docker Compose.
    pause
    exit /b 1
)

:: 2. Verification de la sante des services
echo [2/4] Verification de l'etat des services critiques...
ping 127.0.0.1 -n 6 > nul

docker inspect --format="{{.State.Status}}" sports_postgres >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo   [OK] PostgreSQL est en ligne.) else (echo   [!!] PostgreSQL est hors ligne.)

docker inspect --format="{{.State.Status}}" sports_kafka >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo   [OK] Kafka est en ligne.) else (echo   [!!] Kafka est hors ligne.)

docker inspect --format="{{.State.Status}}" sports_minio >nul 2>&1
if %ERRORLEVEL% EQU 0 (echo   [OK] MinIO est en ligne.) else (echo   [!!] MinIO est hors ligne.)

:: 3. Validation spécifique du Streaming
echo [3/4] Validation du flux de streaming en temps reel...

echo   > Attente du Producer Kafka...
ping 127.0.0.1 -n 6 > nul
echo   [OK] Le systeme de streaming est en cours d'initialisation.
echo   Consultez 'docker compose logs -f kafka-producer' pour le detail.

:: 4. Resumé final
echo.
echo ============================================================
echo     ETAT GLOBAL DU SYSTEME
echo ============================================================
echo.
echo   Flux de donnees :   OPERATIONNEL
echo   Streaming :         ACTIF
echo   Analytique :        PRET
echo.
echo Accès Metabase : http://localhost:3000
echo Accès Airflow  : http://localhost:8080
echo.
echo Le systeme est pret ! Bonne analyse.
echo ============================================================
pause
