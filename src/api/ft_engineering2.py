"""
Preprocesamiento + entrenamiento para la API de recomendaciones.

Fuente de datos: Snowflake (tabla TRANSACCIONES), vía src.snowflake.load_data.
Snowflake devuelve los nombres de columna en MAYÚSCULAS (identificadores sin
comillas), así que todo este archivo trabaja con CUSTOMERID, STOCKCODE,
INVOICEDATE, etc. — a diferencia de ft_engineering.py (basado en el csv
local), que usaba los nombres tal cual venían del csv.

Diferencia clave con ft_engineering.py: aquí también se ENTRENAN los modelos
(get_als_recommender / get_fpgrowth_recommender), no solo se preparan los
datos. La API (main.py) llama a estas dos funciones UNA sola vez al arrancar
y sirve desde memoria — por eso ya no hay split 80/20 ni evaluación aquí:
ambos modelos se entrenan con el 100% del histórico disponible, porque este
archivo ya no mide métricas (eso se quedó en Modelos_juntos.py / ft_engineering.py,
para el reporte del proyecto).

CustomerID se trata como texto en todo el pipeline, nunca como entero: en
Snowflake la columna está declarada STRING (ver create_table.py), así que
puede llegar como "12347" o con un ".0" colgado si se subió desde una
columna float con nulos — se normaliza aquí, no se asume forma numérica.
"""

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.preprocessing import MultiLabelBinarizer
from implicit.als import AlternatingLeastSquares

from src.snowflake.load_data import load_data_from_snowflake

FACTORS = 50
REGULARIZATION = 0.01
ITERATIONS = 20


def load_raw():
    """Única lectura de datos: trae TRANSACCIONES completa desde Snowflake,
    normaliza columnas a mayúsculas (defensivo, por si el driver devolviera
    algo distinto) y limpia el formato de CUSTOMERID."""
    df = load_data_from_snowflake()
    df.columns = df.columns.str.upper()

    df["INVOICEDATE"] = pd.to_datetime(df["INVOICEDATE"])
    df = df.sort_values("INVOICEDATE").reset_index(drop=True)

    df["CUSTOMERID"] = df["CUSTOMERID"].astype(str).str.strip()
    df["CUSTOMERID"] = df["CUSTOMERID"].str.replace(r"\.0$", "", regex=True)

    return df


# ============================================================
# ALS (por cliente) — entrenado con el 100% del histórico
# ============================================================

def get_als_recommender(raw_df=None):
    """Entrena ALS y devuelve todo lo que Modelos_top.py necesita para
    recomendar. Nada de esto se recalcula por request.

    Devuelve:
        model: AlternatingLeastSquares ya entrenado
        train_matrix: matriz dispersa cliente x item usada para entrenar
        customer_id_to_code: CustomerID (string) -> código interno
        item_map: código interno -> StockCode
        description_map: StockCode -> Description
    """
    if raw_df is None:
        raw_df = load_raw()

    df = raw_df.dropna(subset=["CUSTOMERID"]).reset_index(drop=True)
    df = df[df["CUSTOMERID"] != ""].reset_index(drop=True)

    df["customer_code"] = df["CUSTOMERID"].astype("category").cat.codes
    df["item_code"] = df["STOCKCODE"].astype("category").cat.codes

    customer_map = dict(enumerate(df["CUSTOMERID"].astype("category").cat.categories))
    item_map = dict(enumerate(df["STOCKCODE"].astype("category").cat.categories))
    description_map = (
        df.dropna(subset=["DESCRIPTION"])
        .drop_duplicates(subset=["STOCKCODE"])
        .set_index("STOCKCODE")["DESCRIPTION"]
        .to_dict()
    )

    n_customers = df["customer_code"].nunique()
    n_items = df["item_code"].nunique()

    grouped = (
        df.groupby(["customer_code", "item_code"], observed=True)["QUANTITY"]
        .sum()
        .reset_index()
    )
    train_matrix = csr_matrix(
        (grouped["QUANTITY"], (grouped["customer_code"], grouped["item_code"])),
        shape=(n_customers, n_items),
    )

    model = AlternatingLeastSquares(
        factors=FACTORS, regularization=REGULARIZATION, iterations=ITERATIONS
    )
    model.fit(train_matrix)

    customer_id_to_code = {v: k for k, v in customer_map.items()}
    return model, train_matrix, customer_id_to_code, item_map, description_map


def get_popularity_recommender(raw_df=None, k=30):
    """Top-k de productos más vendidos (por unidades totales), sin importar
    el cliente. Se usa como respaldo cuando un CustomerID no existe en el
    histórico de ALS (cliente nuevo o inválido), y también para rellenar
    FP-Growth cuando no hay suficientes co-ocurrencias reales.

    k=30 por defecto (más de los 10 que se muestran al final) para tener
    margen de sobra al excluir duplicados o el producto seleccionado."""
    if raw_df is None:
        raw_df = load_raw()

    df = raw_df.dropna(subset=["STOCKCODE"])
    description_map = (
        df.dropna(subset=["DESCRIPTION"])
        .drop_duplicates(subset=["STOCKCODE"])
        .set_index("STOCKCODE")["DESCRIPTION"]
        .to_dict()
    )
    top_codes = (
        df.groupby("STOCKCODE")["QUANTITY"].sum().sort_values(ascending=False).head(k).index.tolist()
    )
    return top_codes, description_map


# ============================================================
# FP-GROWTH (por factura) — construida con el 100% del histórico
# ============================================================

def get_fpgrowth_recommender(raw_df=None):
    """Arma la matriz dispersa factura x producto que necesita FP-Growth,
    ya lista para recomendar.

    Se guarda como matriz DISPERSA (scipy.sparse), no como DataFrame denso:
    la enorme mayoría de combinaciones factura-producto son 0 (una factura
    típica tiene un puñado de productos, no miles), así que un DataFrame
    denso desperdicia memoria y espacio en disco sin necesidad — esto fue
    lo que infló el .pkl a 163MB. La matriz dispersa guarda lo mismo con
    una fracción del tamaño, sin perder ningún dato.

    Devuelve:
        basket_sparse: matriz dispersa (facturas x productos), booleana
        item_columns: lista de StockCode, en el mismo orden que las
            columnas de basket_sparse
        stock_code_to_col: StockCode -> índice de columna (lookup O(1))
        description_map: StockCode -> Description
    """
    if raw_df is None:
        raw_df = load_raw()

    df = raw_df.dropna(subset=["INVOICE", "STOCKCODE"]).reset_index(drop=True)
    description_map = (
        df.drop_duplicates(subset=["STOCKCODE"]).set_index("STOCKCODE")["DESCRIPTION"].to_dict()
    )

    basket_list = df.groupby("INVOICE")["STOCKCODE"].apply(list).tolist()
    mlb = MultiLabelBinarizer(sparse_output=True)
    basket_sparse = mlb.fit_transform(basket_list).tocsr()
    item_columns = list(mlb.classes_)
    stock_code_to_col = {code: i for i, code in enumerate(item_columns)}

    return basket_sparse, item_columns, stock_code_to_col, description_map
