# src/snowflake/create_table.py
"""
Script para crear la tabla en Snowflake si no existe.
"""

import snowflake.connector
from src.snowflake.config import get_snowflake_connection_params


def create_table_if_not_exists():
    """
    Crea la tabla TRANSACCIONES en Snowflake si no existe.
    """
    params = get_snowflake_connection_params()
    conn = snowflake.connector.connect(**params)
    cursor = conn.cursor()
    
    print("🔌 Conectado a Snowflake.")
    
    # SQL para crear la tabla
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS TRANSACCIONES (
        Invoice STRING,
        StockCode STRING,
        Description STRING,
        Quantity INTEGER,
        InvoiceDate TIMESTAMP,
        Price FLOAT,
        CustomerID STRING,
        Country STRING
    )
    """
    
    cursor.execute(create_table_sql)
    print("✅ Tabla TRANSACCIONES verificada/creada.")
    
    cursor.close()
    conn.close()
    print("🔌 Conexión cerrada.")


if __name__ == "__main__":
    create_table_if_not_exists()