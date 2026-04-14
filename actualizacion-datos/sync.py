"""
Sincroniza marcaciones desde la API interna hacia DynamoDB (tabla Marcaciones).
Clave: marcacion = {fecha}#{codigo}  (único por empleado por día)
"""
import os, sys, time, logging
import requests
import boto3
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv

load_dotenv()

# ── Configuración ──────────────────────────────────────────────
API_URL    = os.getenv('API_ASISTENCIA_URL')
AWS_KEY    = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
TABLE_NAME = os.getenv('DYNAMODB_TABLE', 'Marcaciones')
INTERVALO  = int(os.getenv('INTERVALO_MINUTOS', '15'))  # cada cuántos minutos sincroniza

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
log = logging.getLogger(__name__)


# ── AWS ────────────────────────────────────────────────────────
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
)
table = dynamodb.Table(TABLE_NAME)


def fetch_api() -> list[dict]:
    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def sync():
    log.info("Obteniendo datos de la API...")
    try:
        registros = fetch_api()
    except Exception as e:
        log.error(f"Error al llamar la API: {e}")
        return

    log.info(f"  {len(registros)} registros recibidos")

    insertados = 0
    errores    = 0

    # batch_writer hace grupos de 25 automáticamente (límite DynamoDB)
    with table.batch_writer() as batch:
        for r in registros:
            try:
                clave = f"{r['fecha']}#{r['codigo']}"
                item  = {
                    'marcacion':      clave,
                    'empresa':        r.get('empresa'),
                    'grupo':          r.get('grupo', ''),
                    'codigo':         r.get('codigo'),
                    'nombre':         r.get('nombre', ''),
                    'fecha':          r.get('fecha', ''),
                    'cedula':         r.get('cedula', ''),
                    'apellido_nombre':r.get('apellido_nombre', ''),
                    'ingreso':        r.get('ingreso') or '',
                    'salida':         r.get('salida')  or '',
                }
                batch.put_item(Item=item)
                insertados += 1
            except Exception as e:
                log.error(f"  Error en registro {r.get('codigo')}: {e}")
                errores += 1

    log.info(f"  Sincronizados: {insertados} | Errores: {errores}")


def main():
    log.info("=== Servicio de sincronización iniciado ===")
    log.info(f"API: {API_URL}")
    log.info(f"Tabla DynamoDB: {TABLE_NAME} ({AWS_REGION})")
    log.info(f"Intervalo: cada {INTERVALO} minutos")

    while True:
        sync()
        log.info(f"Próxima sync en {INTERVALO} minutos...")
        time.sleep(INTERVALO * 60)


if __name__ == '__main__':
    main()
