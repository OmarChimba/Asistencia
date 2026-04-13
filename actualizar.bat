@echo off
title Actualizando - Reporte de Asistencia
cd /d "%~dp0"

echo ============================================
echo   ACTUALIZANDO DESDE GITHUB
echo ============================================
echo.

:: ── Bajar cambios ────────────────────────────────────────────
echo Descargando actualizaciones...
git pull origin main
if errorlevel 1 (
    echo ERROR: No se pudo actualizar desde GitHub.
    pause & exit /b 1
)

:: ── Actualizar dependencias Python si cambiaron ──────────────
echo Actualizando dependencias Python...
backend\venv\Scripts\pip install -r backend\requirements.txt -q

:: ── Actualizar dependencias Node si cambiaron ────────────────
cd frontend
echo Actualizando dependencias Node.js...
npm install --silent
cd ..

:: ── Cerrar servidores anteriores ─────────────────────────────
echo Cerrando servidores anteriores...
taskkill /FI "WINDOWTITLE eq Backend FastAPI*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Frontend Vite*" /F >nul 2>&1
timeout /t 2 /nobreak >nul

:: ── Lanzar servidores actualizados ───────────────────────────
echo Iniciando servidores...
start "Backend FastAPI - Puerto 8000" cmd /k "cd /d %~dp0 && backend\venv\Scripts\activate && uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000"
start "Frontend Vite React - Puerto 5173" cmd /k "cd /d %~dp0\frontend && npm run dev"

timeout /t 7 /nobreak >nul
start "" http://localhost:5173

echo.
echo ============================================
echo   Actualizacion completada
echo   Backend  : http://localhost:8000
echo   Frontend : http://localhost:5173
echo ============================================
