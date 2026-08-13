"""
API para visualizar las recomendaciones de ALS y FP-Growth.

Carga los datos de Snowflake y entrena ambos modelos UNA sola vez al
arrancar (lifespan) y los sirve desde memoria — ningún endpoint vuelve a
entrenar ni a leer Snowflake por request.

Cómo correrla (desde la raíz del proyecto, la carpeta que contiene `src/`):
    uvicorn src.api.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.ft_engineering2 import load_raw, get_als_recommender, get_fpgrowth_recommender
from src.api.Modelos_top import recomendar_als, recomendar_fp_growth

modelos = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cargando datos desde Snowflake y entrenando modelos...")
    raw_df = load_raw()

    (
        modelos["als_model"],
        modelos["train_matrix"],
        modelos["customer_id_to_code"],
        modelos["item_map"],
        modelos["description_map"],
    ) = get_als_recommender(raw_df=raw_df)

    modelos["basket_matrix"], modelos["fp_description_map"] = get_fpgrowth_recommender(raw_df=raw_df)

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
        raise HTTPException(status_code=404, detail="CustomerID no encontrado en el histórico")
    return recs


@app.get("/api/products/{stock_code}/cross-sell")
def get_cross_sell(stock_code: str):
    return recomendar_fp_growth(stock_code, modelos["basket_matrix"], modelos["fp_description_map"])
