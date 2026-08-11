# src/snowflake/load_data.py
"""
Script para leer datos desde Snowflake.
"""

import pandas as pd
import snowflake.connector
from src.snowflake.config import get_snowflake_connection_params


def load_data_from_snowflake(limit=None):
    """
    Lee los datos desde Snowflake y retorna un DataFrame.
    
    Args:
        limit (int, optional): Número de filas a leer. Si es None, lee todas.
    
    Returns:
        pd.DataFrame: Datos cargados
    """
    params = get_snowflake_connection_params()
    conn = snowflake.connector.connect(**params)
    print("🔌 Conectado a Snowflake.")

    # Construir la consulta
    query = "SELECT * FROM TRANSACCIONES"
    if limit:
        query = f"{query} LIMIT {limit}"

    print(f"📥 Ejecutando consulta: {query}")

    # Leer directamente a DataFrame
    df = pd.read_sql(query, conn)

    print(f"✅ Datos cargados: {len(df)} registros, {len(df.columns)} columnas")

    conn.close()
    print("🔌 Conexión cerrada.")

    return df


def load_data_sample(n_rows=1000):
    """Lee solo las primeras N filas de la tabla."""
    return load_data_from_snowflake(limit=n_rows)


if __name__ == "__main__":
    # Prueba rápida
    df = load_data_sample(1000)
    print("\n📊 Primeras filas:")
    print(df.head())
    print("\n📊 Información del DataFrame:")
    print(df.info())