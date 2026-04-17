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

# ── CORS ─────────────────────────────────────────────────────
# En Lambda, setear ALLOWED_ORIGINS=https://tu-app.amplifyapp.com
ALLOWED_ORIGINS = [o.strip() for o in os.getenv('ALLOWED_ORIGINS', '').split(',') if o.strip()]

# ── Etiquetas legibles para los códigos de grupo ───────────
GRUPO_LABELS = {
    'COSE':  'Cosecha',
    'CHAN':  'Chantilin',
    'ALFON': 'San Alfonso',
    'SEBA':  'San Sebastián',
    'FELI':  'San Felipe',
    'GUAY':  'Guaytacama',
    'MEC':   'Mecánica',
    'TRAC':  'Servicio de Tractores',
    'ADM':   'Administración',
    'PIL':   'Pilones',
    'FLOR':  'Nintanga Flores',
    'POSTC': 'Postcosecha',
    'GENER': 'General',
    'BODE':  'Bodega',
    'BIO':   'Bionintanga',
    'COMP':  'Compostera',
    'CAB':   'Caballerizas',
    'BRIG':  'Brigada',
    'GUARD': 'Guardiania',
    'LIMPI': 'Limpieza',
    'SAN':   'San Isidro',
    'CAR':   'Santa Carmen',
    'PATR':  'San Patricio',
    'MONI':  'Monitoreo',
    'MOY':   'La Moya',
    'CRUZ':  'Santa Cruz',
    'TAMBO': 'Tambo Mulalo',
    'KOSH':  'Kosher',
    'SIE-F': 'Siembra Flores',
    'CUL-F': 'Cultivo Flores',
    'RIE-F': 'Riego Flores',
    'SEM-F': 'Semillero Flores',
    'PELET': 'Peletizadora',
    'SANB': 'San Blas',
    'SAGRI': 'Servicios Agricolas',
    'FUM-R': 'Riego Y Fumigaciones',
    'GANAD': 'Ganaderia Guaytacama',
    'FRAN': 'San Francisco',
    'ISIN': 'San Isinche',
}

# ── Usuarios del sistema ────────────────────────────────────
# grupos: palabras clave que se comparan (sin importar mayúsculas)
#         contra los campos "grupo" y "nombre" que devuelve la API.
# is_admin: True → ve todos los grupos con filtro, False → solo sus grupos.
USERS = {
    'luis.toctaguano@nintanga.com.ec': {
        'password': 'Cosecha-2026',
        'nombre':   'Luis Toctaguano',
        'grupos':   ['COSE', 'CHAN'],
        'is_admin': False,
    },
    'nelson.garcia@nintanga.com.ec': {
        'password': 'Salfonso-2026',
        'nombre':   'Nelson García',
        'grupos':   ['ALFON'],
        'is_admin': False,
    },
    'jhonatan.curicho@nintanga.com.ec': {
        'password': 'Ssebastian-2026',
        'nombre':   'Jhonatan Curicho',
        'grupos':   ['SEBA'],
        'is_admin': False,
    },
    'milton.quimbiamba@nintanga.com.ec': {
        'password': 'Sfelipe-2026',
        'nombre':   'Milton Quimbiamba',
        'grupos':   ['FELI'],
        'is_admin': False,
    },
    'gustavo.toscano@nintanga.com.ec': {
        'password': 'Guaytacama-2026',
        'nombre':   'Gustavo Toscano',
        'grupos':   ['GUAY'],
        'is_admin': False, 
    },
    'pchimba@provefrut.com': {
        'password': 'Peter-2026',
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