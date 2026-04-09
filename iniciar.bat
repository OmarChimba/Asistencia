@echo off
title Reporte de Asistencia
cd /d "%~dp0"

echo Preparando entorno...

:: ── Python venv (dentro de backend/) ───────────────────────
if not exist backend\venv (
    echo Creando entorno virtual Python...
    python -m venv backend\venv
)
echo Instalando dependencias Python...
backend\venv\Scripts\pip install -r backend\requirements.txt -q

:: ── Node modules ────────────────────────────────────────────
cd frontend
if not exist node_modules (
    echo Instalando dependencias Node.js...
    npm install
)
cd ..

:: ── Lanzar servidores ───────────────────────────────────────
echo Iniciando servidores...

start "Backend FastAPI - Puerto 8000" cmd /k "cd /d %~dp0 && backend\venv\Scripts\activate && uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000"
start "Frontend Vite React - Puerto 5173" cmd /k "cd /d %~dp0\frontend && npm run dev -- --host 0.0.0.0"

:: ── Abrir navegador ─────────────────────────────────────────
echo Esperando que los servidores inicien...
timeout /t 7 /nobreak > nul
start "" http://localhost:5173

echo.
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:5173
echo.
