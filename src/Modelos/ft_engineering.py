"""
Preprocesamiento para los modelos de recomendación.

El csv se lee UNA sola vez (load_raw) y desde ahí se derivan los dos formatos
que necesitan los modelos:
  - Popularidad, Item-Based CF y ALS -> get_train_test()        (por cliente)
  - FP-Growth                        -> get_train_test_fpgrowth() (por factura)

Ambas funciones aceptan un raw_df ya cargado (para no releer el csv cuando se
necesitan los dos formatos en la misma corrida, como en Modelos_juntos.py) o,
si no se les pasa nada, lo cargan ellas mismas para poder usarse solas.

El split es temporal 80/20 en los dos casos: el 20% de test corresponde
siempre a las compras/facturas más recientes (no es un split aleatorio).
"""

import os
import sys
from pathlib import Path

import pandas as pd
from scipy.sparse import csr_matrix

# ============================================================
# IMPORTAR MÓDULO DE SNOWFLAKE
# ============================================================

# Agregar la carpeta src al path para poder importar desde snowflake
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.snowflake.load_data import load_data_from_snowflake, load_data_sample


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Ya no necesitamos DEFAULT_CSV_PATH porque usamos Snowflake.
# Pero lo mantenemos por compatibilidad si algún otro módulo lo usa.
DEFAULT_CSV_PATH = None  # Ya no se usa para carga, solo para referencia


# ============================================================
# FUNCIÓN PRINCIPAL DE CARGA (MODIFICADA)
# ============================================================

# src/modelos/ft_engineering.py - PARTE MODIFICADA

def load_raw(path=None):
    """
    Carga los datos desde Snowflake (en lugar de un archivo CSV local).
    Parsea InvoiceDate y ordena por fecha una vez.
    get_train_test() y get_train_test_fpgrowth() parten de este mismo df.

    Args:
        path (str, optional): Se ignora. Se mantiene por compatibilidad.

    Returns:
        pd.DataFrame: DataFrame con los datos ordenados por fecha.
    """
    print("📥 Cargando datos desde Snowflake...")
    
    # Cargar datos desde Snowflake
    df = load_data_from_snowflake()
    
    print(f"✅ Datos cargados: {len(df):,} registros, {len(df.columns)} columnas")
        
    # ============================================================
    # NORMALIZAR NOMBRES DE COLUMNAS (MAYÚSCULAS → Capitalizadas)
    # ============================================================
    # Snowflake devuelve las columnas en mayúsculas, pero el código
    # espera nombres específicos (ej: 'InvoiceDate' en lugar de 'INVOICEDATE')
    
    # Mapeo de nombres de columnas (mayúsculas → formato esperado)
    column_mapping = {
        'INVOICE': 'Invoice',
        'STOCKCODE': 'StockCode',
        'DESCRIPTION': 'Description',
        'QUANTITY': 'Quantity',
        'INVOICEDATE': 'InvoiceDate',
        'PRICE': 'Price',
        'CUSTOMERID': 'CustomerID',
        'COUNTRY': 'Country'
    }
    
    # Renombrar solo las columnas que existen
    existing_columns = {col: column_mapping.get(col) for col in df.columns if col in column_mapping}
    df = df.rename(columns=existing_columns)
    
    
    # Asegurar que InvoiceDate sea datetime
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Ordenar por fecha
    df = df.sort_values("InvoiceDate").reset_index(drop=True)
    
    print("📊 Datos ordenados por fecha.")
    
    return df


# ============================================================
# FUNCIÓN PARA CARGAR UNA MUESTRA (NUEVA, PARA PRUEBAS)
# ============================================================

def load_raw_sample(n_rows=1000):
    """
    Carga solo una muestra de los datos desde Snowflake.
    Útil para pruebas rápidas.

    Args:
        n_rows (int): Número de filas a cargar.

    Returns:
        pd.DataFrame: Muestra de datos ordenados por fecha.
    """
    print(f"📥 Cargando muestra de {n_rows} registros desde Snowflake...")
    
    df = load_data_sample(n_rows)
    
    if 'InvoiceDate' in df.columns:
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    df = df.sort_values("InvoiceDate").reset_index(drop=True)
    
    print(f"✅ Muestra cargada: {len(df)} registros")
    
    return df


# ============================================================
# EL RESTO DEL CÓDIGO PERMANECE IGUAL
# ============================================================

