# ===========================================================
# CARGA DE LIBRERÍAS
# ===========================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# ===========================================================
# CARGA DE DATOS
# ===========================================================

RUTA_DATASET = (
    r"C:\Proyectos_soy_henry\Proyecto_Final\Sistema_de_reomendacion"
    r"\data\raw\online_retail_II.csv"
)


df = pd.read_csv(
    RUTA_DATASET,
    sep=",",
    encoding="utf-8-sig"
)


# ===========================================================
# 1. COMPRENSIÓN DEL DATASET
# ===========================================================

def resumen_dataframe(df):
    """
    Genera un resumen inicial del DataFrame:

    - Dimensiones
    - Información general
    - Estadísticos descriptivos
    - Primeras filas
    """

    print("\n" + "=" * 70)
    print("1. RESUMEN INICIAL DEL DATAFRAME")
    print("=" * 70)

    # -------------------------------------------------------
    # 1.1 DIMENSIONES
    # -------------------------------------------------------

    print("\n1.1 DIMENSIONES DEL DATAFRAME")
    print("-" * 70)

    print(f"Filas:    {df.shape[0]:,}")
    print(f"Columnas: {df.shape[1]:,}")

    # -------------------------------------------------------
    # 1.2 INFORMACIÓN GENERAL
    # -------------------------------------------------------

    print("\n1.2 INFORMACIÓN GENERAL")
    print("-" * 70)

    df.info()

    # -------------------------------------------------------
    # 1.3 ESTADÍSTICOS DESCRIPTIVOS
    # -------------------------------------------------------

    print("\n1.3 ESTADÍSTICOS DESCRIPTIVOS")
    print("-" * 70)

    print(
        df.describe(include="all").to_string()
    )

    # -------------------------------------------------------
    # 1.4 PRIMERAS FILAS
    # -------------------------------------------------------

    print("\n1.4 PRIMERAS FILAS")
    print("-" * 70)

    print(
        df.head().to_string()
    )


# ===========================================================
# 3. CALIDAD DE LOS DATOS
# ===========================================================

