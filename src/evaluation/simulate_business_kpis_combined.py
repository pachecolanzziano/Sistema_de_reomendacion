"""
Simulación de impacto de negocio — ALS + FP-Growth

Este script NO afirma que los KPIs se cumplirán.
Construye escenarios hipotéticos de incrementalidad a partir del
valor observado en el backtesting de cada modelo.

KPI 1:
- Ticket promedio actual: €464
- Objetivo: +15% = €533,60
- Incremento requerido: €69,60 por cliente
- ALS es la base principal porque se evalúa por cliente.

KPI 2:
- Aumento de ventas de productos recomendados.
- FP-Growth aporta la señal de cross-selling y se evalúa por factura.
- No se suman directamente ALS + FP-Growth, porque utilizan unidades
  de evaluación diferentes y podrían generar doble conteo.
"""

from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "business_simulation"

ALS_DETAIL = OUTPUT_DIR / "als_recommendation_impact.csv"
FP_DETAIL = OUTPUT_DIR / "fp_growth_recommendation_impact.csv"

TICKET_ACTUAL = 464.0
TARGET_TICKET = TICKET_ACTUAL * 1.15
REQUIRED_INCREMENT = TARGET_TICKET - TICKET_ACTUAL

# Escenarios de sensibilidad.
SCENARIOS = {
    "Conservador": 0.25,
    "Base": 0.50,
    "Optimista": 0.75,
}

# Umbral matemático exacto para alcanzar el +15% del ticket
# usando el valor observado de coincidencias de ALS.
def load_als_summary():
    if not ALS_DETAIL.exists():
        raise FileNotFoundError(f"No existe: {ALS_DETAIL}")

    df = pd.read_csv(ALS_DETAIL)

    required = {"customer_id", "stock_code", "bought_in_test", "actual_value_eur"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"ALS detail no contiene las columnas esperadas: {sorted(missing)}")

    total_recommendations = len(df)
    relevant = int(df["bought_in_test"].astype(bool).sum())
    total_value = float(
        df.loc[df["bought_in_test"].astype(bool), "actual_value_eur"].fillna(0).sum()
    )

    customer_value = (
        df.loc[df["bought_in_test"].astype(bool)]
        .groupby("customer_id")["actual_value_eur"]
        .sum()
    )

    return {
        "customers_evaluated": int(df["customer_id"].nunique()),
        "recommendations_generated": total_recommendations,
        "relevant_recommendations": relevant,
        "observed_match_rate": relevant / total_recommendations,
        "observed_value_per_customer": float(customer_value.mean()),
        "observed_total_value": total_value,
    }


def load_fp_summary():
    if not FP_DETAIL.exists():
        raise FileNotFoundError(f"No existe: {FP_DETAIL}")

    df = pd.read_csv(FP_DETAIL)

    required = {"invoice", "recommended_product", "relevant_in_test", "value_in_test_eur"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"FP-Growth detail no contiene las columnas esperadas: {sorted(missing)}"
        )

    total_recommendations = len(df)
    relevant = int(df["relevant_in_test"].astype(bool).sum())
    total_value = float(
        df.loc[df["relevant_in_test"].astype(bool), "value_in_test_eur"].fillna(0).sum()
    )

    invoice_value = (
        df.loc[df["relevant_in_test"].astype(bool)]
        .groupby("invoice")["value_in_test_eur"]
        .sum()
    )

    return {
        "invoices_evaluated": int(df["invoice"].nunique()),
        "recommendations_generated": total_recommendations,
        "relevant_recommendations": relevant,
        "observed_match_rate": relevant / total_recommendations,
        "observed_value_per_invoice": float(invoice_value.mean()),
        "observed_total_value": total_value,
    }


