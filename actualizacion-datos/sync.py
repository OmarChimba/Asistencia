"""
Sincroniza marcaciones desde la API interna hacia DynamoDB.
- Clave: marcacion = str(codigo)  — un registro por empleado
- Solo mantiene registros de la fecha actual
- Limpia la tabla si detecta claves con formato incorrecto o fecha distinta
- Revisa cambios cada POLL_SEGUNDOS (default 30)
"""
import os, time, hashlib, json, logging
import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

API_URL    = os.getenv('API_ASISTENCIA_URL')
AWS_KEY    = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION',       'us-east-1')
TABLE_NAME = os.getenv('DYNAMODB_TABLE',   'Marcaciones')
POLL_SEG   = int(os.getenv('POLL_SEGUNDOS', '30'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)

dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
)
table = dynamodb.Table(TABLE_NAME)


# ── Helpers ────────────────────────────────────────────────────

def fetch_api() -> list[dict]:
    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def calcular_hash(registros: list[dict]) -> str:
    contenido = json.dumps(registros, sort_keys=True, default=str)
    return hashlib.md5(contenido.encode()).hexdigest()


def limpiar_tabla():
    """Elimina TODOS los registros de la tabla."""
    log.info("  Limpiando tabla...")
    eliminados = 0
    scan = table.scan(ProjectionExpression='marcacion')
    while True:
        with table.batch_writer() as batch:
            for item in scan['Items']:
                batch.delete_item(Key={'marcacion': item['marcacion']})
                eliminados += 1
        if 'LastEvaluatedKey' not in scan:
            break
        scan = table.scan(
            ProjectionExpression='marcacion',
            ExclusiveStartKey=scan['LastEvaluatedKey'],
        )
    log.info(f"  Eliminados: {eliminados} registros")


def tabla_necesita_limpieza(fecha_hoy: str) -> bool:
    """
    Retorna True si la tabla tiene:
    - Registros de otra fecha
    - Claves con formato incorrecto (contienen '_' o '#')
    """
    scan = table.scan(
        ProjectionExpression='marcacion, fecha',
        Limit=50,
    )
    items = scan.get('Items', [])
    if not items:
        return False
    for item in items:
        clave = str(item.get('marcacion', ''))
        fecha = str(item.get('fecha', ''))
        # Formato incorrecto: tiene _ o # (formatos viejos)
        if '_' in clave or '#' in clave:
            log.warning(f"  Clave con formato incorrecto: {clave}")
            return True
        # Fecha distinta a hoy
        if fecha and fecha != fecha_hoy:
            log.info(f"  Fecha en tabla ({fecha}) distinta a hoy ({fecha_hoy})")
            return True
    return False


def escribir_registros(registros: list[dict]):
    insertados = 0
    errores    = 0
    with table.batch_writer() as batch:
        for r in registros:
            codigo = r.get('codigo')
            try:
                batch.put_item(Item={
                    'marcacion':       str(codigo),
                    'empresa':         r.get('empresa'),
                    'grupo':           r.get('grupo',           ''),
                    'codigo':          codigo,
                    'nombre':          r.get('nombre',          ''),
                    'fecha':           r.get('fecha',           ''),
                    'cedula':          r.get('cedula',          ''),
                    'apellido_nombre': r.get('apellido_nombre', ''),
                    'ingreso':         r.get('ingreso') or '',
                    'salida':          r.get('salida')  or '',
                })
                insertados += 1
            except Exception as e:
                log.error(f"  Error en {codigo}: {e}")
                errores += 1
    log.info(f"  Escritos/actualizados: {insertados} | Errores: {errores}")


# ── Ciclo principal ────────────────────────────────────────────

def main():
    log.info("══════════════════════════════════════════")
    log.info("  Servicio de sincronización de marcaciones")
    log.info(f"  API     : {API_URL}")
    log.info(f"  Tabla   : {TABLE_NAME} ({AWS_REGION})")
    log.info(f"  Revisión: cada {POLL_SEG} segundos")
    log.info("══════════════════════════════════════════")

    hash_anterior = None

    while True:
        try:
            registros = fetch_api()

            if not registros:
                log.warning("API devolvió 0 registros.")
                time.sleep(POLL_SEG)
                continue

            fecha_hoy   = registros[0].get('fecha', '')
            hash_actual = calcular_hash(registros)

            # Verificar si la tabla necesita limpieza (formato incorrecto o fecha vieja)
            if tabla_necesita_limpieza(fecha_hoy):
                log.info("Limpieza necesaria → borrando tabla y recargando")
                limpiar_tabla()
                hash_anterior = None   # forzar escritura

            if hash_actual == hash_anterior:
                time.sleep(POLL_SEG)
                continue

            log.info(f"Cambios detectados — {len(registros)} registros | fecha: {fecha_hoy}")
            escribir_registros(registros)
            hash_anterior = hash_actual

        except requests.exceptions.RequestException as e:
            log.error(f"Error de conexión con la API: {e}")
        except Exception as e:
            log.error(f"Error inesperado: {e}")

        time.sleep(POLL_SEG)


if __name__ == '__main__':
    main()
