from io import StringIO

import pandas as pd

from firebase_config import get_firestore_client


COLLECTION_NAME = "datasets"
DOCUMENT_ID = "retail_dataset"


def load_dataset():
    """
    Recupera el CSV almacenado en Firestore y lo devuelve
    como un pandas DataFrame.
    """

    db = get_firestore_client()

    document_ref = (
        db.collection(COLLECTION_NAME)
        .document(DOCUMENT_ID)
    )

    document = document_ref.get()

    if not document.exists:
        raise FileNotFoundError(
            "No existe el dataset en Firestore."
        )

    data = document.to_dict()

    csv_text = data.get("csv_data")

    if not csv_text:
        raise ValueError(
            "El documento existe, pero no contiene "
            "el campo 'csv_data'."
        )

    df = pd.read_csv(
        StringIO(csv_text)
    )

    return df


if __name__ == "__main__":
    df = load_dataset()

    print("Dataset descargado correctamente.")
    print()
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print()
    print("Columnas:")
    print(df.columns.tolist())
    print()
    print("Primeras filas:")
    print(df.head())