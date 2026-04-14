"""
Sincroniza marcaciones desde la API interna hacia DynamoDB.
- Revisa la API cada POLL_SEGUNDOS (default 30)
- Solo sincroniza si hay registros nuevos o actualizados
- Clave: marcacion = {codigo}_{n}
- Al cambiar de fecha: limpia la tabla y recarga
"""
import os, time, hashlib, json, logging
import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

# ── Configuración ──────────────────────────────────────────────
API_URL      = os.getenv('API_ASISTENCIA_URL')
AWS_KEY      = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET   = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION   = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME   = os.getenv('DYNAMODB_TABLE', 'Marcaciones')
POLL_SEG     = int(os.getenv('POLL_SEGUNDOS', '30'))

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
    """Hash del contenido completo para detectar cualquier cambio."""
    contenido = json.dumps(registros, sort_keys=True, default=str)
    return hashlib.md5(contenido.encode()).hexdigest()


def fecha_en_tabla() -> str | None:
    resp = table.scan(Limit=1, ProjectionExpression='fecha')
    items = resp.get('Items', [])
    return items[0]['fecha'] if items else None


def limpiar_tabla():
    log.info("  Limpiando tabla (fecha nueva)...")
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


def escribir_registros(registros: list[dict]):
    """
    Clave: marcacion = str(codigo)
    Si ya existe un registro con el mismo codigo → lo sobreescribe (upsert).
    """
    insertados = 0
    errores    = 0
    with table.batch_writer() as batch:
        for r in registros:
            codigo    = r.get('codigo')
            marcacion = str(codigo)          # clave única por empleado
            try:
                batch.put_item(Item={
                    'marcacion':       marcacion,
                    'empresa':         r.get('empresa'),
                    'grupo':           r.get('grupo', ''),
                    'codigo':          codigo,
                    'nombre':          r.get('nombre', ''),
                    'fecha':           r.get('fecha', ''),
                    'cedula':          r.get('cedula', ''),
                    'apellido_nombre': r.get('apellido_nombre', ''),
                    'ingreso':         r.get('ingreso') or '',
                    'salida':          r.get('salida')  or '',
                })
                insertados += 1
            except Exception as e:
                log.error(f"  Error en {marcacion}: {e}")
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

            hash_actual = calcular_hash(registros)

            if hash_actual == hash_anterior:
                log.debug("Sin cambios, esperando...")
                time.sleep(POLL_SEG)
                continue

            # Hay cambios — sincronizar
            fecha_api   = registros[0].get('fecha', '')
            fecha_tabla = fecha_en_tabla()

            log.info(f"Cambios detectados — {len(registros)} registros | fecha: {fecha_api}")

            if fecha_tabla and fecha_tabla != fecha_api:
                limpiar_tabla()

            escribir_registros(registros)
            hash_anterior = hash_actual

        except requests.exceptions.RequestException as e:
            log.error(f"Error de conexión con la API: {e}")
        except Exception as e:
            log.error(f"Error inesperado: {e}")

        time.sleep(POLL_SEG)


if __name__ == '__main__':
    main()
