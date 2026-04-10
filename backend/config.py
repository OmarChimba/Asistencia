# ══════════════════════════════════════════════════════════════
#  Configuración del sistema
# ══════════════════════════════════════════════════════════════

# URL de la API de asistencia
API_ASISTENCIA_URL = 'http://172.20.4.69:8000/api/cargar-asistencia/'

# Clave secreta para las sesiones (cámbiala en producción)
SECRET_KEY = 'nintanga-provefrut-2024-secretkey'

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
