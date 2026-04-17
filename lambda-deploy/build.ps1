# build.ps1 — Construye el ZIP de Lambda usando Amazon Linux (igual que el runtime de AWS)
# Ejecutar desde la raiz del proyecto: .\lambda-deploy\build.ps1
$ErrorActionPreference = "Stop"

$Root        = Split-Path $PSScriptRoot
$BackendPath = "$Root\backend"
$ZipPath     = "$PSScriptRoot\lambda-function.zip"
$ScriptPath  = "$PSScriptRoot\build_in_docker.sh"

# Script que corre dentro del contenedor Linux
@'
#!/bin/bash
set -e
pip install -r /src/requirements.txt -t /tmp/pkg --no-cache-dir -q
cp /src/app.py /src/config.py /tmp/pkg/
cd /tmp/pkg
python3 - <<'PYEOF'
import zipfile, os
with zipfile.ZipFile('/out/lambda-function.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if '__pycache__' not in d]
        for f in files:
            if not f.endswith('.pyc'):
                z.write(os.path.join(root, f))
print('ZIP creado correctamente')
PYEOF
'@ | Set-Content $ScriptPath -Encoding UTF8

Write-Host "Construyendo dentro de Amazon Linux 2023 (Python 3.14)..."
if (Test-Path $ZipPath) { Remove-Item $ZipPath }

docker run --rm `
  --entrypoint /bin/bash `
  -v "${BackendPath}:/src" `
  -v "${PSScriptRoot}:/out" `
  public.ecr.aws/lambda/python:3.14 `
  /out/build_in_docker.sh

$size = [math]::Round((Get-Item $ZipPath).Length / 1MB, 1)
Write-Host ""
Write-Host "Paquete listo: $ZipPath ($size MB)"
Write-Host "  Runtime: Python 3.14"
Write-Host "  Handler: app.handler"
