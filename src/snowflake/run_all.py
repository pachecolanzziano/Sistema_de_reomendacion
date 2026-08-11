# src/snowflake/run_all.py
"""
Orquestador del flujo de datos con Snowflake.
Ejecuta secuencialmente: creación de tabla → carga de datos → verificación.
"""

import time
import sys
from pathlib import Path

# Añadir la carpeta src al path para poder importar los módulos
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.snowflake.create_table import create_table_if_not_exists
from src.snowflake.upload_data import upload_csv_to_snowflake
from src.snowflake.load_data import load_data_sample


def run_all(force_reupload=False):
    """
    Ejecuta todo el flujo de datos secuencialmente.
    
    Args:
        force_reupload (bool): Si True, recarga los datos aunque la tabla ya exista.
    """
    print("="*60)
    print("🚀 INICIANDO FLUJO DE DATOS CON SNOWFLAKE")
    print("="*60)
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # PASO 1: Crear la tabla (si no existe)
    # ---------------------------------------------------------
    print("\n📌 PASO 1: Verificando/Creando tabla en Snowflake...")
    print("-"*40)
    
    create_table_if_not_exists()
    
    # ---------------------------------------------------------
    # PASO 2: Subir el CSV a Snowflake
    # ---------------------------------------------------------
    print("\n📌 PASO 2: Subiendo datos a Snowflake...")
    print("-"*40)
    
    upload_csv_to_snowflake(force=force_reupload)
    
    # ---------------------------------------------------------
    # PASO 3: Verificar que los datos llegaron
    # ---------------------------------------------------------
    print("\n📌 PASO 3: Verificando datos subidos...")
    print("-"*40)
    
    df = load_data_sample(5)
    print(f"\n✅ Verificación exitosa: {len(df)} filas de muestra cargadas.")
    print("\n📊 Muestra de datos:")
    print(df.head())
    
    # ---------------------------------------------------------
    # FINAL
    # ---------------------------------------------------------
    elapsed_time = time.time() - start_time
    print("\n" + "="*60)
    print(f"✅ FLUJO COMPLETADO EN {elapsed_time:.2f} segundos")
    print("="*60)
    
    return df


if __name__ == "__main__":
    # Ejecutar el flujo completo
    df = run_all(force_reupload=False)