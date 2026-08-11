"""
Preprocesamiento para los modelos de recomendación (Item-Based CF / ALS).

Lee DataSetLimpio.csv, ordena por fecha y arma la matriz de interacción
cliente-item con un split temporal 80/20: el 20% de test corresponde
siempre a las compras más recientes del dataset (no es un split aleatorio).
"""

import os

import pandas as pd
from scipy.sparse import csr_matrix

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DataSetLimpio.csv")


def load_and_split(path=DEFAULT_CSV_PATH, test_size=0.2):
    # Country y Description quedan fuera del modelado a propósito:
    # Country porque >90% es "United Kingdom" (sesgaría el modelo sin aportar),
    # Description porque no es una variable de interacción cliente-item.
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    df = df.sort_values("InvoiceDate").reset_index(drop=True)

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


def get_train_test(path=DEFAULT_CSV_PATH, test_size=0.2):
    """Punto de entrada que usan los scripts de modelos (item_based_cf.py, etc.).

    Devuelve:
        train_matrix: matriz dispersa cliente x item (solo con datos de train)
        test_df: filas del 20% más reciente, con customer_code / item_code
        customer_map: código -> CustomerID original
        item_map: código -> StockCode original
        description_map: StockCode -> Description (solo para mostrar resultados)
    """
    train_df, test_df, customer_map, item_map, description_map, n_customers, n_items = (
        load_and_split(path, test_size)
    )
    train_matrix = build_interaction_matrix(train_df, n_customers, n_items)
    return train_matrix, test_df, customer_map, item_map, description_map
