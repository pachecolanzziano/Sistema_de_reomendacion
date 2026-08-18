"""
Funciones de recomendación listas para usar desde la API (main.py).

No entrena nada ni calcula métricas — eso vive en ft_engineering2.py (los
modelos ya llegan entrenados) y en Modelos_juntos.py / ft_engineering.py
(la evaluación, para el reporte del proyecto). Este archivo solo envuelve
el modelo ALS y la matriz de FP-Growth ya entrenados en dos funciones
simples, para que main.py no tenga que conocer los detalles de cada modelo.
"""

import numpy as np

K = 10


def recomendar_als(customer_id, model, train_matrix, customer_id_to_code, item_map, description_map, k=K):
    """Top-k de productos recomendados por ALS para un CustomerID real
    (string, tal como llega de Snowflake). None si el cliente no existe
    en el histórico de entrenamiento."""
    customer_code = customer_id_to_code.get(str(customer_id).strip())
    if customer_code is None:
        return None

    item_ids, _scores = model.recommend(
        customer_code,
        train_matrix[customer_code],
        N=k,
        filter_already_liked_items=False,
    )
    return [
        {"stock_code": item_map[i], "description": description_map.get(item_map[i], item_map[i])}
        for i in item_ids
    ]


def recomendar_popularidad(top_codes, description_map, k=K):
    """Top-k de productos más vendidos. Se usa como respaldo cuando
    recomendar_als() no encuentra al cliente (nuevo o CustomerID inválido)."""
    return [
        {"stock_code": c, "description": description_map.get(c, c)}
        for c in top_codes[:k]
    ]


def recomendar_fp_growth(
    stock_code,
    basket_sparse,
    item_columns,
    stock_code_to_col,
    description_map,
    popularity_top_codes,
    popularity_description_map,
    k=K,
):
    """Top-k de productos que suelen comprarse junto con stock_code.

    Si las co-ocurrencias reales no alcanzan para completar k (poco
    historial de ese producto, o directamente no existe en el histórico
    de FP-Growth), rellena con el baseline de popularidad hasta llegar a
    k — nunca repite un producto ya incluido ni el propio stock_code.

    basket_sparse es una matriz dispersa (facturas x productos); item_columns
    e stock_code_to_col traducen entre StockCode e índice de columna."""
    resultados = []
    col_idx = stock_code_to_col.get(stock_code)

    if col_idx is not None:
        mask = basket_sparse[:, col_idx].toarray().ravel().astype(bool)
        if mask.any():
            co_occurrence = np.asarray(basket_sparse[mask].sum(axis=0)).ravel()
            co_occurrence[col_idx] = -1  # nunca recomendar el mismo producto
            top_idx = np.argsort(-co_occurrence, kind="stable")[:k]
            top_idx = [i for i in top_idx if co_occurrence[i] > 0]
            resultados = [
                {"stock_code": item_columns[i], "description": description_map.get(item_columns[i], item_columns[i])}
                for i in top_idx
            ]

    if len(resultados) < k:
        ya_incluidos = {r["stock_code"] for r in resultados}
        ya_incluidos.add(stock_code)
        for code in popularity_top_codes:
            if len(resultados) >= k:
                break
            if code in ya_incluidos:
                continue
            resultados.append({"stock_code": code, "description": popularity_description_map.get(code, code)})
            ya_incluidos.add(code)

    return resultados
