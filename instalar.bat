@echo off
title Instalacion - Reporte de Asistencia
cd /d "%~dp0"

echo ============================================
echo   INSTALACION INICIAL
echo ============================================
echo.

:: ── Verificar Git ────────────────────────────────────────────
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no esta instalado. Descargalo en https://git-scm.com
    pause & exit /b 1
)

:: ── Verificar Python ─────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado. Descargalo en https://python.org
    pause & exit /b 1
)

:: ── Verificar Node.js ────────────────────────────────────────
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no esta instalado. Descargalo en https://nodejs.org
    pause & exit /b 1
)

:: ── Clonar repositorio ───────────────────────────────────────
if not exist backend (
    echo Clonando repositorio...
    git clone https://github.com/OmarChimba/Asistencia.git .
) else (
    echo Repositorio ya existe, actualizando...
    git pull origin main
)

:: ── Entorno virtual Python ───────────────────────────────────
if not exist backend\venv (
    echo Creando entorno virtual Python...
    python -m venv backend\venv
)
echo Instalando dependencias Python...
backend\venv\Scripts\pip install -r backend\requirements.txt -q

:: ── Node modules ─────────────────────────────────────────────
cd frontend
echo Instalando dependencias Node.js...
npm install
cd ..

echo.
echo ============================================
echo   Instalacion completada exitosamente
echo   Ahora ejecuta: iniciar.bat
echo ============================================
pause
