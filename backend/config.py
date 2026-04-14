# ══════════════════════════════════════════════════════════════
#  Configuración del sistema  (valores leídos desde .env)
# ══════════════════════════════════════════════════════════════
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SECRET_KEY      = os.getenv('SECRET_KEY',      'nintanga-provefrut-2024-secretkey')
BACKEND_HOST    = os.getenv('BACKEND_HOST',    '0.0.0.0')
BACKEND_PORT    = int(os.getenv('BACKEND_PORT', '8000'))

# ── AWS DynamoDB ────────────────────────────────────────────
AWS_ACCESS_KEY_ID     = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION            = os.getenv('AWS_REGION',       'us-east-1')
DYNAMODB_TABLE        = os.getenv('DYNAMODB_TABLE',   'Marcaciones')

# ── Etiquetas legibles para los códigos de grupo ───────────
GRUPO_LABELS = {
    'COSE':  'Cosecha',
    'CHAN':  'Chantilin',
    'ALFON': 'San Alfonso',
    'SEBA':  'San Sebastián',
    'FELI':  'San Felipe',
}

# ── Usuarios del sistema ────────────────────────────────────
# grupos: palabras clave que se comparan (sin importar mayúsculas)
#         contra los campos "grupo" y "nombre" que devuelve la API.
# is_admin: True → ve todos los grupos con filtro, False → solo sus grupos.
USERS = {
    'luis.toctaguano@nintanga.com.ec': {
        'password': 'Nintanga2024',
        'nombre':   'Luis Toctaguano',
        'grupos':   ['COSE', 'CHAN'],
        'is_admin': False,
    },
    'nelson.garcia@nintanga.com.ec': {
        'password': 'Nintanga2024',
        'nombre':   'Nelson García',
        'grupos':   ['ALFON'],
        'is_admin': False,
    },
    'jhonatan.curicho@nintanga.com.ec': {
        'password': 'Nintanga2024',
        'nombre':   'Jhonatan Curicho',
        'grupos':   ['SEBA'],
        'is_admin': False,
    },
    'milton.quimbiamba@nintanga.com.ec': {
        'password': 'Nintanga2024',
        'nombre':   'Milton Quimbiamba',
        'grupos':   ['FELI'],
        'is_admin': False,
    },
    'pchimba@provefrut.com': {
        'password': 'Provefrut2024',
        'nombre':   'Omar Chimba',
        'grupos':   [],
        'is_admin': True,
    },
    'msangucho@provefrut.com': {
        'password': 'Provefrut2024',
        'nombre':   'Miguel Sangucho',
        'grupos':   [],
        'is_admin': True,
    },
}
