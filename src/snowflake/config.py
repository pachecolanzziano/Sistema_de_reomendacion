# src/snowflake/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

def get_snowflake_connection_params():
    """Retorna un diccionario con los parámetros de conexión a Snowflake."""
    params = {
        'account': os.getenv('SNOWFLAKE_ACCOUNT'),
        'user': os.getenv('SNOWFLAKE_USER'),
        'password': os.getenv('SNOWFLAKE_PASSWORD'),
        'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
        'database': os.getenv('SNOWFLAKE_DATABASE'),
        'schema': os.getenv('SNOWFLAKE_SCHEMA')
    }
    
    missing = [k for k, v in params.items() if v is None]
    if missing:
        raise ValueError(f"Faltan variables en .env: {', '.join(missing)}")
    
    return params