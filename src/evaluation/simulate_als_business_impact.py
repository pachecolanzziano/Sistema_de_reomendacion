"""
Simulación de impacto de negocio de recomendaciones ALS.

Objetivo de esta primera versión:
1. Cargar el train/test temporal que ya utiliza el proyecto.
2. Entrenar ALS una sola vez sobre train.
3. Generar Top-K recomendaciones por cliente.
4. Comparar las recomendaciones contra las compras posteriores del test.
5. Calcular el valor económico de las recomendaciones acertadas.
6. Exportar un CSV para continuar con la simulación de impacto sobre los KPIs.

IMPORTANTE:
- Este script NO demuestra causalidad ni que el KPI del +15% se cumplirá.
- El valor calculado representa compras posteriores que coinciden con productos
  recomendados en el backtesting histórico.
- La conversión de esas coincidencias en ventas adicionales reales se modelará
  después mediante escenarios de sensibilidad.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from implicit.als import AlternatingLeastSquares


# -----------------------------------------------------------------------------
# Rutas e imports del proyecto
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "src" / "Modelos"

# Los módulos actuales del proyecto usan imports locales como:
#     from ft_engineering import get_train_test
# Por eso agregamos src/Modelos al path para reutilizar el código existente
# sin duplicar la lógica de preprocesamiento.
sys.path.insert(0, str(MODELS_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from ft_engineering import get_train_test  # noqa: E402


# -----------------------------------------------------------------------------
# Parámetros de simulación
# -----------------------------------------------------------------------------
K = 10
FACTORS = 50
REGULARIZATION = 0.01
ITERATIONS = 20

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "business_simulation"
OUTPUT_FILE = OUTPUT_DIR / "als_recommendation_impact.csv"

TICKET_AVERAGE_EUR = 464.00
TARGET_INCREASE = 0.15
TARGET_TICKET_EUR = TICKET_AVERAGE_EUR * (1 + TARGET_INCREASE)
TARGET_INCREMENT_EUR = TARGET_TICKET_EUR - TICKET_AVERAGE_EUR


# -----------------------------------------------------------------------------
# Modelo
# -----------------------------------------------------------------------------
def train_als(train_matrix):
    """Entrena ALS una sola vez y devuelve el modelo."""
    model = AlternatingLeastSquares(
        factors=FACTORS,
        regularization=REGULARIZATION,
        iterations=ITERATIONS,
    )
    model.fit(train_matrix)
    return model


def recommend_als(model, customer_code, train_matrix, k=K):
    """Devuelve Top-K recomendaciones permitiendo recompras."""
    item_ids, scores = model.recommend(
        customer_code,
        train_matrix[customer_code],
        N=k,
        filter_already_liked_items=False,
    )
    return item_ids, scores


# -----------------------------------------------------------------------------
# Construcción del dataset de impacto
# -----------------------------------------------------------------------------
def build_impact_table(model, train_matrix, test_df, item_map, description_map):
    """Genera una fila por recomendación y marca si apareció posteriormente."""
    rows: list[dict] = []

    # Compras posteriores por cliente + producto.
    # Usamos Quantity * Price para obtener el valor monetario observado en test.
    test = test_df.copy()
    test["Quantity"] = pd.to_numeric(test["Quantity"], errors="coerce").fillna(0)
    test["Price"] = pd.to_numeric(test["Price"], errors="coerce").fillna(0)
    test["line_value"] = test["Quantity"] * test["Price"]

    # Para la simulación de compra, nos quedamos con líneas positivas.
    test_positive = test[(test["Quantity"] > 0) & (test["Price"] > 0)].copy()

    # Si hay varias líneas del mismo producto para el mismo cliente en test,
    # consolidamos cantidad y valor.
    actuals = (
        test_positive.groupby(["customer_code", "StockCode"], as_index=False)
        .agg(
            actual_quantity=("Quantity", "sum"),
            actual_value_eur=("line_value", "sum"),
        )
    )

    actual_lookup = {
        (row.customer_code, str(row.StockCode)): {
            "actual_quantity": float(row.actual_quantity),
            "actual_value_eur": float(row.actual_value_eur),
        }
        for row in actuals.itertuples(index=False)
    }

    # No todos los customer_code del test necesariamente existen en train.
    customers = sorted(test_positive["customer_code"].dropna().unique())

    for customer_code in customers:
        customer_code = int(customer_code)

        if customer_code >= train_matrix.shape[0]:
            continue
        if train_matrix[customer_code].nnz == 0:
            continue

        recommended_ids, scores = recommend_als(
            model,
            customer_code,
            train_matrix,
            k=K,
        )

        # ID real del cliente.
        customer_id = int(customer_code)
        # get_train_test no devuelve el customer_map aquí como argumento de esta
        # función, así que después sustituimos el ID usando el mapa completo.
        # Este campo se rellena en main().

        for rank, (item_code, score) in enumerate(
            zip(recommended_ids, scores), start=1
        ):
            stock_code = str(item_map[int(item_code)])
            actual = actual_lookup.get((customer_code, stock_code))

            rows.append(
                {
                    "customer_code": customer_id,
                    "rank": rank,
                    "item_code": int(item_code),
                    "stock_code": stock_code,
                    "description": description_map.get(stock_code, stock_code),
                    "als_score": float(score),
                    "bought_in_test": actual is not None,
                    "actual_quantity": 0.0 if actual is None else actual["actual_quantity"],
                    "actual_value_eur": 0.0 if actual is None else actual["actual_value_eur"],
                }
            )

    return pd.DataFrame(rows)


# -----------------------------------------------------------------------------
# Resumen
# -----------------------------------------------------------------------------
def summarize_impact(detail_df: pd.DataFrame) -> dict:
    """Calcula indicadores principales del backtesting económico."""
    if detail_df.empty:
        raise ValueError("No se generaron recomendaciones para el conjunto evaluado.")

    total_recommendations = len(detail_df)
    hits = int(detail_df["bought_in_test"].sum())
    total_hit_value = float(detail_df.loc[detail_df["bought_in_test"], "actual_value_eur"].sum())

    customer_summary = (
        detail_df.groupby("customer_code")
        .agg(
            recommendations=("stock_code", "count"),
            relevant_recommendations=("bought_in_test", "sum"),
            matched_value_eur=("actual_value_eur", "sum"),
        )
        .reset_index()
    )

    return {
        "customers_evaluated": int(customer_summary["customer_code"].nunique()),
        "total_recommendations": total_recommendations,
        "relevant_recommendations": hits,
        "observed_hit_rate": hits / total_recommendations,
        "observed_hit_value_eur": total_hit_value,
        "avg_matched_value_per_customer_eur": float(customer_summary["matched_value_eur"].mean()),
        "ticket_average_eur": TICKET_AVERAGE_EUR,
        "target_ticket_eur": TARGET_TICKET_EUR,
        "target_increment_eur": TARGET_INCREMENT_EUR,
    }


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("SIMULACIÓN DE IMPACTO DE NEGOCIO — ALS")
    print("=" * 80)
    print(f"Ticket promedio actual: €{TICKET_AVERAGE_EUR:,.2f}")
    print(f"Objetivo +15%: €{TARGET_TICKET_EUR:,.2f}")
    print(f"Incremento requerido: €{TARGET_INCREMENT_EUR:,.2f} por cliente")
    print("\n📥 Cargando train/test desde Snowflake...")

    train_matrix, test_df, customer_map, item_map, description_map = get_train_test()

    print(f"✅ Matriz de entrenamiento: {train_matrix.shape}")
    print(f"✅ Registros test: {len(test_df):,}")
    print(f"✅ Clientes disponibles: {len(customer_map):,}")
    print(f"✅ Productos disponibles: {len(item_map):,}")

    print("\n🧠 Entrenando ALS una sola vez...")
    model = train_als(train_matrix)
    print("✅ ALS entrenado")

    print("\n📊 Generando recomendaciones y contrastándolas con compras futuras...")
    detail_df = build_impact_table(
        model=model,
        train_matrix=train_matrix,
        test_df=test_df,
        item_map=item_map,
        description_map=description_map,
    )

    if detail_df.empty:
        raise ValueError("La tabla de impacto quedó vacía.")

    # Reemplazar el código interno por el CustomerID real.
    detail_df["customer_id"] = detail_df["customer_code"].map(customer_map)
    detail_df = detail_df[
        [
            "customer_id",
            "customer_code",
            "rank",
            "item_code",
            "stock_code",
            "description",
            "als_score",
            "bought_in_test",
            "actual_quantity",
            "actual_value_eur",
        ]
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    detail_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    summary = summarize_impact(detail_df)

    print("\n" + "=" * 80)
    print("RESULTADOS DEL BACKTESTING ECONÓMICO")
    print("=" * 80)
    print(f"Clientes evaluados: {summary['customers_evaluated']:,}")
    print(f"Recomendaciones generadas: {summary['total_recommendations']:,}")
    print(f"Recomendaciones relevantes: {summary['relevant_recommendations']:,}")
    print(f"Tasa observada de coincidencia: {summary['observed_hit_rate']:.2%}")
    print(f"Valor observado de coincidencias: €{summary['observed_hit_value_eur']:,.2f}")
    print(
        "Valor medio de coincidencias por cliente: "
        f"€{summary['avg_matched_value_per_customer_eur']:,.2f}"
    )
    print(f"Objetivo de incremento por cliente: €{summary['target_increment_eur']:,.2f}")
    print(f"\n📄 Detalle exportado a: {OUTPUT_FILE}")
    print("=" * 80)


if __name__ == "__main__":
    main()