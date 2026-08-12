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

import pandas as pd
from scipy.sparse import csr_matrix

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DataSetLimpio.csv")


def load_raw(path=DEFAULT_CSV_PATH):
    """Única lectura del csv. Parsea InvoiceDate y ordena por fecha una vez;
    get_train_test() y get_train_test_fpgrowth() parten de este mismo df."""
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    return df.sort_values("InvoiceDate").reset_index(drop=True)


# ============================================================
# POPULARIDAD / ITEM-BASED CF / ALS (por cliente)
# ============================================================

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


def get_train_test(path=DEFAULT_CSV_PATH, test_size=0.2, raw_df=None):
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


# ============================================================
# FP-GROWTH (por factura — necesita la canasta completa, no el
# agregado por cliente que usan los tres modelos de arriba)
# ============================================================

def get_train_test_fpgrowth(path=DEFAULT_CSV_PATH, test_size=0.2, raw_df=None):
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


if __name__ == "__main__":
    basket, test, desc = get_train_test_fpgrowth()
    print(f"¡Proceso exitoso! Total de transacciones de entrenamiento: {len(basket)}")