def main():
    print("=" * 100)
    print("SIMULACIÓN DE IMPACTO DE NEGOCIO — ALS + FP-GROWTH")
    print("=" * 100)
    print(f"\nKPI 1 — Ticket promedio")
    print(f"Ticket actual:        €{TICKET_ACTUAL:,.2f}")
    print(f"Objetivo +15%:        €{TARGET_TICKET:,.2f}")
    print(f"Incremento requerido: €{REQUIRED_INCREMENT:,.2f} por cliente")

    als = load_als_summary()
    fp = load_fp_summary()

    print("\n--- Resultados observados de ALS ---")
    print(f"Clientes evaluados:             {als['customers_evaluated']:,}")
    print(f"Recomendaciones generadas:      {als['recommendations_generated']:,}")
    print(f"Recomendaciones relevantes:     {als['relevant_recommendations']:,}")
    print(f"Tasa observada de coincidencia: {als['observed_match_rate']:.2%}")
    print(f"Valor observado por cliente:    €{als['observed_value_per_customer']:,.2f}")

    als_threshold = REQUIRED_INCREMENT / als["observed_value_per_customer"]

    als_rows = []
    for scenario, rate in SCENARIOS.items():
        incremental = als["observed_value_per_customer"] * rate
        ticket = TICKET_ACTUAL + incremental
        growth = incremental / TICKET_ACTUAL

        als_rows.append({
            "scenario": scenario,
            "assumed_incrementality": rate,
            "observed_value_per_customer_eur": als["observed_value_per_customer"],
            "simulated_increment_per_customer_eur": incremental,
            "simulated_ticket_eur": ticket,
            "simulated_ticket_growth": growth,
            "reaches_15pct_target": ticket >= TARGET_TICKET,
        })

    als_rows.append({
        "scenario": "Umbral KPI",
        "assumed_incrementality": als_threshold,
        "observed_value_per_customer_eur": als["observed_value_per_customer"],
        "simulated_increment_per_customer_eur": REQUIRED_INCREMENT,
        "simulated_ticket_eur": TARGET_TICKET,
        "simulated_ticket_growth": 0.15,
        "reaches_15pct_target": True,
    })

    als_scenarios = pd.DataFrame(als_rows)

    print("\nEscenarios ALS:")
    print(
        als_scenarios[
            [
                "scenario",
                "assumed_incrementality",
                "simulated_increment_per_customer_eur",
                "simulated_ticket_eur",
                "simulated_ticket_growth",
                "reaches_15pct_target",
            ]
        ].to_string(index=False)
    )

    print("\nKPI 2 — Ventas de productos recomendados")
    print("\n--- Resultados observados de FP-Growth ---")
    print(f"Facturas evaluadas:             {fp['invoices_evaluated']:,}")
    print(f"Recomendaciones generadas:      {fp['recommendations_generated']:,}")
    print(f"Recomendaciones relevantes:     {fp['relevant_recommendations']:,}")
    print(f"Tasa observada de coincidencia: {fp['observed_match_rate']:.2%}")
    print(f"Valor observado por factura:    €{fp['observed_value_per_invoice']:,.2f}")

    fp_rows = []
    for scenario, rate in SCENARIOS.items():
        incremental_value = fp["observed_value_per_invoice"] * rate
        fp_rows.append({
            "scenario": scenario,
            "assumed_incrementality": rate,
            "observed_value_per_invoice_eur": fp["observed_value_per_invoice"],
            "simulated_incremental_sales_per_invoice_eur": incremental_value,
        })

    fp_scenarios = pd.DataFrame(fp_rows)

    print("\nEscenarios FP-Growth:")
    print(
        fp_scenarios[
            [
                "scenario",
                "assumed_incrementality",
                "simulated_incremental_sales_per_invoice_eur",
            ]
        ].to_string(index=False)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    als_path = OUTPUT_DIR / "als_kpi_scenarios.csv"
    fp_path = OUTPUT_DIR / "fp_growth_kpi_scenarios.csv"
    summary_path = OUTPUT_DIR / "business_kpi_simulation_summary.csv"

    als_scenarios.to_csv(als_path, index=False, encoding="utf-8-sig")
    fp_scenarios.to_csv(fp_path, index=False, encoding="utf-8-sig")

    executive = pd.DataFrame([
        {
            "kpi": "Ticket promedio",
            "model": "ALS",
            "baseline_eur": TICKET_ACTUAL,
            "target_eur": TARGET_TICKET,
            "required_increment_eur": REQUIRED_INCREMENT,
            "observed_value_per_unit_eur": als["observed_value_per_customer"],
            "unit": "cliente",
            "incrementality_threshold": als_threshold,
            "note": (
                "El umbral indica qué proporción del valor observado en backtesting "
                "tendría que ser incremental para alcanzar el +15%."
            ),
        },
        {
            "kpi": "Ventas de productos recomendados",
            "model": "FP-Growth",
            "baseline_eur": None,
            "target_eur": None,
            "required_increment_eur": None,
            "observed_value_per_unit_eur": fp["observed_value_per_invoice"],
            "unit": "factura",
            "incrementality_threshold": None,
            "note": (
                "La consigna no define un porcentaje objetivo para este KPI; "
                "se presentan escenarios de incrementalidad."
            ),
        },
    ])

    executive.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 100)
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"✅ {als_path}")
    print(f"✅ {fp_path}")
    print(f"✅ {summary_path}")

    print("\nCONCLUSIÓN METODOLÓGICA")
    print(
        "Los escenarios son simulaciones de sensibilidad basadas en el "
        "valor observado en backtesting."
    )
    print(
        "No demuestran causalidad ni garantizan el cumplimiento de los KPIs."
    )
    print(
        "La validación definitiva requeriría una prueba real en producción, "
        "idealmente mediante un experimento controlado."
    )


if __name__ == "__main__":
    main()