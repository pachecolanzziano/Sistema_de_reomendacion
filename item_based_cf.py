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


def recommend(customer_code, train_matrix, item_similarity, k=K):
    bought = train_matrix[customer_code].toarray().ravel()
    scores = bought @ item_similarity
    scores[bought.nonzero()] = -np.inf  # no recomendar lo que ya compró
    top = np.argpartition(scores, -k)[-k:]
    return top[np.argsort(-scores[top])]


def precision_at_k(recommended, actual, k=K):
    if not actual:
        return None
    return len(set(recommended[:k]) & actual) / k


def main():
    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()
    item_similarity = cosine_similarity(train_matrix.T, dense_output=True)

    actuals = test_df.groupby("customer_code")["item_code"].apply(set)

    precisions = []
    example_customer_code, example_recs = None, None
    for customer_code, actual_items in actuals.items():
        if customer_code >= train_matrix.shape[0]:
            continue  # cliente que no aparece en train
        if train_matrix[customer_code].nnz == 0:
            continue  # cliente sin historial en train, no se puede recomendar
        recs = recommend(customer_code, train_matrix, item_similarity)
        p = precision_at_k(recs, actual_items)
        if p is not None:
            precisions.append(p)
        if example_customer_code is None and random.random() < 0.05:
            example_customer_code, example_recs = customer_code, recs

    print(f"Precision@{K} promedio: {np.mean(precisions):.4f}")
    print(f"Clientes evaluados: {len(precisions)}")

    if example_customer_code is not None:
        names = [description_map.get(item_map[i], item_map[i]) for i in example_recs]
        print(f"Ejemplo, cliente {customer_map[example_customer_code]}: {names}")


if __name__ == "__main__":
    main()
