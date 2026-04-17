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
