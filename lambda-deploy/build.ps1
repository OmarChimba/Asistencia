# build.ps1 — Construye el ZIP de Lambda usando Amazon Linux (igual que el runtime de AWS)
# Ejecutar desde la raiz del proyecto: .\lambda-deploy\build.ps1
$ErrorActionPreference = "Stop"

$Root       = Split-Path $PSScriptRoot
$BackendPath = "$Root\backend"
$PackageDir  = "$PSScriptRoot\package"
$ZipPath     = "$PSScriptRoot\lambda-function.zip"

Write-Host "Limpiando paquete anterior..."
if (Test-Path $PackageDir) { Remove-Item $PackageDir -Recurse -Force }
New-Item -ItemType Directory -Path $PackageDir | Out-Null

Write-Host "Instalando dependencias con Amazon Linux 2023 (Python 3.12)..."
docker run --rm `
  --entrypoint pip `
  -v "${BackendPath}:/src" `
  -v "${PackageDir}:/out" `
  public.ecr.aws/lambda/python:3.12 `
  install -r /src/requirements.txt -t /out --no-cache-dir

Write-Host "Copiando codigo fuente..."
Copy-Item "$BackendPath\app.py"    "$PackageDir\"
Copy-Item "$BackendPath\config.py" "$PackageDir\"

Write-Host "Creando ZIP..."
if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Compress-Archive -Path "$PackageDir\*" -DestinationPath $ZipPath

$size = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "Paquete listo: $ZipPath ($size MB)"
Write-Host "  Runtime: Python 3.12"
Write-Host "  Handler: app.handler"
