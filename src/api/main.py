"""
API para visualizar las recomendaciones de ALS y FP-Growth.

Al arrancar, carga los artefactos de src/api/artifacts/ una sola vez y los
sirve desde memoria. Si falta alguno, ejecuta train_and_export.py para
generarlos (esto requiere acceso a Snowflake); si ya existen, omite el
entrenamiento y la API arranca directamente.

Cómo correr la API (desde la raíz del proyecto, la carpeta que contiene `src/`):
    python -m uvicorn src.api.main:app --reload
"""

import pickle
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from implicit.cpu.als import AlternatingLeastSquares
from scipy.sparse import load_npz

from src.api.Modelos_top import recomendar_als, recomendar_fp_growth, recomendar_popularidad

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
ARTIFACT_FILES = (
    "als_model.npz",
    "train_matrix.npz",
    "basket_matrix.npz",
    "artifacts.pkl",
)

modelos = {}


def ensure_artifacts() -> None:
    """Genera los artefactos solo cuando falta alguno de los necesarios."""
    missing_files = [
        filename for filename in ARTIFACT_FILES if not (ARTIFACTS_DIR / filename).is_file()
    ]
    if not missing_files:
        print("Artefactos existentes detectados; se omite el entrenamiento.")
        return

    print(
        "Faltan artefactos pre-entrenados "
        f"({', '.join(missing_files)}). Ejecutando train_and_export..."
    )
    subprocess.run(
        [sys.executable, "-m", "src.api.train_and_export"],
        check=True,
    )

    remaining_files = [
        filename for filename in ARTIFACT_FILES if not (ARTIFACTS_DIR / filename).is_file()
    ]
    if remaining_files:
        raise RuntimeError(
            "El entrenamiento terminó sin generar todos los artefactos: "
            f"{', '.join(remaining_files)}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_artifacts()
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
