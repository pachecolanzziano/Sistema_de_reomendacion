"""
Funciones de recomendación listas para usar desde la API (main.py).

No entrena nada ni calcula métricas — eso vive en ft_engineering2.py (los
modelos ya llegan entrenados) y en Modelos_juntos.py / ft_engineering.py
(la evaluación, para el reporte del proyecto). Este archivo solo envuelve
el modelo ALS y la matriz de FP-Growth ya entrenados en dos funciones
simples, para que main.py no tenga que conocer los detalles de cada modelo.
"""

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


def recomendar_fp_growth(stock_code, basket_matrix, description_map, k=K):
    """Top-k de productos que suelen comprarse junto con stock_code.
    Lista vacía si el producto no aparece en el histórico de entrenamiento."""
    if stock_code not in basket_matrix.columns:
        return []
    transacciones = basket_matrix[basket_matrix[stock_code]]
    if len(transacciones) == 0:
        return []
    coocurrencias = (
        transacciones.drop(columns=[stock_code]).sum().sort_values(ascending=False)
    )
    top_codes = coocurrencias.head(k).index.tolist()
    return [
        {"stock_code": c, "description": description_map.get(c, c)}
        for c in top_codes
    ]
