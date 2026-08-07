"""
Baseline de popularidad.

Recomienda a TODOS los clientes los mismos K productos más vendidos en train
(sin personalización). Sirve como piso de comparación: si Item-Based CF o ALS
no le ganan a esto, no están aportando valor real.
"""

import numpy as np

from ft_engineering import get_train_test
from item_based_cf import K, precision_at_k


def top_k_items(train_matrix, k=K):
    total_qty_per_item = np.asarray(train_matrix.sum(axis=0)).ravel()
    return np.argsort(-total_qty_per_item)[:k]


def main():
    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()
    popular_items = top_k_items(train_matrix)

    actuals = test_df.groupby("customer_code")["item_code"].apply(set)

    precisions = []
    for customer_code, actual_items in actuals.items():
        if customer_code >= train_matrix.shape[0]:
            continue
        if train_matrix[customer_code].nnz == 0:
            continue  # mismo filtro que item_based_cf.py: sin historial en train no cuenta
        p = precision_at_k(popular_items, actual_items)
        if p is not None:
            precisions.append(p)

    names = [description_map.get(item_map[i], item_map[i]) for i in popular_items]
    print(f"Precision@{K} promedio (popularidad): {np.mean(precisions):.4f}")
    print(f"Clientes evaluados: {len(precisions)}")
    print(f"Top {K} productos: {names}")


if __name__ == "__main__":
    main()
