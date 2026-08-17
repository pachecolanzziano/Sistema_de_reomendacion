"""
Entrena ALS, FP-Growth y el baseline de popularidad UNA vez, y guarda todo
en src/api/artifacts/ para que main.py los cargue sin necesitar conexión a
Snowflake en tiempo de ejecución (necesario para dockerizar con arranque
instantáneo).

Correr manualmente, con acceso a Snowflake, desde la raíz del proyecto:

    python -m src.api.train_and_export

Cada vez que quieras refrescar los datos/modelos: vuelve a correr esto y
reconstruye la imagen de Docker con los artefactos nuevos.
"""

import pickle
from pathlib import Path

from scipy.sparse import save_npz

from src.api.ft_engineering2 import (
    load_raw,
    get_als_recommender,
    get_fpgrowth_recommender,
    get_popularity_recommender,
)

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

def main():
    ARTIFACTS_DIR.mkdir(exist_ok=True)

    print("Cargando datos desde Snowflake...")
    raw_df = load_raw()

    print("Entrenando ALS...")
    als_model, train_matrix, customer_id_to_code, item_map, description_map = (
        get_als_recommender(raw_df=raw_df)
    )
    als_model.save(str(ARTIFACTS_DIR / "als_model.npz"))
    save_npz(ARTIFACTS_DIR / "train_matrix.npz", train_matrix)

    print("Construyendo matriz de FP-Growth...")
    basket_sparse, item_columns, stock_code_to_col, fp_description_map = (
        get_fpgrowth_recommender(raw_df=raw_df)
    )
    save_npz(ARTIFACTS_DIR / "basket_matrix.npz", basket_sparse)

    print("Calculando baseline de popularidad...")
    popularity_top_codes, popularity_description_map = get_popularity_recommender(raw_df=raw_df)

    with open(ARTIFACTS_DIR / "artifacts.pkl", "wb") as f:
        pickle.dump(
            {
                "customer_id_to_code": customer_id_to_code,
                "item_map": item_map,
                "description_map": description_map,
                "item_columns": item_columns,
                "stock_code_to_col": stock_code_to_col,
                "fp_description_map": fp_description_map,
                "popularity_top_codes": popularity_top_codes,
                "popularity_description_map": popularity_description_map,
            },
            f,
        )

    print(f"Listo. Artefactos guardados en {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()
