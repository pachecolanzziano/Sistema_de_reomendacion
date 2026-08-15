"""
API para visualizar las recomendaciones de ALS y FP-Growth.

Esta versión NO se conecta a Snowflake ni entrena nada: carga los
artefactos ya entrenados por train_and_export.py (src/api/artifacts/) UNA
sola vez al arrancar y los sirve desde memoria. Así el contenedor de Docker
arranca al instante y no necesita credenciales de Snowflake en runtime.

Si aún no generaste los artefactos, corre primero (con acceso a Snowflake):
    python -m src.api.train_and_export

Cómo correr la API (desde la raíz del proyecto, la carpeta que contiene `src/`):
    python -m uvicorn src.api.main:app --reload
"""

import pickle
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from implicit.cpu.als import AlternatingLeastSquares
from scipy.sparse import load_npz

from src.api.Modelos_top import recomendar_als, recomendar_fp_growth, recomendar_popularidad

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"

modelos = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cargando artefactos pre-entrenados...")

    modelos["als_model"] = AlternatingLeastSquares.load(str(ARTIFACTS_DIR / "als_model.npz"))
    modelos["train_matrix"] = load_npz(ARTIFACTS_DIR / "train_matrix.npz")
    modelos["basket_matrix"] = load_npz(ARTIFACTS_DIR / "basket_matrix.npz")

    with open(ARTIFACTS_DIR / "artifacts.pkl", "rb") as f:
        modelos.update(pickle.load(f))

    print("Modelos listos.")
    yield
    modelos.clear()


app = FastAPI(title="Recomendador Online Retail", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="src/api/static"), name="static")


@app.get("/")
def index():
    return FileResponse("src/api/static/index.html")


@app.get("/api/recommendations/{customer_id}")
def get_recommendations(customer_id: str):
    recs = recomendar_als(
        customer_id,
        modelos["als_model"],
        modelos["train_matrix"],
        modelos["customer_id_to_code"],
        modelos["item_map"],
        modelos["description_map"],
    )
    if recs is None:
        recs = recomendar_popularidad(
            modelos["popularity_top_codes"], modelos["popularity_description_map"]
        )
    return recs


@app.get("/api/products/{stock_code}/cross-sell")
def get_cross_sell(stock_code: str):
    return recomendar_fp_growth(
        stock_code,
        modelos["basket_matrix"],
        modelos["item_columns"],
        modelos["stock_code_to_col"],
        modelos["fp_description_map"],
        modelos["popularity_top_codes"],
        modelos["popularity_description_map"],
    )
