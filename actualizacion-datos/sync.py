"""
Sincroniza marcaciones desde la API interna hacia DynamoDB.
Clave: marcacion = {codigo}_{n}  (n = orden secuencial en el response)
Limpieza: si la fecha del API es distinta a la almacenada → borra todo y recarga
"""
import os, time, logging
from collections import defaultdict
from datetime import datetime
import requests
import boto3
from boto3.dynamodb.conditions import Attr
from dotenv import load_dotenv

load_dotenv()

# ── Configuración ──────────────────────────────────────────────
API_URL    = os.getenv('API_ASISTENCIA_URL')
AWS_KEY    = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME = os.getenv('DYNAMODB_TABLE', 'Marcaciones')
INTERVALO  = int(os.getenv('INTERVALO_MINUTOS', '15'))

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


def fecha_en_tabla() -> str | None:
    """Devuelve la fecha del primer registro en la tabla, o None si está vacía."""
    resp = table.scan(Limit=1, ProjectionExpression='fecha')
    items = resp.get('Items', [])
    return items[0]['fecha'] if items else None


def limpiar_tabla():
    """Elimina todos los registros de la tabla en lotes de 25."""
    log.info("Limpiando tabla...")
    eliminados = 0
    scan = table.scan(ProjectionExpression='marcacion')
    while True:
        items = scan.get('Items', [])
        with table.batch_writer() as batch:
            for item in items:
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
    Escribe registros en DynamoDB.
    Clave: {codigo}_{n} donde n es el orden de aparición por codigo.
    """
    contador = defaultdict(int)   # cuántas veces aparece cada codigo
    insertados = 0
    errores    = 0

    with table.batch_writer() as batch:
        for r in registros:
            codigo = r.get('codigo')
            contador[codigo] += 1
            n = contador[codigo]
            marcacion = f"{codigo}_{n}"

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

    log.info(f"  Escritos: {insertados} | Errores: {errores}")


# ── Ciclo principal ────────────────────────────────────────────

def sync():
    log.info("─── Iniciando sincronización ───")

    try:
        registros = fetch_api()
    except Exception as e:
        log.error(f"Error al llamar la API: {e}")
        return

    if not registros:
        log.warning("La API devolvió 0 registros.")
        return

    fecha_api   = registros[0].get('fecha', '')
    fecha_tabla = fecha_en_tabla()

    log.info(f"Fecha API: {fecha_api} | Fecha en tabla: {fecha_tabla or 'vacía'}")

    # Si cambió la fecha → limpiar y recargar (datos de nuevo día)
    if fecha_tabla and fecha_tabla != fecha_api:
        log.info("Fecha cambió → limpiando tabla antes de escribir")
        limpiar_tabla()

    log.info(f"Escribiendo {len(registros)} registros...")
    escribir_registros(registros)


def main():
    log.info("══════════════════════════════════════════")
    log.info("  Servicio de sincronización de marcaciones")
    log.info(f"  API     : {API_URL}")
    log.info(f"  Tabla   : {TABLE_NAME} ({AWS_REGION})")
    log.info(f"  Intervalo: cada {INTERVALO} minutos")
    log.info("══════════════════════════════════════════")

    while True:
        sync()
        log.info(f"Próxima sync en {INTERVALO} minutos...")
        time.sleep(INTERVALO * 60)


if __name__ == '__main__':
    main()
