# ══════════════════════════════════════════════════════════════
#  Imagen de producción: nginx + FastAPI
#  El frontend se compila ANTES en el host (cd frontend && npm run build)
#  porque npm no puede descargar paquetes dentro de Docker en esta red
#  (proxy con certificado autofirmado). Se copia frontend/dist.
# ══════════════════════════════════════════════════════════════
FROM python:3.12-slim

# Instalar nginx y supervisor
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── Backend ───────────────────────────────────────────────────
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# ── Frontend (archivos estáticos del build) ───────────────────
COPY frontend/dist /usr/share/nginx/html

# ── Configuraciones ───────────────────────────────────────────
COPY Asistencia-app/nginx.conf        /etc/nginx/nginx.conf
COPY Asistencia-app/supervisord.conf  /etc/supervisor/conf.d/app.conf

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
