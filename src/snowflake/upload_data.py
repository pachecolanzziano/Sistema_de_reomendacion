# src/snowflake/upload_data.py
"""
Script para subir el CSV a Snowflake.
"""

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from pathlib import Path
from src.snowflake.config import get_snowflake_connection_params

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "src" / "data" / "DataSetLimpio.csv"
TABLE_NAME = "TRANSACCIONES"


def upload_csv_to_snowflake(force=False):
    """
    Lee el CSV y lo sube a Snowflake.
    
    Args:
        force (bool): Si True, sobrescribe la tabla aunque ya tenga datos.
    """
    # 1. Verificar que el CSV existe
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {CSV_PATH}")
    
    file_size_mb = CSV_PATH.stat().st_size / (1024 * 1024)
    print(f"📁 CSV encontrado: {CSV_PATH}")
    print(f"📏 Tamaño: {file_size_mb:.2f} MB")

    # 2. Conectar a Snowflake
    params = get_snowflake_connection_params()
    conn = snowflake.connector.connect(**params)
    print("🔌 Conectado a Snowflake.")

    # 3. Verificar si la tabla ya tiene datos
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM TRANSACCIONES")
    count = cursor.fetchone()[0]
    cursor.close()
    
    if count > 0 and not force:
        print(f"⚠️ La tabla ya contiene {count} registros.")
        print("   Para recargar, usa force=True en la función.")
        conn.close()
        return

    # 4. Leer el CSV
    print("📤 Leyendo CSV...")
    df = pd.read_csv(CSV_PATH)
    print(f"📊 Registros cargados: {len(df)}")

    # 5. Subir a Snowflake
    success, nrows, ncols = write_pandas(
        conn=conn,
        df=df,
        table_name=TABLE_NAME,
        database=params['database'],
        schema=params['schema'],
        quote_identifiers=False,
        overwrite=force or count == 0
    )

    if success:
        print(f"✅ ¡Carga completada!")
        print(f"📊 Filas subidas: {nrows}")
        print(f"📋 Columnas: {ncols}")
    else:
        print("❌ Error al subir los datos.")

    # 6. Cerrar conexión
    conn.close()
    print("🔌 Conexión cerrada.")


if __name__ == "__main__":
    upload_csv_to_snowflake(force=False)