"""
Prueba de conexión AWS — verifica credenciales y lista tablas DynamoDB.
Ejecutar: python test_aws.py
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

KEY    = os.getenv('AWS_ACCESS_KEY_ID')
SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')

if not KEY or not SECRET:
    print("ERROR: Faltan AWS_ACCESS_KEY_ID o AWS_SECRET_ACCESS_KEY en .env")
    exit(1)

print(f"Credenciales cargadas: {KEY[:8]}...")

# ── 1. Verificar identidad ──────────────────────────────────
print("\n[1] Verificando credenciales con STS...")
try:
    sts = boto3.client('sts', aws_access_key_id=KEY, aws_secret_access_key=SECRET)
    identity = sts.get_caller_identity()
    print(f"    Cuenta  : {identity['Account']}")
    print(f"    Usuario : {identity['Arn']}")
    print("    OK - Credenciales validas")
except (ClientError, NoCredentialsError) as e:
    print(f"    ERROR: {e}")
    exit(1)

# ── 2. Listar tablas DynamoDB por region ───────────────────
REGIONES = ['us-east-1', 'us-east-2', 'us-west-2', 'sa-east-1']

print("\n[2] Buscando tablas DynamoDB...")
for region in REGIONES:
    try:
        ddb = boto3.client(
            'dynamodb',
            region_name=region,
            aws_access_key_id=KEY,
            aws_secret_access_key=SECRET,
        )
        tablas = ddb.list_tables()['TableNames']
        if tablas:
            print(f"    Region {region}: {tablas}")
        else:
            print(f"    Region {region}: sin tablas")
    except ClientError as e:
        print(f"    Region {region}: {e.response['Error']['Message']}")
