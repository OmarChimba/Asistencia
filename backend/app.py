import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import requests as http_client

from config import API_ASISTENCIA_URL, SECRET_KEY, USERS, GRUPO_LABELS

app = FastAPI(title="Reporte de Asistencia")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(5173|4173|5174|5175)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALGORITHM            = "HS256"
TOKEN_EXPIRE_HOURS   = 10
security             = HTTPBearer()


# ── JWT ──────────────────────────────────────────────────────

def create_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    email = verify_token(credentials.credentials)
    if not email or email not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    return {**USERS[email], "email": email}


# ── Helpers ──────────────────────────────────────────────────

def get_tab(record: dict, keywords: list[str]) -> str | None:
    """Devuelve el keyword que corresponde al registro usando el código exacto de grupo."""
    grupo = record.get("grupo", "").strip().upper()
    for kw in keywords:
        if kw.strip().upper() == grupo:
            return kw
    return None

def fetch_asistencia() -> list[dict]:
    resp = http_client.get(API_ASISTENCIA_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ── Modelos ──────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


# ── Endpoints ────────────────────────────────────────────────

@app.post("/api/login")
def login(body: LoginRequest):
    email = body.email.strip().lower()
    user  = USERS.get(email)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {
        "token":        create_token(email),
        "nombre":       user["nombre"],
        "is_admin":     user["is_admin"],
        "grupos":       user["grupos"],
        "grupoLabels":  GRUPO_LABELS,
    }

@app.get("/api/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "nombre":       current_user["nombre"],
        "is_admin":     current_user["is_admin"],
        "grupos":       current_user["grupos"],
        "grupoLabels":  GRUPO_LABELS,
    }

@app.get("/api/asistencia")
def asistencia(current_user: dict = Depends(get_current_user)):
    try:
        data = fetch_asistencia()
    except http_client.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="No se puede conectar con el servidor de asistencia.")
    except http_client.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="La API de asistencia no respondió a tiempo.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if current_user["is_admin"]:
        return data

    grupos = current_user["grupos"]
    result = []
    for r in data:
        tab = get_tab(r, grupos)
        if tab:
            result.append({**r, "_tab": tab})
    return result


@app.get("/api/debug/mi-data")
def debug_mi_data(current_user: dict = Depends(get_current_user)):
    """Muestra los primeros 5 registros crudos de la API con el _tab asignado."""
    try:
        data = fetch_asistencia()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    grupos = current_user["grupos"]
    sample = []
    for r in data[:30]:
        tab = get_tab(r, grupos) if not current_user["is_admin"] else "admin"
        sample.append({
            "grupo":  r.get("grupo"),
            "nombre": r.get("nombre"),
            "_tab":   tab,
        })
    return {"grupos_usuario": grupos, "muestra": sample}


@app.get("/api/debug/grupos")
def debug_grupos(current_user: dict = Depends(get_current_user)):
    """Solo admin: muestra todos los valores únicos de 'grupo' y 'nombre' con su conteo."""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores")
    try:
        data = fetch_asistencia()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    from collections import Counter
    grupos_count  = Counter(r.get("grupo",  "") for r in data)
    nombres_count = Counter(r.get("nombre", "") for r in data)
    return {
        "total_registros": len(data),
        "por_grupo":  dict(sorted(grupos_count.items())),
        "por_nombre": dict(sorted(nombres_count.items())),
    }


# ── Entry point ──────────────────────────────────────────────

