"""
ALS (Alternating Least Squares) para feedback implícito.

Se alimenta de la misma matriz de interacción de train que ft_engineering.py
construye para Item-Based CF, y se evalúa con las mismas métricas (Precision,
Recall, MAP, Coverage) para poder comparar los dos modelos directamente.
"""

import random

import numpy as np
from implicit.als import AlternatingLeastSquares

from ft_engineering import get_train_test
from item_based_cf import K, precision_at_k, recall_at_k, average_precision_at_k

FACTORS = 50
REGULARIZATION = 0.01
ITERATIONS = 20


def recommend(model, customer_code, train_matrix, k=K, filter_already_liked=True):
    item_ids, _scores = model.recommend(
        customer_code,
        train_matrix[customer_code],
        N=k,
        filter_already_liked_items=filter_already_liked,
    )
    return item_ids


def main():
    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()
    n_items = train_matrix.shape[1]

    model = AlternatingLeastSquares(
        factors=FACTORS, regularization=REGULARIZATION, iterations=ITERATIONS
    )
    model.fit(train_matrix)

    actuals = test_df.groupby("customer_code")["item_code"].apply(set)

    metrics = {
        filter_seen: {"precision": [], "recall": [], "ap": [], "recommended_items": set()}
        for filter_seen in (True, False)
    }
    example_customer_code, example_recs = None, None
    for customer_code, actual_items in actuals.items():
        if customer_code >= train_matrix.shape[0]:
            continue  # cliente que no aparece en train
        if train_matrix[customer_code].nnz == 0:
            continue  # cliente sin historial en train, no se puede recomendar
        for filter_seen in (True, False):
            recs = recommend(model, customer_code, train_matrix, filter_already_liked=filter_seen)
            m = metrics[filter_seen]
            p = precision_at_k(recs, actual_items)
            if p is not None:
                m["precision"].append(p)
                m["recall"].append(recall_at_k(recs, actual_items))
                m["ap"].append(average_precision_at_k(recs, actual_items))
            m["recommended_items"].update(recs)
            if filter_seen and example_customer_code is None and random.random() < 0.05:
                example_customer_code, example_recs = customer_code, recs

    for filter_seen, label in ((True, "excluyendo recompras"), (False, "permitiendo recompras")):
        m = metrics[filter_seen]
        coverage = len(m["recommended_items"]) / n_items
        print(f"--- {label} ---")
        print(f"Precision@{K}: {np.mean(m['precision']):.4f}")
        print(f"Recall@{K}:    {np.mean(m['recall']):.4f}")
        print(f"MAP@{K}:       {np.mean(m['ap']):.4f}")
        print(f"Coverage@{K}:  {coverage:.4f}")

    print(f"Clientes evaluados: {len(metrics[True]['precision'])}")

    if example_customer_code is not None:
        names = [description_map.get(item_map[i], item_map[i]) for i in example_recs]
        print(f"Ejemplo, cliente {customer_map[example_customer_code]}: {names}")


if __name__ == "__main__":
    main()