# load_and_split() - SIN CAMBIOS
def load_and_split(raw_df, test_size=0.2):
    # Country y Description quedan fuera del modelado a propósito:
    # Country porque >90% es "United Kingdom" (sesgaría el modelo sin aportar),
    # Description porque no es una variable de interacción cliente-item.
    df = raw_df.dropna(subset=["CustomerID"]).reset_index(drop=True)
    df["CustomerID"] = df["CustomerID"].astype(int)

    df["customer_code"] = df["CustomerID"].astype("category").cat.codes
    df["item_code"] = df["StockCode"].astype("category").cat.codes

    customer_map = dict(enumerate(df["CustomerID"].astype("category").cat.categories))
    item_map = dict(enumerate(df["StockCode"].astype("category").cat.categories))

    # Solo para traducir StockCode -> nombre legible en las recomendaciones finales;
    # no se usa en el entrenamiento del modelo.
    description_map = (
        df.dropna(subset=["Description"])
        .drop_duplicates(subset=["StockCode"])
        .set_index("StockCode")["Description"]
        .to_dict()
    )

    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    n_customers = df["customer_code"].nunique()
    n_items = df["item_code"].nunique()

    return train_df, test_df, customer_map, item_map, description_map, n_customers, n_items


# build_interaction_matrix() - SIN CAMBIOS
def build_interaction_matrix(df, n_customers, n_items):
    grouped = (
        df.groupby(["customer_code", "item_code"], observed=True)["Quantity"]
        .sum()
        .reset_index()
    )
    return csr_matrix(
        (grouped["Quantity"], (grouped["customer_code"], grouped["item_code"])),
        shape=(n_customers, n_items),
    )


# get_train_test() - SIN CAMBIOS (solo usa load_raw internamente)
def get_train_test(path=None, test_size=0.2, raw_df=None):
    """Punto de entrada que usan Popularidad, Item-Based CF y ALS.

    raw_df: opcional. Si ya se cargó el csv con load_raw() (por ejemplo porque
    también se va a llamar get_train_test_fpgrowth() en la misma corrida), se
    pasa aquí para no releerlo. Si se deja en None, esta función lo carga sola.

    Devuelve:
        train_matrix: matriz dispersa cliente x item (solo con datos de train)
        test_df: filas del 20% más reciente, con customer_code / item_code
        customer_map: código -> CustomerID original
        item_map: código -> StockCode original
        description_map: StockCode -> Description (solo para mostrar resultados)
    """
    if raw_df is None:
        raw_df = load_raw(path)

    train_df, test_df, customer_map, item_map, description_map, n_customers, n_items = (
        load_and_split(raw_df, test_size)
    )
    train_matrix = build_interaction_matrix(train_df, n_customers, n_items)
    return train_matrix, test_df, customer_map, item_map, description_map


# get_train_test_fpgrowth() - SIN CAMBIOS
def get_train_test_fpgrowth(path=None, test_size=0.2, raw_df=None):
    """Punto de entrada que usa FP-Growth.

    raw_df: mismo propósito que en get_train_test() — reutilizar el csv ya
    cargado en vez de releerlo cuando ambos flujos corren juntos.
    """
    if raw_df is None:
        raw_df = load_raw(path)

    df = raw_df.dropna(subset=["Invoice", "StockCode"]).reset_index(drop=True)

    description_map = (
        df.drop_duplicates(subset=["StockCode"]).set_index("StockCode")["Description"].to_dict()
    )

    split_idx = int(len(df) * (1 - test_size))
    train_df = df.iloc[:split_idx].copy()
    test_df = df.iloc[split_idx:].copy()

    train_basket_list = train_df.groupby("Invoice")["StockCode"].apply(list).tolist()

    return train_basket_list, test_df, description_map


# ============================================================
# PRUEBA RÁPIDA (MODIFICADA PARA PROBAR SNOWFLAKE)
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("🧪 PRUEBA DE CARGA DESDE SNOWFLAKE")
    print("="*60)
    
    # Probar carga completa
    print("\n📥 Cargando datos completos...")
    df = load_raw()
    print(f"✅ Datos cargados: {len(df):,} registros")
    print(f"📊 Columnas: {df.columns.tolist()}")
    print(f"📊 Rango de fechas: {df['InvoiceDate'].min()} a {df['InvoiceDate'].max()}")
    
    # Probar una función que usa load_raw
    print("\n" + "="*60)
    print("🧪 PRUEBA DE get_train_test()")
    print("="*60)
    
    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()
    
    print(f"✅ Matriz de entrenamiento: {train_matrix.shape}")
    print(f"✅ Test: {len(test_df)} registros")
    print(f"✅ Clientes: {len(customer_map)}")
    print(f"✅ Productos: {len(item_map)}")
    
    # Probar FP-Growth
    print("\n" + "="*60)
    print("🧪 PRUEBA DE get_train_test_fpgrowth()")
    print("="*60)
    
    basket, test_df, desc = get_train_test_fpgrowth()
    print(f"✅ Canastas de entrenamiento: {len(basket)}")
    print(f"✅ Test: {len(test_df)} registros")
    
    print("\n✅ ¡Todas las pruebas completadas con éxito!")