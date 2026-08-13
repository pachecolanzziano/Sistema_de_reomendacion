"""
Sistema de recomendación de productos — Online Retail II.

Integra los dos modelos de mejor desempeño del proyecto en un solo archivo:
  - ALS (factorización matricial, feedback implícito)
  - FP-Growth (cross-sell por co-ocurrencia en factura)

ALS usa el preprocesamiento por cliente que vive en ft_engineering.py (split
temporal 80/20, matriz de interacción cliente-item). FP-Growth usa su propio
preprocesamiento porque trabaja a nivel de factura, no de cliente.

ALS PERMITE recompras: no se excluyen productos que el cliente ya compró
antes. En este dataset mayorista la recompra es una señal de compra real,
no ruido — excluirla perjudicaba notablemente las métricas en las pruebas
del proyecto.
"""

import random

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from implicit.als import AlternatingLeastSquares

from ft_engineering import load_raw, get_train_test, get_train_test_fpgrowth

K = 10
FACTORS = 50
REGULARIZATION = 0.01
ITERATIONS = 20


# ============================================================
# MÉTRICAS COMPARTIDAS
# ============================================================

def precision_at_k(recommended, actual, k=K):
    if not actual:
        return None
    return len(set(recommended[:k]) & actual) / k


def recall_at_k(recommended, actual, k=K):
    if not actual:
        return None
    return len(set(recommended[:k]) & actual) / len(actual)


def average_precision_at_k(recommended, actual, k=K):
    if not actual:
        return None
    hits = 0
    sum_precisions = 0.0
    for i, item in enumerate(recommended[:k], start=1):
        if item in actual:
            hits += 1
            sum_precisions += hits / i
    return sum_precisions / min(len(actual), k)


def print_result_block(model_label, precision, recall, map_score, coverage):
    print("\n" + "=" * 80)
    print(f" RESULTADOS FINALES DE EVALUACIÓN ({model_label.upper()})")
    print("=" * 80)
    print(f" Modelo        : {model_label}")
    print(f" Precision@{K}  : {precision:.4f}")
    print(f" Recall@{K}     : {recall:.4f}")
    print(f" MAP@{K}        : {map_score:.4f}")
    print(f" Coverage@{K}   : {coverage:.4f}")
    print("=" * 80)


# ============================================================
# ALS (permite recompras)
# ============================================================

def recommend_als(model, customer_code, train_matrix, k=K):
    item_ids, _scores = model.recommend(
        customer_code,
        train_matrix[customer_code],
        N=k,
        filter_already_liked_items=False,
    )
    return item_ids


def run_als(train_matrix, test_df, customer_map, item_map, description_map):
    model = AlternatingLeastSquares(
        factors=FACTORS, regularization=REGULARIZATION, iterations=ITERATIONS
    )
    model.fit(train_matrix)

    n_items = train_matrix.shape[1]
    actuals = test_df.groupby("customer_code")["item_code"].apply(set)

    precisions, recalls, aps, recommended_items = [], [], [], set()
    example_customer_code, example_recs = None, None
    for customer_code, actual_items in actuals.items():
        if customer_code >= train_matrix.shape[0]:
            continue
        if train_matrix[customer_code].nnz == 0:
            continue
        recs = recommend_als(model, customer_code, train_matrix)
        p = precision_at_k(recs, actual_items)
        if p is not None:
            precisions.append(p)
            recalls.append(recall_at_k(recs, actual_items))
            aps.append(average_precision_at_k(recs, actual_items))
        recommended_items.update(recs)
        if example_customer_code is None and random.random() < 0.05:
            example_customer_code, example_recs = customer_code, recs

    coverage = len(recommended_items) / n_items
    print_result_block("ALS", np.mean(precisions), np.mean(recalls), np.mean(aps), coverage)
    print(f" Clientes evaluados: {len(precisions)}")
    if example_customer_code is not None:
        names = [description_map.get(item_map[i], item_map[i]) for i in example_recs]
        print(f" Ejemplo, cliente {customer_map[example_customer_code]}: {names}")


# ============================================================
# FP-GROWTH (cross-sell por co-ocurrencia en factura)
# ============================================================

def build_basket_matrix(train_basket_list):
    """A partir de la lista de canastas (una lista de StockCode por factura)
    que entrega get_train_test_fpgrowth() en ft_engineering.py, arma la matriz
    binaria factura x producto que necesita recommend_fp_growth()."""
    mlb = MultiLabelBinarizer()
    basket_array = mlb.fit_transform(train_basket_list)
    return pd.DataFrame(basket_array.astype(bool), columns=mlb.classes_)


def recommend_fp_growth(producto_base_code, basket_matrix, k=K):
    if producto_base_code not in basket_matrix.columns:
        return []
    transacciones = basket_matrix[basket_matrix[producto_base_code]]
    if len(transacciones) == 0:
        return []
    coocurrencias = (
        transacciones.drop(columns=[producto_base_code]).sum().sort_values(ascending=False)
    )
    return coocurrencias.head(k).index.tolist()


def run_fp_growth(test_df, basket_matrix, description_map):
    precisions, recalls, aps, recommended_items = [], [], [], set()
    test_grouped = test_df.groupby("Invoice")["StockCode"].apply(list)

    for _invoice_id, productos_reales in test_grouped.items():
        productos_reales = [str(p).strip() for p in productos_reales if pd.notna(p)]
        if len(productos_reales) < 2:
            continue
        producto_base = productos_reales[0]
        ground_truth = set(productos_reales[1:])
        if producto_base not in basket_matrix.columns or not ground_truth:
            continue

        sugeridos = recommend_fp_growth(producto_base, basket_matrix, k=K)
        if not sugeridos:
            continue

        recommended_items.update(sugeridos)
        precisions.append(precision_at_k(sugeridos, ground_truth))
        recalls.append(recall_at_k(sugeridos, ground_truth))
        aps.append(average_precision_at_k(sugeridos, ground_truth))

    coverage = len(recommended_items) / len(basket_matrix.columns)

    print_result_block("FP-Growth (StockCode)", np.mean(precisions), np.mean(recalls), np.mean(aps), coverage)
    print(f" Facturas evaluadas: {len(precisions)}")

    producto_aleatorio = random.choice(basket_matrix.columns.tolist())
    nombre_producto = description_map.get(producto_aleatorio, producto_aleatorio)
    recomendaciones = recommend_fp_growth(producto_aleatorio, basket_matrix, k=K)
    nombres_rec = [description_map.get(c, c) for c in recomendaciones]
    print(f" Ejemplo, si el cliente lleva '{nombre_producto}': {nombres_rec}")


# ============================================================
# EJECUCIÓN
# ============================================================

def main():
    raw_df = load_raw()  # una sola lectura del csv para los 2 modelos

    train_matrix, test_df, customer_map, item_map, description_map = get_train_test(raw_df=raw_df)
    run_als(train_matrix, test_df, customer_map, item_map, description_map)

    train_basket_list, fp_test_df, fp_description_map = get_train_test_fpgrowth(raw_df=raw_df)
    basket_matrix = build_basket_matrix(train_basket_list)
    run_fp_growth(fp_test_df, basket_matrix, fp_description_map)


if __name__ == "__main__":
    main()
