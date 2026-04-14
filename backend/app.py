import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from jose import jwt, JWTError
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from config import SECRET_KEY, USERS, GRUPO_LABELS, \
                   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, DYNAMODB_TABLE

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

_dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
_table = _dynamodb.Table(DYNAMODB_TABLE)


def fetch_asistencia() -> list[dict]:
    """Lee todos los registros de DynamoDB y normaliza tipos."""
    items  = []
    scan   = _table.scan()
    while True:
        for item in scan.get('Items', []):
            items.append({
                'empresa':         int(item.get('empresa') or 0),
                'grupo':           str(item.get('grupo',           '')),
                'codigo':          int(item.get('codigo') or 0),
                'nombre':          str(item.get('nombre',          '')),
                'fecha':           str(item.get('fecha',           '')),
                'cedula':          str(item.get('cedula',          '')),
                'apellido_nombre': str(item.get('apellido_nombre', '')),
                'ingreso':         str(item.get('ingreso') or ''),
                'salida':          str(item.get('salida')  or '') or None,
            })
        if 'LastEvaluatedKey' not in scan:
            break
        scan = _table.scan(ExclusiveStartKey=scan['LastEvaluatedKey'])
    return items


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
    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"Error DynamoDB: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        raise HTTPException(status_code=502, detail=f"Error AWS: {str(e)}")
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


@app.get("/api/debug/grupos")
def debug_grupos(current_user: dict = Depends(get_current_user)):
    """Solo admin: muestra conteo de registros por grupo."""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="Solo administradores")
    try:
        data = fetch_asistencia()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    from collections import Counter
    return {
        "total_registros": len(data),
        "por_grupo": dict(sorted(Counter(r.get("grupo", "") for r in data).items())),
    }


# ── Entry ----------- point ──────────────────────────────────────────────

