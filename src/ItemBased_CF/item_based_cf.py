"""
Item-Based Collaborative Filtering.

Similitud coseno entre items a partir de la matriz de interacción de train,
recomendaciones por cliente y evaluación con Precision@K sobre el 20% más
reciente del dataset (test_df, ver ft_engineering.py).
"""

import random

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ft_engineering import get_train_test

K = 10


def recommend(customer_code, train_matrix, item_similarity, k=K, exclude_seen=True):
    bought = train_matrix[customer_code].toarray().ravel()
    scores = bought @ item_similarity
    if exclude_seen:
        scores[bought.nonzero()] = -np.inf  # no recomendar lo que ya compró
    top = np.argpartition(scores, -k)[-k:]
    return top[np.argsort(-scores[top])]


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


def main():
    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()
    item_similarity = cosine_similarity(train_matrix.T, dense_output=True)
    n_items = train_matrix.shape[1]

    actuals = test_df.groupby("customer_code")["item_code"].apply(set)

    metrics = {
        exclude_seen: {"precision": [], "recall": [], "ap": [], "recommended_items": set()}
        for exclude_seen in (True, False)
    }
    example_customer_code, example_recs = None, None
    for customer_code, actual_items in actuals.items():
        if customer_code >= train_matrix.shape[0]:
            continue  # cliente que no aparece en train
        if train_matrix[customer_code].nnz == 0:
            continue  # cliente sin historial en train, no se puede recomendar
        for exclude_seen in (True, False):
            recs = recommend(customer_code, train_matrix, item_similarity, exclude_seen=exclude_seen)
            m = metrics[exclude_seen]
            p = precision_at_k(recs, actual_items)
            if p is not None:
                m["precision"].append(p)
                m["recall"].append(recall_at_k(recs, actual_items))
                m["ap"].append(average_precision_at_k(recs, actual_items))
            m["recommended_items"].update(recs)
            if exclude_seen and example_customer_code is None and random.random() < 0.05:
                example_customer_code, example_recs = customer_code, recs

    for exclude_seen, label in ((True, "excluyendo recompras"), (False, "permitiendo recompras")):
        m = metrics[exclude_seen]
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
