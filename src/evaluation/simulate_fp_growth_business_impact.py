"""
Simulación de impacto de negocio — FP-Growth / Cross-Sell.

Respeta la lógica actual del proyecto:
- split temporal 80/20
- FP-Growth trabaja a nivel de factura
- primer producto de la factura = producto base
- resto de productos de la factura = ground truth
- recomienda hasta K productos por co-ocurrencia
- calcula valor económico de las coincidencias observadas
"""

from pathlib import Path
import sys
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.Modelos.ft_engineering import get_train_test_fpgrowth

K = 10
TICKET_PROMEDIO = 464.0


def build_basket_matrix(train_basket_list):
    mlb = MultiLabelBinarizer()
    basket_array = mlb.fit_transform(train_basket_list)
    return pd.DataFrame(
        basket_array.astype(bool),
        columns=mlb.classes_,
    )


def recommend_fp_growth(producto_base_code, basket_matrix, k=K):
    if producto_base_code not in basket_matrix.columns:
        return []

    transacciones = basket_matrix[basket_matrix[producto_base_code]]

    if len(transacciones) == 0:
        return []

    coocurrencias = (
        transacciones
        .drop(columns=[producto_base_code])
        .sum()
        .sort_values(ascending=False)
    )
    return coocurrencias.head(k).index.tolist()


def main():
    print("=" * 90)
    print("SIMULACIÓN DE IMPACTO DE NEGOCIO — FP-GROWTH / CROSS-SELL")
    print("=" * 90)
    print(f"Ticket promedio actual: €{TICKET_PROMEDIO:,.2f}")
    print(f"Objetivo +15%: €{TICKET_PROMEDIO * 1.15:,.2f}")
    print(f"Incremento requerido: €{TICKET_PROMEDIO * 0.15:,.2f} por cliente")
    print()

    print("📥 Cargando train/test desde Snowflake...")
    train_basket_list, test_df, description_map = get_train_test_fpgrowth()

    print(f"✅ Canastas de entrenamiento: {len(train_basket_list):,}")
    print(f"✅ Registros test: {len(test_df):,}")

    print("\n🧺 Construyendo matriz de canastas...")
    basket_matrix = build_basket_matrix(train_basket_list)
    print(
        f"✅ Matriz factura × producto: "
        f"{basket_matrix.shape[0]:,} facturas × {basket_matrix.shape[1]:,} productos"
    )

    test_df = test_df.copy()
    test_df["Invoice"] = test_df["Invoice"].astype(str).str.strip()
    test_df["StockCode"] = test_df["StockCode"].astype(str).str.strip()

    if "Quantity" not in test_df.columns or "Price" not in test_df.columns:
        raise ValueError(
            "El test_df no contiene Quantity y Price; "
            "son necesarias para calcular el valor económico."
        )

    test_df["line_value"] = (
        test_df["Quantity"].fillna(0) * test_df["Price"].fillna(0)
    )

    detailed_rows = []
    invoices_evaluated = 0
    recommendations_generated = 0
    relevant_recommendations = 0
    recommended_value = 0.0

    print("\n📊 Generando recomendaciones y contrastándolas con compras reales...")

    for invoice_id, invoice_df in test_df.groupby("Invoice", sort=False):
        products = (
            invoice_df["StockCode"]
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )

        if len(products) < 2:
            continue

        producto_base = products[0]
        ground_truth = set(products[1:])

        if producto_base not in basket_matrix.columns or not ground_truth:
            continue

        recommendations = recommend_fp_growth(
            producto_base,
            basket_matrix,
            k=K,
        )

        if not recommendations:
            continue

        invoices_evaluated += 1
        recommendations_generated += len(recommendations)

        actual_values = (
            invoice_df.groupby("StockCode")["line_value"].sum().to_dict()
        )
        actual_quantities = (
            invoice_df.groupby("StockCode")["Quantity"].sum().to_dict()
        )

        for position, product_code in enumerate(recommendations, start=1):
            product_code = str(product_code).strip()
            relevant = product_code in ground_truth

            value = float(actual_values.get(product_code, 0.0)) if relevant else 0.0
            quantity = (
                float(actual_quantities.get(product_code, 0.0))
                if relevant else 0.0
            )

            if relevant:
                relevant_recommendations += 1
                recommended_value += value

            detailed_rows.append(
                {
                    "invoice": invoice_id,
                    "base_product": producto_base,
                    "base_description": description_map.get(
                        producto_base, producto_base
                    ),
                    "recommended_product": product_code,
                    "recommended_description": description_map.get(
                        product_code, product_code
                    ),
                    "rank": position,
                    "relevant_in_test": relevant,
                    "quantity_purchased": quantity,
                    "value_in_test_eur": value,
                }
            )

    if invoices_evaluated == 0:
        raise RuntimeError(
            "No se pudieron evaluar facturas. Revisa la matriz y el test_df."
        )

    observed_match_rate = (
        relevant_recommendations / recommendations_generated
    )
    mean_value_per_invoice = recommended_value / invoices_evaluated

    print("\n" + "=" * 90)
    print("RESULTADOS DEL BACKTESTING ECONÓMICO — FP-GROWTH")
    print("=" * 90)
    print(f"Facturas evaluadas: {invoices_evaluated:,}")
    print(f"Recomendaciones generadas: {recommendations_generated:,}")
    print(f"Recomendaciones relevantes: {relevant_recommendations:,}")
    print(f"Tasa observada de coincidencia: {observed_match_rate:.2%}")
    print(f"Valor observado de coincidencias: €{recommended_value:,.2f}")
    print(
        f"Valor medio de coincidencias por factura: "
        f"€{mean_value_per_invoice:,.2f}"
    )
    print(
        f"Incremento requerido para +15% del ticket: "
        f"€{TICKET_PROMEDIO * 0.15:,.2f} por cliente"
    )

    output_dir = PROJECT_ROOT / "outputs" / "business_simulation"
    output_dir.mkdir(parents=True, exist_ok=True)

    detail_df = pd.DataFrame(detailed_rows)
    detail_path = output_dir / "fp_growth_recommendation_impact.csv"
    detail_df.to_csv(detail_path, index=False, encoding="utf-8-sig")

    summary_df = pd.DataFrame(
        [{
            "model": "FP-Growth",
            "invoices_evaluated": invoices_evaluated,
            "recommendations_generated": recommendations_generated,
            "relevant_recommendations": relevant_recommendations,
            "observed_match_rate": observed_match_rate,
            "observed_match_value_eur": recommended_value,
            "mean_match_value_per_invoice_eur": mean_value_per_invoice,
            "current_ticket_eur": TICKET_PROMEDIO,
            "target_ticket_eur": TICKET_PROMEDIO * 1.15,
            "required_increment_per_customer_eur": TICKET_PROMEDIO * 0.15,
        }]
    )
    summary_path = output_dir / "fp_growth_business_impact_summary.csv"
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print(f"\n📄 Detalle exportado a: {detail_path}")
    print(f"📄 Resumen exportado a: {summary_path}")
    print("=" * 90)


if __name__ == "__main__":
    main()
