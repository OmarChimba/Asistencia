# ══════════════════════════════════════════════════════════════
#  Stage 1 — Build frontend React
# ══════════════════════════════════════════════════════════════
FROM node:20-slim AS frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build


# ══════════════════════════════════════════════════════════════
#  Stage 2 — Imagen de producción: nginx + FastAPI
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
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html

# ── Configuraciones ───────────────────────────────────────────
COPY Asistencia-app/nginx.conf        /etc/nginx/nginx.conf
COPY Asistencia-app/supervisord.conf  /etc/supervisor/conf.d/app.conf

EXPOSE 80

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