def analizar_calidad(df):
    """
    Analiza la calidad del DataFrame.

    Evalúa:

    - Valores nulos
    - Registros duplicados
    - Valores únicos
    - Cantidades negativas
    - Cantidades iguales a cero
    - Precios negativos
    - Precios iguales a cero
    - Facturas canceladas
    - Clientes sin identificación
    - Fechas inválidas
    - Valores de venta menores o iguales a cero
    """

    print("\n" + "=" * 70)
    print("3. CALIDAD DE LOS DATOS")
    print("=" * 70)

    # =======================================================
    # 3.1 VALORES NULOS
    # =======================================================

    print("\n3.1 VALORES NULOS")
    print("-" * 70)

    missing = pd.DataFrame({
        "Valores Nulos": df.isnull().sum(),
        "% Nulos": round(
            df.isnull().mean() * 100,
            2
        )
    })

    print(
        missing
        .sort_values(
            "Valores Nulos",
            ascending=False
        )
        .to_string()
    )

    # -------------------------------------------------------
    # Gráfico de valores nulos
    # -------------------------------------------------------

    missing_plot = missing[
        missing["Valores Nulos"] > 0
    ]

    if not missing_plot.empty:

        plt.figure(figsize=(9, 4))

        plt.bar(
            missing_plot.index,
            missing_plot["% Nulos"]
        )

        plt.title("Porcentaje de Valores Nulos")
        plt.ylabel("%")
        plt.xlabel("Columnas")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    else:

        print("\nNo se encontraron valores nulos.")

    # =======================================================
    # 3.2 REGISTROS DUPLICADOS
    # =======================================================

    duplicados = df.duplicated().sum()

    print("\n3.2 REGISTROS DUPLICADOS")
    print("-" * 70)

    print(
        f"Registros duplicados : {duplicados:,}"
    )

    print(
        f"Porcentaje           : "
        f"{duplicados / len(df) * 100:.2f}%"
    )

    # =======================================================
    # 3.3 VALORES ÚNICOS
    # =======================================================

    print("\n3.3 VALORES ÚNICOS")
    print("-" * 70)

    valores_unicos = pd.DataFrame({
        "Valores únicos": df.nunique()
    }).sort_values(
        "Valores únicos",
        ascending=False
    )

    print(
        valores_unicos.to_string()
    )

    # =======================================================
    # 3.4 CONSISTENCIA DE QUANTITY
    # =======================================================

    cantidad_negativa = (
        df["Quantity"] < 0
    ).sum()

    cantidad_cero = (
        df["Quantity"] == 0
    ).sum()

    print("\n3.4 CONSISTENCIA DE QUANTITY")
    print("-" * 70)

    print(
        f"Cantidad negativa     : "
        f"{cantidad_negativa:,}"
    )

    print(
        f"Cantidad igual a cero : "
        f"{cantidad_cero:,}"
    )

    # =======================================================
    # 3.5 CONSISTENCIA DE PRICE
    # =======================================================

    precio_negativo = (
        df["Price"] < 0
    ).sum()

    precio_cero = (
        df["Price"] == 0
    ).sum()

    print("\n3.5 CONSISTENCIA DE PRICE")
    print("-" * 70)

    print(
        f"Precio negativo       : "
        f"{precio_negativo:,}"
    )

    print(
        f"Precio igual a cero   : "
        f"{precio_cero:,}"
    )

    # =======================================================
    # 3.6 FACTURAS CANCELADAS
    # =======================================================

    canceladas = (
        df["Invoice"]
        .astype(str)
        .str.startswith("C")
        .sum()
    )

    print("\n3.6 FACTURAS CANCELADAS")
    print("-" * 70)

    print(
        f"Facturas canceladas : "
        f"{canceladas:,}"
    )

    print(
        f"Porcentaje          : "
        f"{canceladas / len(df) * 100:.2f}%"
    )

    # =======================================================
    # 3.7 CLIENTES SIN IDENTIFICACIÓN
    # =======================================================

    clientes_sin_id = (
        df["Customer ID"].isnull()
    ).sum()

    print("\n3.7 CLIENTES SIN IDENTIFICACIÓN")
    print("-" * 70)

    print(
        f"Clientes sin ID : "
        f"{clientes_sin_id:,}"
    )

    print(
        f"Porcentaje      : "
        f"{clientes_sin_id / len(df) * 100:.2f}%"
    )

    # =======================================================
    # 3.8 CONSISTENCIA DE FECHAS
    # =======================================================

    print("\n3.8 CONSISTENCIA DE FECHAS")
    print("-" * 70)

    print(
        f"Tipo actual de InvoiceDate: "
        f"{df['InvoiceDate'].dtype}"
    )

    fechas_invalidas = 0

    fechas = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    fechas_invalidas = fechas.isna().sum()

    print(
        f"Fechas no convertibles: "
        f"{fechas_invalidas:,}"
    )

    if fechas_invalidas == 0:
        print("Formato de fechas: OK")

    # =======================================================
    # 3.9 TOTAL DE VENTA
    # =======================================================

    total_venta = (
        df["Quantity"] * df["Price"]
    )

    total_no_valido = (
        total_venta <= 0
    ).sum()

    print("\n3.9 CONSISTENCIA DEL TOTAL DE VENTA")
    print("-" * 70)

    print(
        f"Ventas <= 0 : "
        f"{total_no_valido:,}"
    )

    print(
        f"Ventas totales : "
        f"{total_venta.sum():,.2f}"
    )

    # =======================================================
    # 3.10 RESUMEN GENERAL
    # =======================================================

    print("\n" + "=" * 70)
    print("RESUMEN DE CALIDAD")
    print("=" * 70)

    print(
        f"Registros                  : "
        f"{len(df):,}"
    )

    print(
        f"Columnas                   : "
        f"{df.shape[1]:,}"
    )

    print(
        f"Valores nulos              : "
        f"{df.isnull().sum().sum():,}"
    )

    print(
        f"Registros duplicados       : "
        f"{duplicados:,}"
    )

    print(
        f"Clientes sin ID            : "
        f"{clientes_sin_id:,}"
    )

    print(
        f"Facturas canceladas        : "
        f"{canceladas:,}"
    )

    print(
        f"Cantidad negativa          : "
        f"{cantidad_negativa:,}"
    )

    print(
        f"Cantidad igual a cero      : "
        f"{cantidad_cero:,}"
    )

    print(
        f"Precio negativo            : "
        f"{precio_negativo:,}"
    )

    print(
        f"Precio igual a cero        : "
        f"{precio_cero:,}"
    )

    print(
        f"Total de venta <= 0        : "
        f"{total_no_valido:,}"
    )

    print(
        f"Fechas inválidas           : "
        f"{fechas_invalidas:,}"
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return {
        "missing": missing,
        "valores_unicos": valores_unicos,
        "duplicados": duplicados,
        "cantidad_negativa": cantidad_negativa,
        "cantidad_cero": cantidad_cero,
        "precio_negativo": precio_negativo,
        "precio_cero": precio_cero,
        "facturas_canceladas": canceladas,
        "clientes_sin_id": clientes_sin_id,
        "fechas_invalidas": fechas_invalidas,
        "total_no_valido": total_no_valido
    }

# ===========================================================
# 4. LIMPIEZA DE DATOS
# ===========================================================

def limpiar_dataset(
    df,
    ruta_salida="DataSetLimpio_V2.csv",
    generar_graficos=True
):
    """
    Limpia el dataset Online Retail II y genera:

    - Dataset limpio
    - Tabla de comparación antes/después
    - Resumen final
    - Gráficos de impacto de la limpieza
    - Validación del dataset resultante

    Reglas aplicadas:

    1. Quantity >= 1800
    2. Price >= 250
    3. Customer ID nulo
    4. Facturas canceladas
    5. Quantity <= 0
    6. Price <= 0

    Retorna:
        df_clean_v2
        resumen
        resumen_final
    """

    import matplotlib.pyplot as plt

    print("\n" + "=" * 70)
    print("4. LIMPIEZA DEL DATASET")
    print("=" * 70)

    # =======================================================
    # 1. COPIA DEL DATASET ORIGINAL
    # =======================================================

    df_clean = df.copy()

    registros_iniciales = len(df_clean)

    print("\nRegistros iniciales:")
    print(f"{registros_iniciales:,}")

    # =======================================================
    # 2. IDENTIFICAR REGISTROS AFECTADOS
    # =======================================================

    # Outliers Quantity
    outliers_quantity = (
        df_clean["Quantity"] >= 1800
    ).sum()

    # Outliers Price
    outliers_price = (
        df_clean["Price"] >= 250
    ).sum()

    # Customer ID nulo
    customer_id_nulos = (
        df_clean["Customer ID"].isnull()
    ).sum()

    # Facturas canceladas
    facturas_canceladas = (
        df_clean["Invoice"]
        .astype(str)
        .str.startswith("C")
    ).sum()

    # Cantidades negativas
    cantidades_negativas = (
        df_clean["Quantity"] < 0
    ).sum()

    # Cantidades iguales a cero
    cantidades_cero = (
        df_clean["Quantity"] == 0
    ).sum()

    # Precios iguales a cero
    precio_cero = (
        df_clean["Price"] == 0
    ).sum()

    # Precios negativos
    precio_negativo = (
        df_clean["Price"] < 0
    ).sum()

    # =======================================================
    # 3. TABLA DE IMPACTO INICIAL
    # =======================================================

    print("\n" + "-" * 70)
    print("REGISTROS AFECTADOS POR REGLA")
    print("-" * 70)

    print(
        f"Customer ID nulo       : {customer_id_nulos:,}"
    )

    print(
        f"Facturas canceladas    : {facturas_canceladas:,}"
    )

    print(
        f"Quantity negativa      : {cantidades_negativas:,}"
    )

    print(
        f"Quantity igual a cero  : {cantidades_cero:,}"
    )

    print(
        f"Price igual a cero     : {precio_cero:,}"
    )

    print(
        f"Price negativo         : {precio_negativo:,}"
    )

    print(
        f"Quantity >= 1800       : {outliers_quantity:,}"
    )

    print(
        f"Price >= 250           : {outliers_price:,}"
    )

    # =======================================================
    # 4. ELIMINACIÓN DE OUTLIERS
    # =======================================================

    df_clean = df_clean[
        (df_clean["Quantity"] < 1800) &
        (df_clean["Price"] < 250)
    ].copy()

    print("\nDespués de eliminar outliers:")
    print(f"{len(df_clean):,}")

    # =======================================================
    # 5. ELIMINAR CUSTOMER ID NULOS
    # =======================================================

    df_clean = df_clean[
        df_clean["Customer ID"].notna()
    ].copy()

    print("\nDespués de eliminar Customer ID nulos:")
    print(f"{len(df_clean):,}")

    # =======================================================
    # 6. ELIMINAR FACTURAS CANCELADAS
    # =======================================================

    df_clean = df_clean[
        ~df_clean["Invoice"]
        .astype(str)
        .str.startswith("C")
    ].copy()

    print("\nDespués de eliminar facturas canceladas:")
    print(f"{len(df_clean):,}")

    # =======================================================
    # 7. ELIMINAR CANTIDADES NO VÁLIDAS
    # =======================================================

    df_clean = df_clean[
        df_clean["Quantity"] > 0
    ].copy()

    print("\nDespués de eliminar Quantity <= 0:")
    print(f"{len(df_clean):,}")

    # =======================================================
    # 8. ELIMINAR PRECIOS NO VÁLIDOS
    # =======================================================

    df_clean = df_clean[
        df_clean["Price"] > 0
    ].copy()

    print("\nDespués de eliminar Price <= 0:")
    print(f"{len(df_clean):,}")

    # =======================================================
    # 9. REINICIAR ÍNDICE
    # =======================================================

    df_clean.reset_index(
        drop=True,
        inplace=True
    )

    registros_finales = len(df_clean)

    registros_eliminados = (
        registros_iniciales -
        registros_finales
    )

    porcentaje_conservado = (
        registros_finales /
        registros_iniciales *
        100
    )

    porcentaje_eliminado = (
        registros_eliminados /
        registros_iniciales *
        100
    )

    # =======================================================
    # 10. TABLA DE COMPARACIÓN
    # =======================================================

    resumen = pd.DataFrame({

        "Indicador": [

            "Registros",

            "Customer ID nulos",

            "Facturas canceladas",

            "Quantity negativa",

            "Quantity igual a cero",

            "Price negativo",

            "Price igual a cero",

            "Outliers Quantity >= 1800",

            "Outliers Price >= 250"

        ],

        "Antes": [

            len(df),

            customer_id_nulos,

            facturas_canceladas,

            cantidades_negativas,

            cantidades_cero,

            precio_negativo,

            precio_cero,

            outliers_quantity,

            outliers_price

        ],

        "Después": [

            registros_finales,

            df_clean["Customer ID"].isnull().sum(),

            df_clean["Invoice"]
            .astype(str)
            .str.startswith("C")
            .sum(),

            (df_clean["Quantity"] < 0).sum(),

            (df_clean["Quantity"] == 0).sum(),

            (df_clean["Price"] < 0).sum(),

            (df_clean["Price"] == 0).sum(),

            (df_clean["Quantity"] >= 1800).sum(),

            (df_clean["Price"] >= 250).sum()

        ]

    })

    resumen["Eliminados"] = (
        resumen["Antes"] -
        resumen["Después"]
    )

    # =======================================================
    # 11. RESUMEN FINAL
    # =======================================================

    resumen_final = pd.DataFrame({

        "Indicador": [

            "Registros iniciales",

            "Registros eliminados",

            "Registros finales",

            "Porcentaje conservado",

            "Porcentaje eliminado"

        ],

        "Valor": [

            f"{registros_iniciales:,}",

            f"{registros_eliminados:,}",

            f"{registros_finales:,}",

            f"{porcentaje_conservado:.2f}%",

            f"{porcentaje_eliminado:.2f}%"

        ]

    })

    # =======================================================
    # 12. MOSTRAR RESULTADOS
    # =======================================================

    print("\n" + "=" * 70)
    print("COMPARACIÓN ANTES VS DESPUÉS")
    print("=" * 70)

    print(
        resumen.to_string(index=False)
    )

    print("\n" + "=" * 70)
    print("RESUMEN FINAL DE LA LIMPIEZA")
    print("=" * 70)

    print(
        resumen_final.to_string(index=False)
    )

    # =======================================================
    # 13. GRÁFICO 1
    # IMPACTO DE LAS REGLAS
    # =======================================================

    if generar_graficos:

        reglas = pd.DataFrame({

            "Regla": [

                "Customer ID nulo",

                "Factura cancelada",

                "Quantity negativa",

                "Quantity = 0",

                "Price = 0",

                "Quantity >= 1800",

                "Price >= 250"

            ],

            "Registros": [

                customer_id_nulos,

                facturas_canceladas,

                cantidades_negativas,

                cantidades_cero,

                precio_cero,

                outliers_quantity,

                outliers_price

            ]

        })

        reglas = reglas.sort_values(
            "Registros",
            ascending=True
        )

        plt.figure(figsize=(10, 6))

        plt.barh(
            reglas["Regla"],
            reglas["Registros"]
        )

        plt.title(
            "Registros afectados por regla de limpieza"
        )

        plt.xlabel(
            "Número de registros"
        )

        plt.ylabel(
            "Regla de limpieza"
        )

        plt.tight_layout()

        plt.show()

        # ===================================================
        # 14. GRÁFICO 2
        # ANTES VS DESPUÉS
        # ===================================================

        plt.figure(figsize=(8, 5))

        plt.bar(
            ["Dataset inicial", "Dataset limpio"],
            [
                registros_iniciales,
                registros_finales
            ]
        )

        plt.title(
            "Comparación del número de registros"
        )

        plt.ylabel(
            "Número de registros"
        )

        plt.tight_layout()

        plt.show()

        # ===================================================
        # 15. GRÁFICO 3
        # CONSERVACIÓN DEL DATASET
        # ===================================================

        plt.figure(figsize=(6, 6))

        plt.pie(
            [
                registros_finales,
                registros_eliminados
            ],
            labels=[
                "Conservados",
                "Eliminados"
            ],
            autopct="%1.2f%%",
            startangle=90
        )

        plt.title(
            "Resultado del proceso de limpieza"
        )

        plt.tight_layout()

        plt.show()

    # =======================================================
    # 16. VALIDACIÓN FINAL
    # =======================================================

    print("\n" + "=" * 70)
    print("VALIDACIÓN DEL DATASET LIMPIO")
    print("=" * 70)

    print(
        f"Registros                 : "
        f"{len(df_clean):,}"
    )

    print(
        f"Customer ID nulos        : "
        f"{df_clean['Customer ID'].isnull().sum():,}"
    )

    print(
        f"Facturas canceladas      : "
        f"{df_clean['Invoice'].astype(str).str.startswith('C').sum():,}"
    )

    print(
        f"Quantity negativa        : "
        f"{(df_clean['Quantity'] < 0).sum():,}"
    )

    print(
        f"Quantity igual a cero    : "
        f"{(df_clean['Quantity'] == 0).sum():,}"
    )

    print(
        f"Price negativo           : "
        f"{(df_clean['Price'] < 0).sum():,}"
    )

    print(
        f"Price igual a cero       : "
        f"{(df_clean['Price'] == 0).sum():,}"
    )

    print(
        f"Quantity >= 1800         : "
        f"{(df_clean['Quantity'] >= 1800).sum():,}"
    )

    print(
        f"Price >= 250             : "
        f"{(df_clean['Price'] >= 250).sum():,}"
    )

    # =======================================================
    # 17. SELECCIONAR COLUMNAS FINALES
    # =======================================================

    columnas = [

        "Invoice",

        "StockCode",

        "Description",

        "Quantity",

        "InvoiceDate",

        "Price",

        "Customer ID",

        "Country"

    ]

    df_clean_v2 = df_clean[
        columnas
    ].copy()

    # Renombrar Customer ID
    df_clean_v2.rename(
        columns={
            "Customer ID": "CustomerID"
        },
        inplace=True
    )

    # =======================================================
    # 18. GUARDAR CSV
    # =======================================================

    df_clean_v2.to_csv(
        ruta_salida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 70)
    print("ARCHIVO GENERADO")
    print("=" * 70)

    print(
        f"Archivo : {ruta_salida}"
    )

    print(
        f"Registros : {len(df_clean_v2):,}"
    )

    print(
        f"Columnas : {df_clean_v2.columns.tolist()}"
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return (
        df_clean_v2,
        resumen,
        resumen_final
    )

# ===========================================================
# 5. ANÁLISIS UNIVARIADO
# ===========================================================

def analizar_univariado(df_clean, generar_graficos=True):
    """
    Realiza el análisis univariado del dataset limpio.

    Dataset esperado después de la limpieza:

    - Invoice
    - StockCode
    - Description
    - Quantity
    - InvoiceDate
    - Price
    - CustomerID
    - Country

    Variables analizadas:

    Numéricas:
    - Quantity
    - Price
    - Total

    Categóricas:
    - Country
    - StockCode
    - CustomerID
    - Invoice

    Genera:
    - Estadísticos descriptivos
    - Percentiles
    - Histogramas
    - Boxplots
    - Top países
    - Top productos
    - Frecuencia de clientes
    - Resumen general
    """

    print("\n" + "=" * 70)
    print("5. ANÁLISIS UNIVARIADO")
    print("=" * 70)

    # =======================================================
    # 5.0 VALIDACIÓN DE COLUMNAS
    # =======================================================

    columnas_requeridas = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "Price",
        "CustomerID",
        "Country"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df_clean.columns
    ]

    if columnas_faltantes:

        raise KeyError(
            f"Faltan las siguientes columnas en df_clean: "
            f"{columnas_faltantes}"
        )

    # Copia para evitar modificar df_clean
    df_analisis = df_clean.copy()

    # =======================================================
    # 5.1 TOTAL DE VENTA
    # =======================================================

    if "Total" not in df_analisis.columns:

        df_analisis["Total"] = (
            df_analisis["Quantity"] *
            df_analisis["Price"]
        )

    print(
        f"\nRegistros analizados: "
        f"{len(df_analisis):,}"
    )

    print(
        f"Clientes únicos: "
        f"{df_analisis['CustomerID'].nunique():,}"
    )

    print(
        f"Facturas únicas: "
        f"{df_analisis['Invoice'].nunique():,}"
    )

    # =======================================================
    # 5.2 QUANTITY
    # =======================================================

    print("\n5.1 ANÁLISIS DE QUANTITY")
    print("-" * 70)

    quantity_stats = df_analisis["Quantity"].describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )

    print(quantity_stats.to_string())

    q90 = df_analisis["Quantity"].quantile(0.90)
    q95 = df_analisis["Quantity"].quantile(0.95)
    q99 = df_analisis["Quantity"].quantile(0.99)

    print("\nPercentiles principales:")
    print(f"P90 : {q90:.2f}")
    print(f"P95 : {q95:.2f}")
    print(f"P99 : {q99:.2f}")

    # -------------------------------------------------------
    # Gráficos Quantity
    # -------------------------------------------------------

    if generar_graficos:

        # Histograma hasta P99

        plt.figure(figsize=(10, 5))

        plt.hist(
            df_analisis[
                df_analisis["Quantity"] <= q99
            ]["Quantity"],
            bins=40,
            edgecolor="black"
        )

        plt.axvline(
            q99,
            linestyle="--",
            label=f"P99 = {q99:.0f}"
        )

        plt.title(
            "Distribución de Quantity - hasta P99"
        )

        plt.xlabel("Cantidad")
        plt.ylabel("Frecuencia")

        plt.legend()
        plt.tight_layout()
        plt.show()

        # Histograma escala log

        plt.figure(figsize=(10, 5))

        plt.hist(
            df_analisis["Quantity"],
            bins=50,
            log=True,
            edgecolor="black"
        )

        plt.title(
            "Distribución de Quantity - Escala Logarítmica"
        )

        plt.xlabel("Cantidad")
        plt.ylabel("Frecuencia")

        plt.tight_layout()
        plt.show()

        # Boxplot

        plt.figure(figsize=(10, 4))

        plt.boxplot(
            df_analisis["Quantity"],
            vert=False
        )

        plt.title(
            "Boxplot de Quantity"
        )

        plt.xlabel("Cantidad")

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.3 PRICE
    # =======================================================

    print("\n5.2 ANÁLISIS DE PRICE")
    print("-" * 70)

    price_stats = df_analisis["Price"].describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )

    print(price_stats.to_string())

    price_p90 = df_analisis["Price"].quantile(0.90)
    price_p95 = df_analisis["Price"].quantile(0.95)
    price_p99 = df_analisis["Price"].quantile(0.99)

    print("\nPercentiles principales:")
    print(f"P90 : {price_p90:.2f}")
    print(f"P95 : {price_p95:.2f}")
    print(f"P99 : {price_p99:.2f}")

    # -------------------------------------------------------
    # Gráficos Price
    # -------------------------------------------------------

    if generar_graficos:

        plt.figure(figsize=(10, 5))

        plt.hist(
            df_analisis[
                df_analisis["Price"] <= price_p99
            ]["Price"],
            bins=40,
            edgecolor="black"
        )

        plt.axvline(
            price_p99,
            linestyle="--",
            label=f"P99 = {price_p99:.2f}"
        )

        plt.title(
            "Distribución de Price - hasta P99"
        )

        plt.xlabel("Precio")
        plt.ylabel("Frecuencia")

        plt.legend()
        plt.tight_layout()
        plt.show()

        # Boxplot

        plt.figure(figsize=(10, 4))

        plt.boxplot(
            df_analisis["Price"],
            vert=False
        )

        plt.title(
            "Boxplot de Price"
        )

        plt.xlabel("Precio")

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.4 TOTAL DE VENTA
    # =======================================================

    print("\n5.3 ANÁLISIS DE TOTAL DE VENTA")
    print("-" * 70)

    total_stats = df_analisis["Total"].describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )

    print(total_stats.to_string())

    ventas_totales = df_analisis["Total"].sum()

    total_p90 = df_analisis["Total"].quantile(0.90)
    total_p95 = df_analisis["Total"].quantile(0.95)
    total_p99 = df_analisis["Total"].quantile(0.99)

    print(
        f"\nVentas totales: "
        f"{ventas_totales:,.2f}"
    )

    print("\nPercentiles principales:")
    print(f"P90 : {total_p90:,.2f}")
    print(f"P95 : {total_p95:,.2f}")
    print(f"P99 : {total_p99:,.2f}")

    # -------------------------------------------------------
    # Gráficos Total
    # -------------------------------------------------------

    if generar_graficos:

        plt.figure(figsize=(10, 5))

        plt.hist(
            df_analisis[
                df_analisis["Total"] <= total_p99
            ]["Total"],
            bins=40,
            edgecolor="black"
        )

        plt.axvline(
            total_p99,
            linestyle="--",
            label=f"P99 = {total_p99:,.2f}"
        )

        plt.title(
            "Distribución del Total de Venta - hasta P99"
        )

        plt.xlabel("Valor de venta")
        plt.ylabel("Frecuencia")

        plt.legend()
        plt.tight_layout()
        plt.show()

        # Boxplot

        plt.figure(figsize=(10, 4))

        plt.boxplot(
            df_analisis["Total"],
            vert=False
        )

        plt.title(
            "Boxplot del Total de Venta"
        )

        plt.xlabel("Total")

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.5 COUNTRY
    # =======================================================

    print("\n5.4 ANÁLISIS DE COUNTRY")
    print("-" * 70)

    paises = (
        df_analisis["Country"]
        .value_counts()
        .head(10)
    )

    print(
        "\nTop 10 países por número de registros:"
    )

    print(
        paises.to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(10, 5))

        paises.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 10 Países por Número de Registros"
        )

        plt.xlabel("Número de registros")
        plt.ylabel("País")

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.6 PRODUCTOS
    # =======================================================

    print("\n5.5 ANÁLISIS DE PRODUCTOS")
    print("-" * 70)

    productos = (
        df_analisis
        .groupby("Description")["Quantity"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    print(
        "\nTop 10 productos por unidades vendidas:"
    )

    print(
        productos.to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(10, 6))

        productos.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 10 Productos por Cantidad Vendida"
        )

        plt.xlabel(
            "Unidades vendidas"
        )

        plt.ylabel(
            "Producto"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.7 CLIENTES
    # =======================================================

    print("\n5.6 ANÁLISIS DE CLIENTES")
    print("-" * 70)

    compras_cliente = (
        df_analisis
        .groupby("CustomerID")["Invoice"]
        .nunique()
        .sort_values(
            ascending=False
        )
    )

    clientes_unicos = (
        df_analisis["CustomerID"]
        .nunique()
    )

    compras_promedio = (
        compras_cliente.mean()
    )

    print(
        f"\nClientes únicos: "
        f"{clientes_unicos:,}"
    )

    print(
        f"Compras promedio por cliente: "
        f"{compras_promedio:.2f}"
    )

    print(
        "\nTop 10 clientes por número de facturas:"
    )

    print(
        compras_cliente
        .head(10)
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(10, 5))

        plt.hist(
            compras_cliente,
            bins=40,
            edgecolor="black"
        )

        plt.title(
            "Distribución de Compras por Cliente"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "Número de clientes"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 5.8 FACTURAS
    # =======================================================

    print("\n5.7 ANÁLISIS DE FACTURAS")
    print("-" * 70)

    facturas = (
        df_analisis["Invoice"]
        .nunique()
    )

    print(
        f"Número de facturas únicas: "
        f"{facturas:,}"
    )

    # =======================================================
    # 5.9 STOCKCODES
    # =======================================================

    print("\n5.8 ANÁLISIS DE STOCKCODE")
    print("-" * 70)

    productos_unicos = (
        df_analisis["StockCode"]
        .nunique()
    )

    print(
        f"Productos únicos: "
        f"{productos_unicos:,}"
    )

    # =======================================================
    # 5.10 RESUMEN NUMÉRICO
    # =======================================================

    resumen = pd.DataFrame({

        "Variable": [
            "Quantity",
            "Price",
            "Total"
        ],

        "Media": [
            df_analisis["Quantity"].mean(),
            df_analisis["Price"].mean(),
            df_analisis["Total"].mean()
        ],

        "Mediana": [
            df_analisis["Quantity"].median(),
            df_analisis["Price"].median(),
            df_analisis["Total"].median()
        ],

        "P90": [
            df_analisis["Quantity"].quantile(0.90),
            df_analisis["Price"].quantile(0.90),
            df_analisis["Total"].quantile(0.90)
        ],

        "P95": [
            df_analisis["Quantity"].quantile(0.95),
            df_analisis["Price"].quantile(0.95),
            df_analisis["Total"].quantile(0.95)
        ],

        "P99": [
            df_analisis["Quantity"].quantile(0.99),
            df_analisis["Price"].quantile(0.99),
            df_analisis["Total"].quantile(0.99)
        ]

    })

    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS UNIVARIADO")
    print("=" * 70)

    print(
        resumen.to_string(
            index=False
        )
    )

    print("=" * 70)

    # =======================================================
    # RETORNO DE RESULTADOS
    # =======================================================

    return {

        "quantity_stats": quantity_stats,

        "price_stats": price_stats,

        "total_stats": total_stats,

        "top_paises": paises,

        "top_productos": productos,

        "compras_cliente": compras_cliente,

        "resumen": resumen,

        "clientes_unicos": clientes_unicos,

        "facturas_unicas": facturas,

        "productos_unicos": productos_unicos,

        "ventas_totales": ventas_totales
    }

# ===========================================================
# 6. ANÁLISIS DEL TAMAÑO DE LA CESTA
# ===========================================================

def analizar_basket_size(df_clean, generar_graficos=True):
    """
    Analiza el tamaño de la cesta de compra.

    Basket Size = número de productos diferentes
    dentro de cada factura.

    Variables requeridas:
    - Invoice
    - StockCode

    Genera:
    - Estadísticos descriptivos
    - Percentiles
    - Distribución del Basket Size
    - Boxplot
    - Distribución hasta P99
    - Rangos de tamaño de cesta
    - Top 10 facturas por variedad de productos
    - Indicadores para Market Basket Analysis

    Retorna:
    - basket_size
    - resumen_basket
    - distribucion_basket
    """

    import matplotlib.pyplot as plt

    print("\n" + "=" * 70)
    print("6. ANÁLISIS DEL TAMAÑO DE LA CESTA")
    print("=" * 70)

    # =======================================================
    # 6.1 VALIDACIÓN
    # =======================================================

    columnas_requeridas = [
        "Invoice",
        "StockCode"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df_clean.columns
    ]

    if columnas_faltantes:

        raise KeyError(
            f"Faltan columnas requeridas: "
            f"{columnas_faltantes}"
        )

    # =======================================================
    # 6.2 CALCULAR BASKET SIZE
    # =======================================================

    basket_size = (
        df_clean
        .groupby("Invoice")["StockCode"]
        .nunique()
        .reset_index()
    )

    basket_size.columns = [
        "Invoice",
        "Basket_Size"
    ]

    # =======================================================
    # 6.3 ESTADÍSTICOS
    # =======================================================

    print("\n6.1 ESTADÍSTICOS DEL BASKET SIZE")
    print("-" * 70)

    estadisticos = basket_size[
        "Basket_Size"
    ].describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99
        ]
    )

    print(
        estadisticos.to_string()
    )

    # =======================================================
    # 6.4 INDICADORES PRINCIPALES
    # =======================================================

    numero_facturas = len(basket_size)

    promedio = (
        basket_size["Basket_Size"]
        .mean()
    )

    mediana = (
        basket_size["Basket_Size"]
        .median()
    )

    minimo = (
        basket_size["Basket_Size"]
        .min()
    )

    maximo = (
        basket_size["Basket_Size"]
        .max()
    )

    p90 = (
        basket_size["Basket_Size"]
        .quantile(0.90)
    )

    p95 = (
        basket_size["Basket_Size"]
        .quantile(0.95)
    )

    p99 = (
        basket_size["Basket_Size"]
        .quantile(0.99)
    )

    # =======================================================
    # 6.5 COMPORTAMIENTO DE LAS CESTAS
    # =======================================================

    facturas_1_producto = (
        basket_size["Basket_Size"] == 1
    ).sum()

    facturas_2_mas = (
        basket_size["Basket_Size"] >= 2
    ).sum()

    facturas_5_mas = (
        basket_size["Basket_Size"] >= 5
    ).sum()

    facturas_10_mas = (
        basket_size["Basket_Size"] >= 10
    ).sum()

    porcentaje_1 = (
        facturas_1_producto /
        numero_facturas *
        100
    )

    porcentaje_2_mas = (
        facturas_2_mas /
        numero_facturas *
        100
    )

    porcentaje_5_mas = (
        facturas_5_mas /
        numero_facturas *
        100
    )

    porcentaje_10_mas = (
        facturas_10_mas /
        numero_facturas *
        100
    )

    print("\n6.2 INDICADORES PRINCIPALES")
    print("-" * 70)

    print(
        f"Facturas analizadas          : "
        f"{numero_facturas:,}"
    )

    print(
        f"Basket Size promedio         : "
        f"{promedio:.2f}"
    )

    print(
        f"Basket Size mediana          : "
        f"{mediana:.0f}"
    )

    print(
        f"Basket Size mínimo           : "
        f"{minimo}"
    )

    print(
        f"Basket Size máximo           : "
        f"{maximo}"
    )

    print(
        f"P90                          : "
        f"{p90:.0f}"
    )

    print(
        f"P95                          : "
        f"{p95:.0f}"
    )

    print(
        f"P99                          : "
        f"{p99:.0f}"
    )

    print(
        f"\nFacturas con 1 producto     : "
        f"{facturas_1_producto:,} "
        f"({porcentaje_1:.2f}%)"
    )

    print(
        f"Facturas con 2+ productos   : "
        f"{facturas_2_mas:,} "
        f"({porcentaje_2_mas:.2f}%)"
    )

    print(
        f"Facturas con 5+ productos   : "
        f"{facturas_5_mas:,} "
        f"({porcentaje_5_mas:.2f}%)"
    )

    print(
        f"Facturas con 10+ productos  : "
        f"{facturas_10_mas:,} "
        f"({porcentaje_10_mas:.2f}%)"
    )

    # =======================================================
    # 6.6 TOP 10 FACTURAS
    # =======================================================

    top_facturas = (
        basket_size
        .sort_values(
            "Basket_Size",
            ascending=False
        )
        .head(10)
    )

    print("\n6.3 TOP 10 FACTURAS POR BASKET SIZE")
    print("-" * 70)

    print(
        top_facturas.to_string(
            index=False
        )
    )

    # =======================================================
    # 6.7 DISTRIBUCIÓN POR RANGOS
    # =======================================================

    bins = [
        0,
        1,
        2,
        5,
        10,
        20,
        50,
        float("inf")
    ]

    labels = [
        "1 producto",
        "2 productos",
        "3-5 productos",
        "6-10 productos",
        "11-20 productos",
        "21-50 productos",
        "Más de 50"
    ]

    basket_size["Rango"] = pd.cut(
        basket_size["Basket_Size"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    distribucion_basket = (
        basket_size["Rango"]
        .value_counts(
            sort=False
        )
        .reset_index()
    )

    distribucion_basket.columns = [
        "Rango",
        "Facturas"
    ]

    distribucion_basket[
        "Porcentaje"
    ] = (
        distribucion_basket["Facturas"] /
        numero_facturas *
        100
    )

    print("\n6.4 DISTRIBUCIÓN POR RANGO")
    print("-" * 70)

    print(
        distribucion_basket.to_string(
            index=False
        )
    )

    # =======================================================
    # 6.8 GRÁFICOS
    # =======================================================

    if generar_graficos:

        # ---------------------------------------------------
        # Gráfico 1 - Distribución general
        # ---------------------------------------------------

        plt.figure(figsize=(10, 5))

        plt.hist(
            basket_size["Basket_Size"],
            bins=40,
            edgecolor="black"
        )

        plt.axvline(
            promedio,
            linestyle="--",
            label=f"Media = {promedio:.2f}"
        )

        plt.axvline(
            mediana,
            linestyle=":",
            label=f"Mediana = {mediana:.0f}"
        )

        plt.title(
            "Distribución del Tamaño de la Cesta"
        )

        plt.xlabel(
            "Número de productos diferentes por factura"
        )

        plt.ylabel(
            "Número de facturas"
        )

        plt.legend()

        plt.tight_layout()
        plt.show()

        # ---------------------------------------------------
        # Gráfico 2 - Distribución hasta P99
        # ---------------------------------------------------

        plt.figure(figsize=(10, 5))

        plt.hist(
            basket_size[
                basket_size["Basket_Size"] <= p99
            ]["Basket_Size"],
            bins=30,
            edgecolor="black"
        )

        plt.axvline(
            p99,
            linestyle="--",
            label=f"P99 = {p99:.0f}"
        )

        plt.title(
            "Distribución del Basket Size - hasta P99"
        )

        plt.xlabel(
            "Número de productos"
        )

        plt.ylabel(
            "Número de facturas"
        )

        plt.legend()

        plt.tight_layout()
        plt.show()

        # ---------------------------------------------------
        # Gráfico 3 - Boxplot
        # ---------------------------------------------------

        plt.figure(figsize=(12, 2.5))

        plt.boxplot(
            basket_size["Basket_Size"],
            vert=False
        )

        plt.title(
            "Boxplot del Tamaño de la Cesta"
        )

        plt.xlabel(
            "Número de productos diferentes"
        )

        plt.tight_layout()
        plt.show()

        # ---------------------------------------------------
        # Gráfico 4 - Rangos de Basket Size
        # ---------------------------------------------------

        plt.figure(figsize=(10, 5))

        plt.bar(
            distribucion_basket["Rango"].astype(str),
            distribucion_basket["Facturas"]
        )

        plt.title(
            "Distribución de Facturas por Tamaño de Cesta"
        )

        plt.xlabel(
            "Rango de productos por factura"
        )

        plt.ylabel(
            "Número de facturas"
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 6.9 RESUMEN
    # =======================================================

    resumen_basket = pd.DataFrame({

        "Indicador": [

            "Número de facturas",

            "Basket Size promedio",

            "Mediana",

            "Mínimo",

            "Máximo",

            "P90",

            "P95",

            "P99",

            "% facturas con 1 producto",

            "% facturas con 2+ productos",

            "% facturas con 5+ productos",

            "% facturas con 10+ productos"

        ],

        "Valor": [

            numero_facturas,

            round(promedio, 2),

            int(mediana),

            int(minimo),

            int(maximo),

            round(p90, 2),

            round(p95, 2),

            round(p99, 2),

            round(porcentaje_1, 2),

            round(porcentaje_2_mas, 2),

            round(porcentaje_5_mas, 2),

            round(porcentaje_10_mas, 2)

        ]

    })

    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS BASKET SIZE")
    print("=" * 70)

    print(
        resumen_basket.to_string(
            index=False
        )
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return {
        "basket_size": basket_size,
        "resumen_basket": resumen_basket,
        "distribucion_basket": distribucion_basket,
        "top_facturas": top_facturas
    }


# ===========================================================
# 7. ANÁLISIS BIVARIADO
# ===========================================================

def analizar_bivariado(df_clean, generar_graficos=True):
    """
    Realiza el análisis bivariado del dataset limpio.

    Analiza relaciones entre:

    - Producto y Quantity
    - Producto y Total
    - País y Total
    - Cliente y frecuencia de compra
    - Quantity y Price
    - Quantity y Total
    - Price y Total
    - Frecuencia de compra y ventas
    - Coocurrencia de productos

    Retorna los principales resultados para continuar
    con el EDA y el análisis de recomendación.
    """

    import matplotlib.pyplot as plt
    import numpy as np

    print("\n" + "=" * 70)
    print("7. ANÁLISIS BIVARIADO")
    print("=" * 70)

    # =======================================================
    # 7.1 VALIDACIÓN
    # =======================================================

    columnas_requeridas = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "Price",
        "CustomerID",
        "Country"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df_clean.columns
    ]

    if columnas_faltantes:

        raise KeyError(
            f"Faltan columnas requeridas: "
            f"{columnas_faltantes}"
        )

    # =======================================================
    # 7.2 COPIA DEL DATASET
    # =======================================================

    df_analisis = df_clean.copy()

    # Limpiar descripción
    df_analisis["Description"] = (
        df_analisis["Description"]
        .astype("string")
        .str.strip()
    )

    # Crear Total
    if "Total" not in df_analisis.columns:

        df_analisis["Total"] = (
            df_analisis["Quantity"] *
            df_analisis["Price"]
        )

    print(
        f"\nRegistros analizados: "
        f"{len(df_analisis):,}"
    )

    # =======================================================
    # 7.3 PRODUCTO VS QUANTITY
    # =======================================================

    print("\n7.1 PRODUCTOS VS CANTIDAD VENDIDA")
    print("-" * 70)

    top_productos_quantity = (
        df_analisis
        .groupby("Description")["Quantity"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print(
        top_productos_quantity
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 7))

        top_productos_quantity.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 20 Productos por Cantidad Vendida"
        )

        plt.xlabel(
            "Cantidad de unidades vendidas"
        )

        plt.ylabel(
            "Producto"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.4 PRODUCTO VS FACTURACIÓN
    # =======================================================

    print("\n7.2 PRODUCTOS VS FACTURACIÓN")
    print("-" * 70)

    ventas_producto = (
        df_analisis
        .groupby("Description")["Total"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print(
        ventas_producto
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 7))

        ventas_producto.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 20 Productos por Facturación"
        )

        plt.xlabel(
            "Ventas"
        )

        plt.ylabel(
            "Producto"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.5 COMPARACIÓN: VOLUMEN VS FACTURACIÓN
    # =======================================================

    print("\n7.3 VOLUMEN VS FACTURACIÓN")
    print("-" * 70)

    producto_resumen = (
        df_analisis
        .groupby("Description")
        .agg(
            Quantity=("Quantity", "sum"),
            Ventas=("Total", "sum"),
            Facturas=("Invoice", "nunique")
        )
        .sort_values(
            "Ventas",
            ascending=False
        )
        .head(20)
    )

    producto_resumen["Precio_Promedio"] = (
        producto_resumen["Ventas"] /
        producto_resumen["Quantity"]
    )

    print(
        producto_resumen
        .head(10)
        .to_string()
    )

    # -------------------------------------------------------
    # Gráfico de dispersión
    # -------------------------------------------------------

    if generar_graficos:

        plt.figure(figsize=(10, 6))

        plt.scatter(
            producto_resumen["Quantity"],
            producto_resumen["Ventas"]
        )

        plt.title(
            "Relación entre Cantidad Vendida y Facturación"
        )

        plt.xlabel(
            "Cantidad vendida"
        )

        plt.ylabel(
            "Facturación"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.6 PAÍS VS FACTURACIÓN
    # =======================================================

    print("\n7.4 PAÍSES VS FACTURACIÓN")
    print("-" * 70)

    ventas_pais = (
        df_analisis
        .groupby("Country")["Total"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(15)
    )

    print(
        ventas_pais
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 6))

        ventas_pais.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 15 Países por Facturación"
        )

        plt.xlabel(
            "Facturación"
        )

        plt.ylabel(
            "País"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.7 CLIENTE VS FRECUENCIA
    # =======================================================

    print("\n7.5 CLIENTES VS FRECUENCIA DE COMPRA")
    print("-" * 70)

    clientes_frecuencia = (
        df_analisis
        .groupby("CustomerID")["Invoice"]
        .nunique()
        .sort_values(
            ascending=False
        )
        .head(20)
    )

    print(
        clientes_frecuencia
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 6))

        clientes_frecuencia.sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 20 Clientes por Número de Compras"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "CustomerID"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.8 QUANTITY VS PRICE
    # =======================================================

    print("\n7.6 QUANTITY VS PRICE")
    print("-" * 70)

    correlacion_quantity_price = (
        df_analisis[
            ["Quantity", "Price"]
        ]
        .corr()
        .loc[
            "Quantity",
            "Price"
        ]
    )

    print(
        f"Correlación Quantity-Price: "
        f"{correlacion_quantity_price:.4f}"
    )

    if generar_graficos:

        # Para evitar que valores extremos dominen
        # la visualización

        q99_quantity = (
            df_analisis["Quantity"]
            .quantile(0.99)
        )

        q99_price = (
            df_analisis["Price"]
            .quantile(0.99)
        )

        df_scatter = df_analisis[
            (df_analisis["Quantity"] <= q99_quantity) &
            (df_analisis["Price"] <= q99_price)
        ]

        plt.figure(figsize=(10, 6))

        plt.scatter(
            df_scatter["Quantity"],
            df_scatter["Price"],
            alpha=0.3
        )

        plt.title(
            "Relación entre Quantity y Price"
        )

        plt.xlabel(
            "Cantidad"
        )

        plt.ylabel(
            "Precio"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.9 QUANTITY VS TOTAL
    # =======================================================

    print("\n7.7 QUANTITY VS TOTAL")
    print("-" * 70)

    correlacion_quantity_total = (
        df_analisis[
            ["Quantity", "Total"]
        ]
        .corr()
        .loc[
            "Quantity",
            "Total"
        ]
    )

    print(
        f"Correlación Quantity-Total: "
        f"{correlacion_quantity_total:.4f}"
    )

    if generar_graficos:

        q99_quantity = (
            df_analisis["Quantity"]
            .quantile(0.99)
        )

        q99_total = (
            df_analisis["Total"]
            .quantile(0.99)
        )

        df_scatter = df_analisis[
            (df_analisis["Quantity"] <= q99_quantity) &
            (df_analisis["Total"] <= q99_total)
        ]

        plt.figure(figsize=(10, 6))

        plt.scatter(
            df_scatter["Quantity"],
            df_scatter["Total"],
            alpha=0.3
        )

        plt.title(
            "Relación entre Quantity y Total"
        )

        plt.xlabel(
            "Cantidad"
        )

        plt.ylabel(
            "Valor de venta"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.10 PRICE VS TOTAL
    # =======================================================

    print("\n7.8 PRICE VS TOTAL")
    print("-" * 70)

    correlacion_price_total = (
        df_analisis[
            ["Price", "Total"]
        ]
        .corr()
        .loc[
            "Price",
            "Total"
        ]
    )

    print(
        f"Correlación Price-Total: "
        f"{correlacion_price_total:.4f}"
    )

    if generar_graficos:

        q99_price = (
            df_analisis["Price"]
            .quantile(0.99)
        )

        q99_total = (
            df_analisis["Total"]
            .quantile(0.99)
        )

        df_scatter = df_analisis[
            (df_analisis["Price"] <= q99_price) &
            (df_analisis["Total"] <= q99_total)
        ]

        plt.figure(figsize=(10, 6))

        plt.scatter(
            df_scatter["Price"],
            df_scatter["Total"],
            alpha=0.3
        )

        plt.title(
            "Relación entre Price y Total"
        )

        plt.xlabel(
            "Precio"
        )

        plt.ylabel(
            "Valor de venta"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.11 MATRIZ DE CORRELACIÓN
    # =======================================================

    print("\n7.9 MATRIZ DE CORRELACIÓN")
    print("-" * 70)

    matriz_correlacion = (
        df_analisis[
            [
                "Quantity",
                "Price",
                "Total"
            ]
        ]
        .corr()
    )

    print(
        matriz_correlacion.to_string()
    )

    if generar_graficos:

        # Usamos matplotlib para evitar depender
        # de seaborn.

        plt.figure(figsize=(7, 6))

        plt.imshow(
            matriz_correlacion,
            interpolation="nearest"
        )

        plt.colorbar()

        plt.xticks(
            range(
                len(matriz_correlacion.columns)
            ),
            matriz_correlacion.columns
        )

        plt.yticks(
            range(
                len(matriz_correlacion.columns)
            ),
            matriz_correlacion.columns
        )

        plt.title(
            "Matriz de Correlación"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.12 CLIENTE VS FACTURACIÓN
    # =======================================================

    print("\n7.10 CLIENTES VS FACTURACIÓN")
    print("-" * 70)

    clientes_resumen = (
        df_analisis
        .groupby("CustomerID")
        .agg(
            Facturas=("Invoice", "nunique"),
            Ventas=("Total", "sum"),
            Productos=("StockCode", "nunique")
        )
    )

    clientes_resumen["Ticket_Promedio"] = (
        clientes_resumen["Ventas"] /
        clientes_resumen["Facturas"]
    )

    clientes_top_ventas = (
        clientes_resumen
        .sort_values(
            "Ventas",
            ascending=False
        )
        .head(20)
    )

    print(
        clientes_top_ventas
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(10, 6))

        plt.scatter(
            clientes_resumen["Facturas"],
            clientes_resumen["Ventas"],
            alpha=0.3
        )

        plt.title(
            "Relación entre Frecuencia de Compra y Facturación"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "Facturación"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.13 COOCURRENCIA DE PRODUCTOS
    # =======================================================

    print("\n7.11 COOCURRENCIA DE PRODUCTOS")
    print("-" * 70)

    # Crear matriz binaria:
    # 1 = producto presente en la factura
    # 0 = producto ausente

    basket = (
        df_analisis
        .groupby(
            [
                "Invoice",
                "Description"
            ]
        )["Quantity"]
        .sum()
        .unstack(
            fill_value=0
        )
    )

    basket_binary = (
        basket > 0
    ).astype(int)

    # Top 20 productos

    top20_productos = (
        basket_binary
        .sum()
        .sort_values(
            ascending=False
        )
        .head(20)
        .index
    )

    basket_top20 = (
        basket_binary[
            top20_productos
        ]
    )

    # Coocurrencia

    coocurrencia = (
        basket_top20.T
        .dot(
            basket_top20
        )
    )

    matriz_coocurrencia = (
        coocurrencia
        .copy()
    )

    # Eliminar diagonal

    matriz = (
        matriz_coocurrencia
        .to_numpy(
            copy=True
        )
    )

    np.fill_diagonal(
        matriz,
        0
    )

    matriz_coocurrencia = pd.DataFrame(
        matriz,
        index=coocurrencia.index,
        columns=coocurrencia.columns
    )

    print(
        "\nMatriz de coocurrencia creada."
    )

    # -------------------------------------------------------
    # Pares de productos más frecuentes
    # -------------------------------------------------------

    pares = []

    productos = (
        matriz_coocurrencia
        .columns
        .tolist()
    )

    for i in range(
        len(productos)
    ):

        for j in range(
            i + 1,
            len(productos)
        ):

            producto_a = productos[i]
            producto_b = productos[j]

            frecuencia = (
                matriz_coocurrencia
                .loc[
                    producto_a,
                    producto_b
                ]
            )

            pares.append(
                (
                    producto_a,
                    producto_b,
                    frecuencia
                )
            )

    pares_productos = pd.DataFrame(
        pares,
        columns=[
            "Producto_A",
            "Producto_B",
            "Coocurrencias"
        ]
    )

    pares_productos = (
        pares_productos
        .sort_values(
            "Coocurrencias",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    print(
        "\nTop 20 pares de productos:"
    )

    print(
        pares_productos
        .head(20)
        .to_string(
            index=False
        )
    )

    # -------------------------------------------------------
    # Heatmap
    # -------------------------------------------------------

    if generar_graficos:

        plt.figure(
            figsize=(12, 10)
        )

        plt.imshow(
            matriz_coocurrencia,
            aspect="auto"
        )

        plt.colorbar(
            label="Número de facturas"
        )

        plt.xticks(
            range(
                len(
                    matriz_coocurrencia.columns
                )
            ),
            matriz_coocurrencia.columns,
            rotation=90
        )

        plt.yticks(
            range(
                len(
                    matriz_coocurrencia.index
                )
            ),
            matriz_coocurrencia.index
        )

        plt.title(
            "Matriz de Coocurrencia - Top 20 Productos"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 7.14 RESUMEN
    # =======================================================

    resumen_bivariado = pd.DataFrame({

        "Indicador": [

            "Productos analizados",

            "Países analizados",

            "Clientes analizados",

            "Facturas analizadas",

            "Correlación Quantity-Price",

            "Correlación Quantity-Total",

            "Correlación Price-Total",

            "Producto más vendido",

            "Producto con mayor facturación",

            "País con mayor facturación"

        ],

        "Valor": [

            df_analisis[
                "StockCode"
            ].nunique(),

            df_analisis[
                "Country"
            ].nunique(),

            df_analisis[
                "CustomerID"
            ].nunique(),

            df_analisis[
                "Invoice"
            ].nunique(),

            round(
                correlacion_quantity_price,
                4
            ),

            round(
                correlacion_quantity_total,
                4
            ),

            round(
                correlacion_price_total,
                4
            ),

            top_productos_quantity.index[0],

            ventas_producto.index[0],

            ventas_pais.index[0]

        ]

    })

    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS BIVARIADO")
    print("=" * 70)

    print(
        resumen_bivariado.to_string(
            index=False
        )
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return {

        "top_productos_quantity":
            top_productos_quantity,

        "ventas_producto":
            ventas_producto,

        "producto_resumen":
            producto_resumen,

        "ventas_pais":
            ventas_pais,

        "clientes_frecuencia":
            clientes_frecuencia,

        "clientes_resumen":
            clientes_resumen,

        "matriz_correlacion":
            matriz_correlacion,

        "basket":
            basket,

        "matriz_coocurrencia":
            matriz_coocurrencia,

        "pares_productos":
            pares_productos,

        "resumen_bivariado":
            resumen_bivariado
    }


# ===========================================================
# 8. ANÁLISIS TEMPORAL
# ===========================================================

def analizar_temporal(df_clean, generar_graficos=True):
    """
    Realiza el análisis temporal del dataset limpio.

    Analiza:

    - Evolución diaria de ventas
    - Evolución mensual de ventas
    - Ventas por año
    - Ventas por mes
    - Facturas por mes
    - Ticket promedio por mes
    - Ventas por día de la semana
    - Facturas por día
    - Ticket promedio por día
    - Ventas por hora
    - Facturas por hora
    - Ticket promedio por hora
    - Relación día de semana vs hora
    - Estacionalidad mensual
    - Período de mayor y menor facturación

    Variables requeridas:

    - Invoice
    - InvoiceDate
    - Quantity
    - Price

    Retorna un diccionario con los principales
    resultados del análisis temporal.
    """

    import matplotlib.pyplot as plt
    import numpy as np

    print("\n" + "=" * 70)
    print("8. ANÁLISIS TEMPORAL")
    print("=" * 70)

    # =======================================================
    # 8.1 VALIDACIÓN
    # =======================================================

    columnas_requeridas = [
        "Invoice",
        "InvoiceDate",
        "Quantity",
        "Price"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df_clean.columns
    ]

    if columnas_faltantes:

        raise KeyError(
            f"Faltan columnas requeridas: "
            f"{columnas_faltantes}"
        )

    # =======================================================
    # 8.2 COPIA DEL DATASET
    # =======================================================

    df_analisis = df_clean.copy()

    # Convertir fecha
    df_analisis["InvoiceDate"] = pd.to_datetime(
        df_analisis["InvoiceDate"],
        errors="coerce"
    )

    # Eliminar fechas no válidas
    fechas_invalidas = (
        df_analisis["InvoiceDate"].isna().sum()
    )

    if fechas_invalidas > 0:

        print(
            f"\nFechas inválidas eliminadas del análisis: "
            f"{fechas_invalidas:,}"
        )

        df_analisis = (
            df_analisis[
                df_analisis["InvoiceDate"].notna()
            ]
            .copy()
        )

    # =======================================================
    # 8.3 VARIABLES TEMPORALES
    # =======================================================

    df_analisis["Año"] = (
        df_analisis["InvoiceDate"].dt.year
    )

    df_analisis["Mes"] = (
        df_analisis["InvoiceDate"].dt.month
    )

    df_analisis["Nombre_Mes"] = (
        df_analisis["InvoiceDate"]
        .dt.month_name()
    )

    df_analisis["Dia"] = (
        df_analisis["InvoiceDate"].dt.day
    )

    df_analisis["Dia_Semana"] = (
        df_analisis["InvoiceDate"]
        .dt.day_name()
    )

    df_analisis["Numero_Dia_Semana"] = (
        df_analisis["InvoiceDate"]
        .dt.dayofweek
    )

    df_analisis["Hora"] = (
        df_analisis["InvoiceDate"].dt.hour
    )

    # Fecha sin hora
    df_analisis["Fecha"] = (
        df_analisis["InvoiceDate"].dt.date
    )

    # Crear Total
    if "Total" not in df_analisis.columns:

        df_analisis["Total"] = (
            df_analisis["Quantity"] *
            df_analisis["Price"]
        )

    print(
        f"\nRegistros analizados: "
        f"{len(df_analisis):,}"
    )

    # =======================================================
    # 8.4 PERÍODO ANALIZADO
    # =======================================================

    fecha_inicio = (
        df_analisis["InvoiceDate"].min()
    )

    fecha_fin = (
        df_analisis["InvoiceDate"].max()
    )

    años = (
        df_analisis["Año"]
        .nunique()
    )

    meses = (
        df_analisis["Mes"]
        .nunique()
    )

    print("\n8.1 PERÍODO ANALIZADO")
    print("-" * 70)

    print(
        f"Fecha inicial : {fecha_inicio}"
    )

    print(
        f"Fecha final   : {fecha_fin}"
    )

    print(
        f"Años          : {años}"
    )

    print(
        f"Meses         : {meses}"
    )

    # =======================================================
    # 8.5 EVOLUCIÓN DIARIA
    # =======================================================

    print("\n8.2 EVOLUCIÓN DIARIA")
    print("-" * 70)

    ventas_diarias = (
        df_analisis
        .groupby("Fecha")
        .agg(
            Ventas=("Total", "sum"),
            Facturas=("Invoice", "nunique")
        )
    )

    ventas_diarias["Ticket_Promedio"] = (
        ventas_diarias["Ventas"] /
        ventas_diarias["Facturas"]
    )

    fecha_mayor_venta = (
        ventas_diarias["Ventas"]
        .idxmax()
    )

    fecha_menor_venta = (
        ventas_diarias["Ventas"]
        .idxmin()
    )

    print(
        f"Mayor venta diaria : "
        f"{fecha_mayor_venta}"
    )

    print(
        f"Valor               : "
        f"{ventas_diarias.loc[fecha_mayor_venta, 'Ventas']:,.2f}"
    )

    print(
        f"\nMenor venta diaria : "
        f"{fecha_menor_venta}"
    )

    print(
        f"Valor               : "
        f"{ventas_diarias.loc[fecha_menor_venta, 'Ventas']:,.2f}"
    )

    if generar_graficos:

        plt.figure(figsize=(14, 5))

        plt.plot(
            ventas_diarias.index,
            ventas_diarias["Ventas"]
        )

        plt.title(
            "Evolución Diaria de las Ventas"
        )

        plt.xlabel("Fecha")
        plt.ylabel("Ventas")

        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.6 EVOLUCIÓN MENSUAL
    # =======================================================

    print("\n8.3 EVOLUCIÓN MENSUAL")
    print("-" * 70)

    ventas_mensuales = (
        df_analisis
        .set_index("InvoiceDate")
        .resample("ME")
        .agg(
            Ventas=("Total", "sum"),
            Facturas=("Invoice", "nunique")
        )
    )

    ventas_mensuales["Ticket_Promedio"] = (
        ventas_mensuales["Ventas"] /
        ventas_mensuales["Facturas"]
    )

    # Variación mensual

    ventas_mensuales["Variacion_%"] = (
        ventas_mensuales["Ventas"]
        .pct_change()
        * 100
    )

    print(
        ventas_mensuales
        .tail(12)
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(14, 6))

        plt.plot(
            ventas_mensuales.index,
            ventas_mensuales["Ventas"],
            marker="o"
        )

        plt.title(
            "Evolución Mensual de las Ventas"
        )

        plt.xlabel("Mes")
        plt.ylabel("Ventas")

        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.7 VENTAS POR AÑO
    # =======================================================

    print("\n8.4 VENTAS POR AÑO")
    print("-" * 70)

    ventas_anio = (
        df_analisis
        .groupby("Año")
        .agg(
            Ventas=("Total", "sum"),
            Facturas=("Invoice", "nunique")
        )
    )

    ventas_anio["Ticket_Promedio"] = (
        ventas_anio["Ventas"] /
        ventas_anio["Facturas"]
    )

    print(
        ventas_anio.to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(8, 5))

        plt.bar(
            ventas_anio.index.astype(str),
            ventas_anio["Ventas"]
        )

        plt.title(
            "Ventas por Año"
        )

        plt.xlabel("Año")
        plt.ylabel("Ventas")

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.8 ESTACIONALIDAD MENSUAL
    # =======================================================

    print("\n8.5 ESTACIONALIDAD MENSUAL")
    print("-" * 70)

    orden_meses = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"
    ]

    ventas_mes = (
        df_analisis
        .groupby(
            "Nombre_Mes"
        )["Total"]
        .sum()
        .reindex(
            orden_meses
        )
    )

    facturas_mes = (
        df_analisis
        .groupby(
            "Nombre_Mes"
        )["Invoice"]
        .nunique()
        .reindex(
            orden_meses
        )
    )

    ticket_mes = (
        ventas_mes /
        facturas_mes
    )

    estacionalidad = pd.DataFrame({
        "Ventas": ventas_mes,
        "Facturas": facturas_mes,
        "Ticket_Promedio": ticket_mes
    })

    print(
        estacionalidad.to_string()
    )

    mes_mayor_venta = (
        ventas_mes.idxmax()
    )

    mes_menor_venta = (
        ventas_mes.idxmin()
    )

    print(
        f"\nMes con mayor facturación: "
        f"{mes_mayor_venta}"
    )

    print(
        f"Mes con menor facturación: "
        f"{mes_menor_venta}"
    )

    if generar_graficos:

        plt.figure(figsize=(12, 5))

        plt.bar(
            ventas_mes.index,
            ventas_mes.values
        )

        plt.title(
            "Estacionalidad de las Ventas por Mes"
        )

        plt.xlabel("Mes")
        plt.ylabel("Ventas")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

        # Facturas

        plt.figure(figsize=(12, 5))

        plt.bar(
            facturas_mes.index,
            facturas_mes.values
        )

        plt.title(
            "Número de Facturas por Mes"
        )

        plt.xlabel("Mes")
        plt.ylabel("Facturas")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

        # Ticket promedio

        plt.figure(figsize=(12, 5))

        plt.plot(
            ticket_mes.index,
            ticket_mes.values,
            marker="o"
        )

        plt.title(
            "Ticket Promedio por Mes"
        )

        plt.xlabel("Mes")
        plt.ylabel("Ticket promedio")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.9 DÍA DE LA SEMANA
    # =======================================================

    print("\n8.6 COMPORTAMIENTO POR DÍA DE LA SEMANA")
    print("-" * 70)

    orden_dias = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    ventas_dia = (
        df_analisis
        .groupby(
            "Dia_Semana"
        )["Total"]
        .sum()
        .reindex(
            orden_dias
        )
    )

    facturas_dia = (
        df_analisis
        .groupby(
            "Dia_Semana"
        )["Invoice"]
        .nunique()
        .reindex(
            orden_dias
        )
    )

    ticket_dia = (
        ventas_dia /
        facturas_dia
    )

    comportamiento_dia = pd.DataFrame({
        "Ventas": ventas_dia,
        "Facturas": facturas_dia,
        "Ticket_Promedio": ticket_dia
    })

    print(
        comportamiento_dia.to_string()
    )

    dia_mayor_venta = (
        ventas_dia.idxmax()
    )

    dia_mayor_facturas = (
        facturas_dia.idxmax()
    )

    print(
        f"\nDía con mayor facturación: "
        f"{dia_mayor_venta}"
    )

    print(
        f"Día con mayor número de facturas: "
        f"{dia_mayor_facturas}"
    )

    if generar_graficos:

        plt.figure(figsize=(10, 5))

        plt.bar(
            ventas_dia.index,
            ventas_dia.values
        )

        plt.title(
            "Ventas por Día de la Semana"
        )

        plt.xlabel("Día")
        plt.ylabel("Ventas")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

        # Facturas

        plt.figure(figsize=(10, 5))

        plt.bar(
            facturas_dia.index,
            facturas_dia.values
        )

        plt.title(
            "Facturas por Día de la Semana"
        )

        plt.xlabel("Día")
        plt.ylabel("Número de facturas")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

        # Ticket

        plt.figure(figsize=(10, 5))

        plt.plot(
            ticket_dia.index,
            ticket_dia.values,
            marker="o"
        )

        plt.title(
            "Ticket Promedio por Día de la Semana"
        )

        plt.xlabel("Día")
        plt.ylabel("Ticket promedio")

        plt.xticks(
            rotation=45
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.10 HORA DEL DÍA
    # =======================================================

    print("\n8.7 COMPORTAMIENTO POR HORA")
    print("-" * 70)

    ventas_hora = (
        df_analisis
        .groupby("Hora")["Total"]
        .sum()
    )

    facturas_hora = (
        df_analisis
        .groupby("Hora")["Invoice"]
        .nunique()
    )

    ticket_hora = (
        ventas_hora /
        facturas_hora
    )

    comportamiento_hora = pd.DataFrame({
        "Ventas": ventas_hora,
        "Facturas": facturas_hora,
        "Ticket_Promedio": ticket_hora
    })

    print(
        comportamiento_hora.to_string()
    )

    hora_mayor_venta = (
        ventas_hora.idxmax()
    )

    hora_mayor_facturas = (
        facturas_hora.idxmax()
    )

    print(
        f"\nHora con mayor facturación: "
        f"{hora_mayor_venta}:00"
    )

    print(
        f"Hora con mayor número de facturas: "
        f"{hora_mayor_facturas}:00"
    )

    if generar_graficos:

        plt.figure(figsize=(12, 5))

        plt.plot(
            ventas_hora.index,
            ventas_hora.values,
            marker="o"
        )

        plt.title(
            "Ventas por Hora del Día"
        )

        plt.xlabel("Hora")
        plt.ylabel("Ventas")

        plt.grid(
            True,
            alpha=0.3
        )

        plt.tight_layout()
        plt.show()

        # Facturas

        plt.figure(figsize=(12, 5))

        plt.plot(
            facturas_hora.index,
            facturas_hora.values,
            marker="o"
        )

        plt.title(
            "Número de Facturas por Hora"
        )

        plt.xlabel("Hora")
        plt.ylabel("Facturas")

        plt.grid(
            True,
            alpha=0.3
        )

        plt.tight_layout()
        plt.show()

        # Ticket

        plt.figure(figsize=(12, 5))

        plt.plot(
            ticket_hora.index,
            ticket_hora.values,
            marker="o"
        )

        plt.title(
            "Ticket Promedio por Hora"
        )

        plt.xlabel("Hora")
        plt.ylabel("Ticket promedio")

        plt.grid(
            True,
            alpha=0.3
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.11 DÍA VS HORA
    # =======================================================

    print("\n8.8 MAPA DE ACTIVIDAD: DÍA VS HORA")
    print("-" * 70)

    heat_ventas = (
        df_analisis
        .pivot_table(
            values="Total",
            index="Dia_Semana",
            columns="Hora",
            aggfunc="sum",
            fill_value=0
        )
        .reindex(
            orden_dias
        )
    )

    heat_facturas = (
        df_analisis
        .pivot_table(
            values="Invoice",
            index="Dia_Semana",
            columns="Hora",
            aggfunc="nunique",
            fill_value=0
        )
        .reindex(
            orden_dias
        )
    )

    # Encontrar combinación máxima

    max_pos = np.unravel_index(
        np.argmax(
            heat_ventas.values
        ),
        heat_ventas.shape
    )

    dia_max_heat = (
        heat_ventas.index[
            max_pos[0]
        ]
    )

    hora_max_heat = (
        heat_ventas.columns[
            max_pos[1]
        ]
    )

    print(
        f"Mayor concentración de ventas: "
        f"{dia_max_heat} a las "
        f"{hora_max_heat}:00"
    )

    if generar_graficos:

        # Mapa de calor de ventas

        plt.figure(figsize=(15, 6))

        plt.imshow(
            heat_ventas,
            aspect="auto"
        )

        plt.colorbar(
            label="Ventas"
        )

        plt.xticks(
            range(
                len(
                    heat_ventas.columns
                )
            ),
            heat_ventas.columns
        )

        plt.yticks(
            range(
                len(
                    heat_ventas.index
                )
            ),
            heat_ventas.index
        )

        plt.xlabel("Hora")
        plt.ylabel("Día de la semana")

        plt.title(
            "Mapa de Calor de Ventas por Día y Hora"
        )

        plt.tight_layout()
        plt.show()

        # Mapa de calor de facturas

        plt.figure(figsize=(15, 6))

        plt.imshow(
            heat_facturas,
            aspect="auto"
        )

        plt.colorbar(
            label="Facturas"
        )

        plt.xticks(
            range(
                len(
                    heat_facturas.columns
                )
            ),
            heat_facturas.columns
        )

        plt.yticks(
            range(
                len(
                    heat_facturas.index
                )
            ),
            heat_facturas.index
        )

        plt.xlabel("Hora")
        plt.ylabel("Día de la semana")

        plt.title(
            "Mapa de Calor de Facturas por Día y Hora"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 8.12 CONCENTRACIÓN TEMPORAL
    # =======================================================

    print("\n8.9 CONCENTRACIÓN TEMPORAL")
    print("-" * 70)

    ventas_total = (
        df_analisis["Total"].sum()
    )

    # Participación por mes

    participacion_mes = (
        ventas_mes /
        ventas_total *
        100
    )

    mes_mayor_participacion = (
        participacion_mes.idxmax()
    )

    print(
        f"Mes con mayor participación: "
        f"{mes_mayor_participacion}"
    )

    print(
        f"Participación: "
        f"{participacion_mes.max():.2f}%"
    )

    # =======================================================
    # 8.13 RESUMEN FINAL
    # =======================================================

    resumen_temporal = pd.DataFrame({

        "Indicador": [

            "Periodo analizado",

            "Número de años",

            "Número de meses",

            "Primer registro",

            "Último registro",

            "Facturas analizadas",

            "Ventas totales",

            "Mes con mayor facturación",

            "Mes con menor facturación",

            "Día con mayor facturación",

            "Día con mayor número de facturas",

            "Hora con mayor facturación",

            "Hora con mayor número de facturas",

            "Mayor combinación día-hora"

        ],

        "Valor": [

            (
                f"{fecha_inicio.date()} - "
                f"{fecha_fin.date()}"
            ),

            años,

            meses,

            fecha_inicio,

            fecha_fin,

            df_analisis[
                "Invoice"
            ].nunique(),

            round(
                ventas_total,
                2
            ),

            mes_mayor_venta,

            mes_menor_venta,

            dia_mayor_venta,

            dia_mayor_facturas,

            f"{hora_mayor_venta}:00",

            f"{hora_mayor_facturas}:00",

            (
                f"{dia_max_heat} "
                f"{hora_max_heat}:00"
            )

        ]

    })

    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS TEMPORAL")
    print("=" * 70)

    print(
        resumen_temporal.to_string(
            index=False
        )
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return {

        "df_temporal": df_analisis,

        "ventas_diarias":
            ventas_diarias,

        "ventas_mensuales":
            ventas_mensuales,

        "ventas_anio":
            ventas_anio,

        "estacionalidad":
            estacionalidad,

        "comportamiento_dia":
            comportamiento_dia,

        "comportamiento_hora":
            comportamiento_hora,

        "heat_ventas":
            heat_ventas,

        "heat_facturas":
            heat_facturas,

        "resumen_temporal":
            resumen_temporal

    }


# ===========================================================
# 9. ANÁLISIS DE CLIENTES
# ===========================================================

def analizar_clientes(df_clean, generar_graficos=True):
    """
    Realiza un análisis completo del comportamiento de clientes.

    Analiza:

    - Número de clientes únicos
    - Facturación por cliente
    - Frecuencia de compra
    - Ticket promedio
    - Productos diferentes comprados
    - Top clientes por facturación
    - Top clientes por frecuencia
    - Top clientes por ticket promedio
    - Distribución del gasto
    - Distribución de frecuencia
    - Relación frecuencia vs facturación
    - Concentración de ventas
    - Segmentación básica por comportamiento

    Retorna un diccionario con los principales resultados.
    """

    import matplotlib.pyplot as plt

    print("\n" + "=" * 70)
    print("9. ANÁLISIS DE CLIENTES")
    print("=" * 70)

    # =======================================================
    # 9.1 VALIDACIÓN
    # =======================================================

    columnas_requeridas = [
        "CustomerID",
        "Invoice",
        "StockCode",
        "Quantity",
        "Price"
    ]

    columnas_faltantes = [
        columna
        for columna in columnas_requeridas
        if columna not in df_clean.columns
    ]

    if columnas_faltantes:

        raise KeyError(
            f"Faltan columnas requeridas: "
            f"{columnas_faltantes}"
        )

    # =======================================================
    # 9.2 COPIA
    # =======================================================

    df_analisis = df_clean.copy()

    # Crear Total si no existe
    if "Total" not in df_analisis.columns:

        df_analisis["Total"] = (
            df_analisis["Quantity"] *
            df_analisis["Price"]
        )

    # Eliminar clientes sin identificación
    df_analisis = (
        df_analisis[
            df_analisis["CustomerID"].notna()
        ]
        .copy()
    )

    print(
        f"\nRegistros analizados: "
        f"{len(df_analisis):,}"
    )

    # =======================================================
    # 9.3 NÚMERO DE CLIENTES
    # =======================================================

    clientes_unicos = (
        df_analisis["CustomerID"]
        .nunique()
    )

    print("\n9.1 CLIENTES ÚNICOS")
    print("-" * 70)

    print(
        f"Clientes únicos: "
        f"{clientes_unicos:,}"
    )

    # =======================================================
    # 9.4 PERFIL DEL CLIENTE
    # =======================================================

    clientes = (
        df_analisis
        .groupby("CustomerID")
        .agg(
            Ventas=(
                "Total",
                "sum"
            ),

            Facturas=(
                "Invoice",
                "nunique"
            ),

            Productos_Diferentes=(
                "StockCode",
                "nunique"
            ),

            Unidades=(
                "Quantity",
                "sum"
            )
        )
    )

    clientes["Ticket_Promedio"] = (
        clientes["Ventas"] /
        clientes["Facturas"]
    )

    clientes["Unidades_Por_Factura"] = (
        clientes["Unidades"] /
        clientes["Facturas"]
    )

    # =======================================================
    # 9.5 ESTADÍSTICOS GENERALES
    # =======================================================

    print("\n9.2 PERFIL GENERAL DE CLIENTES")
    print("-" * 70)

    print(
        f"Ventas promedio por cliente: "
        f"€{clientes['Ventas'].mean():,.2f}"
    )

    print(
        f"Mediana de ventas por cliente: "
        f"€{clientes['Ventas'].median():,.2f}"
    )

    print(
        f"Compras promedio por cliente: "
        f"{clientes['Facturas'].mean():.2f}"
    )

    print(
        f"Ticket promedio: "
        f"€{clientes['Ticket_Promedio'].mean():,.2f}"
    )

    print(
        f"Productos diferentes promedio: "
        f"{clientes['Productos_Diferentes'].mean():.2f}"
    )

    # =======================================================
    # 9.6 TOP CLIENTES POR FACTURACIÓN
    # =======================================================

    top_ventas = (
        clientes
        .sort_values(
            "Ventas",
            ascending=False
        )
        .head(20)
    )

    print("\n9.3 TOP 20 CLIENTES POR FACTURACIÓN")
    print("-" * 70)

    print(
        top_ventas[
            [
                "Ventas",
                "Facturas",
                "Productos_Diferentes",
                "Ticket_Promedio"
            ]
        ]
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 7))

        top_ventas["Ventas"] \
            .sort_values() \
            .plot(
                kind="barh"
            )

        plt.title(
            "Top 20 Clientes por Facturación"
        )

        plt.xlabel(
            "Facturación"
        )

        plt.ylabel(
            "CustomerID"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.7 TOP CLIENTES POR FRECUENCIA
    # =======================================================

    top_frecuencia = (
        clientes
        .sort_values(
            "Facturas",
            ascending=False
        )
        .head(20)
    )

    print("\n9.4 TOP 20 CLIENTES POR FRECUENCIA")
    print("-" * 70)

    print(
        top_frecuencia[
            [
                "Facturas",
                "Ventas",
                "Ticket_Promedio"
            ]
        ]
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 7))

        top_frecuencia["Facturas"] \
            .sort_values() \
            .plot(
                kind="barh"
            )

        plt.title(
            "Top 20 Clientes por Número de Compras"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "CustomerID"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.8 TOP CLIENTES POR TICKET
    # =======================================================

    # Para evitar clientes con una sola factura
    # que puedan distorsionar el análisis,
    # utilizamos clientes con al menos 2 compras.

    clientes_recurrentes = clientes[
        clientes["Facturas"] >= 2
    ]

    top_ticket = (
        clientes_recurrentes
        .sort_values(
            "Ticket_Promedio",
            ascending=False
        )
        .head(20)
    )

    print("\n9.5 TOP 20 CLIENTES POR TICKET PROMEDIO")
    print("-" * 70)

    print(
        top_ticket[
            [
                "Ticket_Promedio",
                "Facturas",
                "Ventas"
            ]
        ]
        .to_string()
    )

    if generar_graficos:

        plt.figure(figsize=(12, 7))

        top_ticket[
            "Ticket_Promedio"
        ].sort_values().plot(
            kind="barh"
        )

        plt.title(
            "Top 20 Clientes por Ticket Promedio"
        )

        plt.xlabel(
            "Ticket promedio"
        )

        plt.ylabel(
            "CustomerID"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.9 DISTRIBUCIÓN DEL GASTO
    # =======================================================

    print("\n9.6 DISTRIBUCIÓN DEL GASTO POR CLIENTE")
    print("-" * 70)

    estadisticos_ventas = (
        clientes["Ventas"]
        .describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
                0.90,
                0.95,
                0.99
            ]
        )
    )

    print(
        estadisticos_ventas.to_string()
    )

    if generar_graficos:

        p99_ventas = (
            clientes["Ventas"]
            .quantile(0.99)
        )

        plt.figure(figsize=(10, 5))

        plt.hist(
            clientes[
                clientes["Ventas"] <= p99_ventas
            ]["Ventas"],
            bins=40,
            edgecolor="black"
        )

        plt.title(
            "Distribución del Gasto por Cliente - P99"
        )

        plt.xlabel(
            "Ventas por cliente"
        )

        plt.ylabel(
            "Número de clientes"
        )

        plt.tight_layout()
        plt.show()

        # Boxplot

        plt.figure(figsize=(12, 2.5))

        plt.boxplot(
            clientes["Ventas"],
            vert=False
        )

        plt.title(
            "Distribución del Gasto por Cliente"
        )

        plt.xlabel(
            "Ventas"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.10 FRECUENCIA DE COMPRA
    # =======================================================

    print("\n9.7 FRECUENCIA DE COMPRA")
    print("-" * 70)

    estadisticos_frecuencia = (
        clientes["Facturas"]
        .describe(
            percentiles=[
                0.25,
                0.50,
                0.75,
                0.90,
                0.95,
                0.99
            ]
        )
    )

    print(
        estadisticos_frecuencia.to_string()
    )

    if generar_graficos:

        p99_frecuencia = (
            clientes["Facturas"]
            .quantile(0.99)
        )

        plt.figure(figsize=(10, 5))

        plt.hist(
            clientes[
                clientes["Facturas"] <= p99_frecuencia
            ]["Facturas"],
            bins=30,
            edgecolor="black"
        )

        plt.title(
            "Distribución de la Frecuencia de Compra - P99"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "Número de clientes"
        )

        plt.tight_layout()
        plt.show()

        # Boxplot

        plt.figure(figsize=(12, 2.5))

        plt.boxplot(
            clientes["Facturas"],
            vert=False
        )

        plt.title(
            "Distribución de la Frecuencia de Compra"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.11 FRECUENCIA VS FACTURACIÓN
    # =======================================================

    print("\n9.8 FRECUENCIA VS FACTURACIÓN")
    print("-" * 70)

    correlacion = (
        clientes[
            [
                "Facturas",
                "Ventas"
            ]
        ]
        .corr()
        .loc[
            "Facturas",
            "Ventas"
        ]
    )

    print(
        f"Correlación entre frecuencia y ventas: "
        f"{correlacion:.4f}"
    )

    if generar_graficos:

        p99_facturas = (
            clientes["Facturas"]
            .quantile(0.99)
        )

        p99_ventas = (
            clientes["Ventas"]
            .quantile(0.99)
        )

        clientes_scatter = clientes[
            (clientes["Facturas"] <= p99_facturas) &
            (clientes["Ventas"] <= p99_ventas)
        ]

        plt.figure(figsize=(10, 6))

        plt.scatter(
            clientes_scatter["Facturas"],
            clientes_scatter["Ventas"],
            alpha=0.4
        )

        plt.title(
            "Relación entre Frecuencia de Compra y Facturación"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "Facturación"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.12 FRECUENCIA VS TICKET
    # =======================================================

    correlacion_ticket = (
        clientes[
            [
                "Facturas",
                "Ticket_Promedio"
            ]
        ]
        .corr()
        .loc[
            "Facturas",
            "Ticket_Promedio"
        ]
    )

    print(
        f"Correlación frecuencia-ticket: "
        f"{correlacion_ticket:.4f}"
    )

    if generar_graficos:

        p99_facturas = (
            clientes["Facturas"]
            .quantile(0.99)
        )

        p99_ticket = (
            clientes["Ticket_Promedio"]
            .quantile(0.99)
        )

        clientes_scatter = clientes[
            (clientes["Facturas"] <= p99_facturas) &
            (
                clientes["Ticket_Promedio"]
                <= p99_ticket
            )
        ]

        plt.figure(figsize=(10, 6))

        plt.scatter(
            clientes_scatter["Facturas"],
            clientes_scatter["Ticket_Promedio"],
            alpha=0.4
        )

        plt.title(
            "Relación entre Frecuencia y Ticket Promedio"
        )

        plt.xlabel(
            "Número de facturas"
        )

        plt.ylabel(
            "Ticket promedio"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.13 CONCENTRACIÓN DE VENTAS
    # =======================================================

    print("\n9.9 CONCENTRACIÓN DE VENTAS")
    print("-" * 70)

    clientes_ordenados = (
        clientes
        .sort_values(
            "Ventas",
            ascending=False
        )
        .copy()
    )

    ventas_total = (
        clientes_ordenados["Ventas"]
        .sum()
    )

    clientes_ordenados[
        "Participacion"
    ] = (
        clientes_ordenados["Ventas"] /
        ventas_total *
        100
    )

    clientes_ordenados[
        "Participacion_Acumulada"
    ] = (
        clientes_ordenados["Participacion"]
        .cumsum()
    )

    top_10_participacion = (
        clientes_ordenados
        .head(10)["Ventas"]
        .sum()
        /
        ventas_total
        *
        100
    )

    top_20_participacion = (
        clientes_ordenados
        .head(20)["Ventas"]
        .sum()
        /
        ventas_total
        *
        100
    )

    top_10_pct_clientes = (
        int(
            np.ceil(
                clientes_unicos * 0.10
            )
        )
    )

    ventas_top_10_pct = (
        clientes_ordenados
        .head(
            top_10_pct_clientes
        )["Ventas"]
        .sum()
        /
        ventas_total
        *
        100
    )

    print(
        f"Top 10 clientes concentran: "
        f"{top_10_participacion:.2f}% de las ventas"
    )

    print(
        f"Top 20 clientes concentran: "
        f"{top_20_participacion:.2f}% de las ventas"
    )

    print(
        f"Top 10% de clientes concentran: "
        f"{ventas_top_10_pct:.2f}% de las ventas"
    )

    if generar_graficos:

        porcentaje_clientes = (
            np.arange(
                1,
                len(clientes_ordenados) + 1
            )
            /
            len(clientes_ordenados)
            *
            100
        )

        porcentaje_ventas = (
            clientes_ordenados[
                "Participacion_Acumulada"
            ]
        )

        plt.figure(figsize=(10, 6))

        plt.plot(
            porcentaje_clientes,
            porcentaje_ventas
        )

        plt.plot(
            [0, 100],
            [0, 100],
            linestyle="--"
        )

        plt.title(
            "Concentración Acumulada de Ventas por Cliente"
        )

        plt.xlabel(
            "% acumulado de clientes"
        )

        plt.ylabel(
            "% acumulado de ventas"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.14 SEGMENTACIÓN BÁSICA
    # =======================================================

    print("\n9.10 SEGMENTACIÓN BÁSICA DE CLIENTES")
    print("-" * 70)

    mediana_ventas = (
        clientes["Ventas"]
        .median()
    )

    mediana_frecuencia = (
        clientes["Facturas"]
        .median()
    )

    def clasificar_cliente(row):

        if (
            row["Ventas"] >= mediana_ventas
            and
            row["Facturas"] >= mediana_frecuencia
        ):

            return "Alto valor y frecuente"

        elif (
            row["Ventas"] >= mediana_ventas
            and
            row["Facturas"] < mediana_frecuencia
        ):

            return "Alto valor y ocasional"

        elif (
            row["Ventas"] < mediana_ventas
            and
            row["Facturas"] >= mediana_frecuencia
        ):

            return "Bajo valor y frecuente"

        else:

            return "Bajo valor y ocasional"

    clientes[
        "Segmento"
    ] = clientes.apply(
        clasificar_cliente,
        axis=1
    )

    segmentos = (
        clientes["Segmento"]
        .value_counts()
        .reset_index()
    )

    segmentos.columns = [
        "Segmento",
        "Clientes"
    ]

    segmentos[
        "Porcentaje"
    ] = (
        segmentos["Clientes"] /
        clientes_unicos *
        100
    )

    print(
        segmentos.to_string(
            index=False
        )
    )

    if generar_graficos:

        plt.figure(figsize=(10, 6))

        plt.bar(
            segmentos["Segmento"],
            segmentos["Clientes"]
        )

        plt.title(
            "Segmentación Básica de Clientes"
        )

        plt.xlabel(
            "Segmento"
        )

        plt.ylabel(
            "Número de clientes"
        )

        plt.xticks(
            rotation=25,
            ha="right"
        )

        plt.tight_layout()
        plt.show()

    # =======================================================
    # 9.15 RESUMEN FINAL
    # =======================================================

    resumen_clientes = pd.DataFrame({

        "Indicador": [

            "Clientes únicos",

            "Ventas totales",

            "Ventas promedio por cliente",

            "Mediana ventas por cliente",

            "Compras promedio por cliente",

            "Ticket promedio",

            "Productos diferentes promedio",

            "Correlación frecuencia-ventas",

            "Correlación frecuencia-ticket",

            "Participación Top 10 clientes",

            "Participación Top 20 clientes",

            "Participación Top 10% clientes"

        ],

        "Valor": [

            clientes_unicos,

            round(
                ventas_total,
                2
            ),

            round(
                clientes["Ventas"].mean(),
                2
            ),

            round(
                clientes["Ventas"].median(),
                2
            ),

            round(
                clientes["Facturas"].mean(),
                2
            ),

            round(
                clientes["Ticket_Promedio"].mean(),
                2
            ),

            round(
                clientes[
                    "Productos_Diferentes"
                ].mean(),
                2
            ),

            round(
                correlacion,
                4
            ),

            round(
                correlacion_ticket,
                4
            ),

            round(
                top_10_participacion,
                2
            ),

            round(
                top_20_participacion,
                2
            ),

            round(
                ventas_top_10_pct,
                2
            )

        ]

    })

    print("\n" + "=" * 70)
    print("RESUMEN DEL ANÁLISIS DE CLIENTES")
    print("=" * 70)

    print(
        resumen_clientes.to_string(
            index=False
        )
    )

    print("=" * 70)

    # =======================================================
    # RETORNAR RESULTADOS
    # =======================================================

    return {

        "clientes": clientes,

        "top_ventas":
            top_ventas,

        "top_frecuencia":
            top_frecuencia,

        "top_ticket":
            top_ticket,

        "segmentos":
            segmentos,

        "resumen_clientes":
            resumen_clientes

    }


