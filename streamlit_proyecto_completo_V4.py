import sys
import importlib.util
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Proyecto | Sistema de Recomendación",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).resolve().parent

# ============================================================
# IMPORTACIÓN ROBUSTA DE LOS MÓDULOS DE MODELOS
# ============================================================
# V4 no importa directamente Modelos_juntos.py porque ese archivo
# ejecuta dependencias adicionales (MLflow) y solo expone ALS/FP-Growth.
# En su lugar reutilizamos las funciones reales de los archivos adjuntos:
# ft_engineering.py, item_based_cf.py, als_model.py y popularity_baseline.py.

MODEL_IMPORT_ERROR = None
FT_FILE = None
ITEM_FILE = None


def _find_file(filename):
    candidates = [
        ROOT / "src" / "Modelos" / filename,
        ROOT / "src" / "models" / filename,
        ROOT / "src" / filename,
        ROOT / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    src = ROOT / "src"
    if src.exists():
        matches = [
            p for p in src.rglob(filename)
            if "__pycache__" not in p.parts and ".venv" not in p.parts
        ]
        if matches:
            return matches[0]
    return None


def _load_module(module_name, path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No fue posible cargar {module_name} desde {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


try:
    # La carpeta raíz, src y src/Modelos deben estar en sys.path para que
    # ft_engineering pueda resolver imports como src.snowflake.load_data.
    for path in [ROOT, ROOT / "src", ROOT / "src" / "Modelos", ROOT / "src" / "models"]:
        if path.exists() and str(path) not in sys.path:
            sys.path.insert(0, str(path))

    FT_FILE = _find_file("ft_engineering.py")
    if FT_FILE is None:
        raise FileNotFoundError(
            "No se encontró ft_engineering.py. Debe estar en src/Modelos/"
        )

    ft_module = _load_module("ft_engineering", FT_FILE)

    ITEM_FILE = _find_file("item_based_cf.py")
    if ITEM_FILE is not None:
        item_module = _load_module("item_based_cf", ITEM_FILE)
    else:
        item_module = None

    load_raw = ft_module.load_raw
    get_train_test = ft_module.get_train_test
    get_train_test_fpgrowth = ft_module.get_train_test_fpgrowth

    # Funciones equivalentes a las entregadas en los archivos de modelos.
    K = getattr(item_module, "K", 10) if item_module else 10
    precision_at_k = getattr(item_module, "precision_at_k", None) if item_module else None
    recall_at_k = getattr(item_module, "recall_at_k", None) if item_module else None
    average_precision_at_k = getattr(item_module, "average_precision_at_k", None) if item_module else None

except Exception as exc:
    MODEL_IMPORT_ERROR = exc
    load_raw = None
    get_train_test = None
    get_train_test_fpgrowth = None
    K = 10
    precision_at_k = recall_at_k = average_precision_at_k = None


# ============================================================
# FUNCIONES DE LOS MODELOS
# ============================================================


def top_k_items(train_matrix, k=10):
    """Baseline de popularidad, equivalente a popularity_baseline.py."""
    total_qty_per_item = np.asarray(train_matrix.sum(axis=0)).ravel()
    return np.argsort(-total_qty_per_item)[:k]


def recommend_cf(customer_code, train_matrix, item_similarity, k=10, exclude_seen=True):
    """Item-Based CF, equivalente a item_based_cf.py."""
    bought = train_matrix[customer_code].toarray().ravel()
    scores = bought @ item_similarity
    if exclude_seen:
        scores[bought.nonzero()] = -np.inf
    k = min(k, len(scores))
    top = np.argpartition(scores, -k)[-k:]
    return top[np.argsort(-scores[top])]


def recommend_als(model, customer_code, train_matrix, k=10):
    """ALS con recompras permitidas, como Modelos_juntos.py."""
    item_ids, _scores = model.recommend(
        customer_code,
        train_matrix[customer_code],
        N=k,
        filter_already_liked_items=False,
    )
    return item_ids


def build_basket_matrix(train_basket_list):
    """Construye la matriz binaria factura x producto para FP-Growth."""
    from sklearn.preprocessing import MultiLabelBinarizer
    mlb = MultiLabelBinarizer()
    basket_array = mlb.fit_transform(train_basket_list)
    return pd.DataFrame(
        basket_array.astype(bool),
        columns=mlb.classes_,
    )


def recommend_fp_growth(producto_base_code, basket_matrix, k=10):
    """Cross-selling por coocurrencia, equivalente al módulo entregado."""
    if producto_base_code not in basket_matrix.columns:
        return []
    transacciones = basket_matrix[basket_matrix[producto_base_code]]
    if len(transacciones) == 0:
        return []
    coocurrencias = (
        transacciones.drop(columns=[producto_base_code])
        .sum()
        .sort_values(ascending=False)
    )
    return coocurrencias.head(k).index.tolist()


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .hero { padding: 28px 32px; border-radius: 16px;
            background: linear-gradient(135deg, #172554, #1e3a8a);
            color: white; margin-bottom: 22px; }
    .hero h1 { font-size: 2.4rem; margin-bottom: 8px; }
    .hero p { font-size: 1.08rem; margin-bottom: 0; }
    .authors { margin-top: 14px; font-size: 0.95rem; opacity: 0.95;
               letter-spacing: 0.15px; }
    .architecture-card { padding: 18px; border-radius: 14px;
                         background: #f8fafc; border: 1px solid #dbeafe;
                         text-align: center; min-height: 150px; }
    .architecture-card h4 { margin-bottom: 8px; }
    .architecture-arrow { display: flex; align-items: center;
                          justify-content: center; font-size: 2rem;
                          color: #2563eb; min-height: 150px; }
    .status-implemented { border-left: 5px solid #16a34a;
                          background: #f0fdf4; padding: 12px 16px;
                          border-radius: 10px; }
    .status-integration { border-left: 5px solid #f59e0b;
                          background: #fffbeb; padding: 12px 16px;
                          border-radius: 10px; }
    .story { padding: 18px 22px; border-radius: 12px;
             background: #f5f7fb; border-left: 5px solid #2563eb;
             margin: 12px 0 20px 0; }
    .success-story { padding: 18px 22px; border-radius: 12px;
                     background: #f1f8f4; border-left: 5px solid #16a34a;
                     margin: 12px 0 20px 0; }
    .big-number { font-size: 2.1rem; font-weight: 700; }
    .small-muted { color: #64748b; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATOS EDA
# ============================================================

@st.cache_data(show_spinner="Cargando dataset para el EDA...")
def load_eda_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_csv(
            uploaded_file,
            encoding="utf-8-sig",
        )

    paths = [
        ROOT / "src" / "data" / "raw" / "online_retail_II.csv",
        ROOT / "data" / "raw" / "online_retail_II.csv",
        ROOT.parent / "data" / "raw" / "online_retail_II.csv",
        ROOT.parent.parent / "data" / "raw" / "online_retail_II.csv",
    ]

    for path in paths:
        if path.exists():
            return pd.read_csv(
                path,
                encoding="utf-8-sig",
            )

    return None


@st.cache_data(show_spinner="Aplicando limpieza del EDA...")
def clean_eda_data(df):
    d = df.copy()

    d.columns = [
        str(c).strip()
        for c in d.columns
    ]

    if "Customer ID" in d.columns:
        d.rename(
            columns={"Customer ID": "CustomerID"},
            inplace=True,
        )

    d["InvoiceDate"] = pd.to_datetime(
        d["InvoiceDate"],
        errors="coerce",
    )

    d["Quantity"] = pd.to_numeric(
        d["Quantity"],
        errors="coerce",
    )

    d["Price"] = pd.to_numeric(
        d["Price"],
        errors="coerce",
    )

    initial = len(d)

    rules = {
        "CustomerID nulo": int(d["CustomerID"].isna().sum()),
        "Factura cancelada": int(
            d["Invoice"]
            .astype(str)
            .str.startswith("C")
            .sum()
        ),
        "Quantity negativa": int(
            (d["Quantity"] < 0).sum()
        ),
        "Quantity = 0": int(
            (d["Quantity"] == 0).sum()
        ),
        "Price negativo": int(
            (d["Price"] < 0).sum()
        ),
        "Price = 0": int(
            (d["Price"] == 0).sum()
        ),
        "Quantity >= 1800": int(
            (d["Quantity"] >= 1800).sum()
        ),
        "Price >= 250": int(
            (d["Price"] >= 250).sum()
        ),
    }

    clean = d[
        (d["Quantity"] < 1800)
        & (d["Price"] < 250)
        & d["CustomerID"].notna()
        & ~d["Invoice"].astype(str).str.startswith("C")
        & (d["Quantity"] > 0)
        & (d["Price"] > 0)
    ].copy()

    clean["Total"] = (
        clean["Quantity"] *
        clean["Price"]
    )

    clean["Año"] = clean["InvoiceDate"].dt.year
    clean["Mes"] = clean["InvoiceDate"].dt.month
    clean["Dia_Semana"] = (
        clean["InvoiceDate"]
        .dt.day_name()
    )
    clean["Hora"] = (
        clean["InvoiceDate"]
        .dt.hour
    )

    clean.reset_index(
        drop=True,
        inplace=True,
    )

    meta = {
        "initial": initial,
        "final": len(clean),
        "rules": rules,
    }

    return clean, meta


# ============================================================
# MODELOS
# ============================================================

METRICS = pd.DataFrame(
    [
        ["Popularidad (Top-K)", 0.0773, 0.0243, 0.0378, 0.0022],
        ["Item-Based CF",       0.1162, 0.0575, 0.0827, 0.3931],
        ["ALS",                 0.1631, 0.0802, 0.0969, 0.2726],
        ["FP-Growth",           0.1404, 0.1042, 0.1098, 0.4583],
    ],
    columns=["Modelo", "Precision@10", "Recall@10", "MAP@10", "Coverage@10"],
)


@st.cache_data(show_spinner="Cargando transacciones para los modelos...")
def load_model_data():
    if MODEL_IMPORT_ERROR is not None or load_raw is None:
        raise RuntimeError(
            "No fue posible importar ft_engineering.py: "
            f"{MODEL_IMPORT_ERROR}"
        )
    return load_raw()


@st.cache_resource(show_spinner="Preparando modelos de recomendación...")
def build_recommendation_system():
    """Prepara una sola vez las matrices y modelos usados por la demo."""
    if MODEL_IMPORT_ERROR is not None:
        raise RuntimeError(str(MODEL_IMPORT_ERROR))

    raw_df = load_model_data()

    (
        train_matrix,
        test_df,
        customer_map,
        item_map,
        description_map,
    ) = get_train_test(raw_df=raw_df)

    # Item-Based CF: mismo enfoque del archivo item_based_cf.py.
    item_similarity = cosine_similarity(
        train_matrix.T,
        dense_output=True,
    )

    # ALS: mismos hiperparámetros del archivo als_model.py / Modelos_juntos.py.
    try:
        from implicit.als import AlternatingLeastSquares
    except Exception as exc:
        raise RuntimeError(
            "No está instalada la dependencia 'implicit'. "
            "Instálala con: pip install implicit\n\n" + str(exc)
        )

    als_model = AlternatingLeastSquares(
        factors=50,
        regularization=0.01,
        iterations=20,
    )
    als_model.fit(train_matrix)

    popular_items = top_k_items(train_matrix, k=10)

    (
        train_basket_list,
        fp_test_df,
        fp_description_map,
    ) = get_train_test_fpgrowth(raw_df=raw_df)

    basket_matrix = build_basket_matrix(train_basket_list)

    return {
        "raw_df": raw_df,
        "train_matrix": train_matrix,
        "test_df": test_df,
        "customer_map": customer_map,
        "item_map": item_map,
        "description_map": description_map,
        "item_similarity": item_similarity,
        "als_model": als_model,
        "popular_items": popular_items,
        "basket_matrix": basket_matrix,
        "fp_description_map": fp_description_map,
        "fp_test_df": fp_test_df,
    }


def product_name(
    stock_code,
    description_map,
):
    return description_map.get(
        stock_code,
        stock_code,
    )


def recommendation_table(
    items,
    item_map,
    description_map,
):
    rows = []

    for rank, internal_item in enumerate(
        items,
        start=1,
    ):
        stock_code = item_map.get(
            internal_item,
            internal_item,
        )

        rows.append(
            {
                "Ranking": rank,
                "StockCode": stock_code,
                "Producto": product_name(
                    stock_code,
                    description_map,
                ),
            }
        )

    return pd.DataFrame(rows)


def fp_recommendation_table(
    items,
    description_map,
):
    rows = []

    for rank, stock_code in enumerate(
        items,
        start=1,
    ):
        rows.append(
            {
                "Ranking": rank,
                "StockCode": stock_code,
                "Producto": product_name(
                    stock_code,
                    description_map,
                ),
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"€{value:,.2f}"


def percentage(value):
    return f"{value:.2%}"


def insight(text):
    st.markdown(
        f"""
        <div class="story">
            <b>💡 Insight:</b> {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title, subtitle=None):
    st.header(title)

    if subtitle:
        st.caption(subtitle)



# ============================================================
# 05 FUNCIONAMIENTO DEL MODELO
# ============================================================

def render_funcionamiento_modelo():

    section_title(
        "05 · Funcionamiento del modelo",
        "Del dato histórico a una recomendación que puede ser consumida "
        "por una aplicación.",
    )

    st.markdown(
        """
        <div class="story">
        <h3>🏗️ ¿Cómo funciona la solución de extremo a extremo?</h3>
        <p>
        El sistema toma las transacciones históricas, las limpia y transforma,
        entrena los recomendadores, evalúa su desempeño y expone las
        recomendaciones para que puedan ser utilizadas por una aplicación.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("⚙️ Flujo de entrenamiento y consumo de recomendaciones")

    _, diagram_col, _ = st.columns([1, 2, 1])
    with diagram_col:
        st.image(
            ROOT / "src" / "api" / "static" / "diagrama_flujo_modelo.png",
            caption=(
                "Flujo desde el entrenamiento en Snowflake hasta las "
                "recomendaciones mostradas al cliente."
            ),
            use_container_width=True,
        )

    st.divider()

    # --------------------------------------------------------
    # Arquitectura visual
    # --------------------------------------------------------

    st.subheader("🔄 Arquitectura completa")

    stages = [
        (
            "1️⃣ Datos",
            "❄️ Snowflake",
            "Transacciones históricas",
        ),
        (
            "2️⃣ Preparación",
            "🐍 Python",
            "Limpieza + transformación + features",
        ),
        (
            "3️⃣ Entrenamiento",
            "🤖 Modelos",
            "Popularidad · CF · ALS · FP-Growth",
        ),
        (
            "4️⃣ Servicio",
            "⚡ FastAPI",
            "API de recomendaciones",
        ),
        (
            "5️⃣ Despliegue",
            "🐳 Docker",
            "Entorno reproducible",
        ),
    ]

    for i in range(0, len(stages), 3):
        batch = stages[i:i + 3]

        cols = st.columns(
            len(batch) * 2 - 1
        )

        position = 0

        for j, (title, icon, description) in enumerate(batch):

            with cols[position]:
                st.markdown(
                    f"""
                    <div class="architecture-card">
                        <h4>{title}</h4>
                        <div style="font-size:2rem;">{icon}</div>
                        <p><strong>{description}</strong></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            position += 1

            if j < len(batch) - 1:
                with cols[position]:
                    st.markdown(
                        '<div class="architecture-arrow">→</div>',
                        unsafe_allow_html=True,
                    )

                position += 1

    st.markdown(
        '<div class="architecture-arrow">↓</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>📊 Streamlit</h4>
                <div style="font-size:2rem;">🎛️</div>
                <p>
                Exploración del EDA, comparación de modelos,
                demostración y visualización de recomendaciones.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>🌐 Página web / E-commerce</h4>
                <div style="font-size:2rem;">🛒</div>
                <p>
                Puede consumir la API para mostrar recomendaciones
                directamente al cliente.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Flujo técnico: entrenamiento offline + consumo online
    # --------------------------------------------------------

    st.subheader("⚙️ Flujo técnico del sistema")

    st.markdown(
        """
        <div class="story">
            <h3>🔄 Dos momentos, un mismo motor de recomendación</h3>
            <p>
                La solución separa el <strong>entrenamiento offline</strong>,
                donde se preparan los datos y se generan los artefactos,
                del <strong>consumo online</strong>, donde la API utiliza
                esos artefactos para responder las solicitudes del usuario.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # FASE 1
    st.markdown(
        """
        <div style="
            padding:12px 18px;
            border-radius:12px;
            background:#eff6ff;
            border-left:6px solid #2563eb;
            margin:10px 0 16px 0;
        ">
            <strong>🔵 FASE 1 · ENTRENAMIENTO OFFLINE</strong><br>
            <span style="color:#64748b;">
                Se ejecuta cuando se actualizan o reentrenan los modelos.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, a1, c2, a2, c3 = st.columns([3, 0.7, 3, 0.7, 3])

    with c1:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>🐍 ft_engineering2.py</h4>
                <div style="font-size:2rem;">🗄️ → 🧹 → 🧠</div>
                <p>
                    Conecta a <strong>Snowflake</strong>, prepara los datos
                    y entrena los modelos.
                </p>
                <hr>
                <span class="small-muted">
                    ALS · FP-Growth · Popularidad
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a1:
        st.markdown(
            '<div class="architecture-arrow">→</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>⚙️ train_and_export.py</h4>
                <div style="font-size:2rem;">🔄</div>
                <p>
                    Ejecuta el entrenamiento una vez y prepara
                    los resultados para producción.
                </p>
                <hr>
                <span class="small-muted">
                    Entrenar → validar → exportar
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a2:
        st.markdown(
            '<div class="architecture-arrow">→</div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>📦 artifacts/</h4>
                <div style="font-size:2rem;">💾</div>
                <p>
                    Guarda los resultados que serán reutilizados
                    por la aplicación.
                </p>
                <hr>
                <span class="small-muted">
                    .npz → matrices / ALS<br>
                    .pkl → mapas de IDs
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="architecture-arrow">↓</div>',
        unsafe_allow_html=True,
    )

    # Separador de fases
    st.markdown(
        """
        <div style="
            border-top:2px dashed #cbd5e1;
            margin:12px 0 22px 0;
            position:relative;
        ">
            <div style="
                text-align:center;
                margin-top:-13px;
            ">
                <span style="
                    background:white;
                    padding:0 14px;
                    color:#f97316;
                    font-weight:700;
                ">
                    🟠 FASE 2 · CONSUMO ONLINE
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Cada vez que un usuario solicita una recomendación, "
        "se utilizan los artefactos previamente generados; "
        "el modelo no necesita volver a entrenarse."
    )

    c1, a1, c2 = st.columns([3, 0.7, 3])

    with c1:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>🚀 main.py</h4>
                <div style="font-size:2rem;">📦 → 🌐</div>
                <p>
                    Carga <strong>artifacts/</strong> al iniciar
                    y expone la API de recomendaciones.
                </p>
                <hr>
                <span class="small-muted">
                    Recibe solicitud → ejecuta → responde JSON
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with a1:
        st.markdown(
            '<div class="architecture-arrow">→</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="architecture-card">
                <h4>🤖 Modelos_top.py</h4>
                <div style="font-size:2rem;">🧠</div>
                <p>
                    Contiene las funciones que generan
                    las recomendaciones.
                </p>
                <hr>
                <span class="small-muted">
                    recomendar_als()<br>
                    recomendar_fp_growth()
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="architecture-arrow">↓</div>',
        unsafe_allow_html=True,
    )

    # Frontend
    st.markdown(
        """
        <div class="architecture-card" style="
            max-width:900px;
            margin:0 auto;
        ">
            <h4>🌐 static/</h4>
            <div style="font-size:2rem;">HTML · CSS · JavaScript</div>
            <p>
                Es la capa que ve e interactúa con el usuario.
            </p>
            <hr>
            <span class="small-muted">
                <strong>index.html</strong> → estructura ·
                <strong>style.css</strong> → diseño ·
                <strong>script.js</strong> → interacción y fetch()
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="architecture-arrow">↓</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            max-width:650px;
            margin:0 auto;
            padding:18px 22px;
            border-radius:14px;
            background:#fff7ed;
            border:1px solid #fed7aa;
            text-align:center;
        ">
            <h4>👤 Navegador del cliente</h4>
            <div style="font-size:2rem;">🧑‍💻</div>
            <p>
                Ingresa <strong>CustomerID</strong>, interactúa con
                la página y solicita una recomendación.
            </p>
            <strong>
                Solicitud → API → Modelo → JSON → Página
            </strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Flujo de una solicitud
    st.subheader("🔁 ¿Qué ocurre cuando el usuario hace clic?")

    request_steps = [
        ("1", "👤 Usuario", "Ingresa CustomerID o selecciona un producto."),
        ("2", "📡 JavaScript", "Hace una petición mediante fetch()."),
        ("3", "⚡ API / main.py", "Recibe la solicitud."),
        ("4", "🤖 Modelos_top.py", "Ejecuta el recomendador correspondiente."),
        ("5", "🧠 Modelo", "Calcula y ordena los productos candidatos."),
        ("6", "📄 JSON", "La API devuelve las recomendaciones."),
        ("7", "🛒 Frontend", "La página muestra los productos al cliente."),
    ]

    for number, title, description in request_steps:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:14px;
                padding:9px 14px;
                margin:5px 0;
                border-radius:10px;
                background:#f8fafc;
                border-left:4px solid #2563eb;
            ">
                <div style="
                    min-width:34px;
                    height:34px;
                    border-radius:50%;
                    background:#2563eb;
                    color:white;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-weight:700;
                ">{number}</div>
                <div>
                    <strong>{title}</strong><br>
                    <span style="color:#64748b;">
                        {description}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        """
        **🎯 Concepto clave para la sustentación**

        El entrenamiento es **offline** y puede ser costoso.
        La recomendación es **online**: la aplicación reutiliza los
        artefactos ya entrenados para responder rápidamente.
        Así, el mismo motor puede ser consumido por **Streamlit,
        una página web u otros sistemas** mediante la API.
        """
    )

    # --------------------------------------------------------
    # 1. Datos
    # --------------------------------------------------------

    st.subheader("1️⃣ Fuente de datos")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Transacciones",
            "805.243",
        )

    with c2:
        st.metric(
            "Clientes evaluados",
            "2.285",
        )

    with c3:
        st.metric(
            "Modelos evaluados",
            "4",
        )

    st.markdown(
        """
        **Snowflake** centraliza las transacciones utilizadas por el
        sistema. La información se consulta y se lleva al proceso de
        preparación antes de entrenar los modelos.
        """
    )

    # --------------------------------------------------------
    # 2. Limpieza
    # --------------------------------------------------------

    st.subheader("2️⃣ Limpieza y preparación")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="status-implemented">
            <strong>🧹 Limpieza</strong><br><br>
            • Nulos<br>
            • Cancelaciones<br>
            • Cantidades inválidas<br>
            • Precios inválidos<br>
            • Outliers
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="status-implemented">
            <strong>🔧 Transformación</strong><br><br>
            • Clientes<br>
            • Productos<br>
            • Facturas<br>
            • Fechas<br>
            • Total de venta
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="status-implemented">
            <strong>🧠 Feature Engineering</strong><br><br>
            • Matriz cliente-producto<br>
            • Matriz producto-producto<br>
            • Cestas de compra<br>
            • Variables para entrenamiento
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # 3. Entrenamiento
    # --------------------------------------------------------

    st.subheader("3️⃣ Entrenamiento de los recomendadores")

    model_flow = pd.DataFrame(
        {
            "Modelo": [
                "Popularidad",
                "Item-Based CF",
                "ALS",
                "FP-Growth",
            ],
            "Qué aprende": [
                "Productos más frecuentes",
                "Relación entre productos",
                "Patrones cliente-producto",
                "Productos comprados juntos",
            ],
            "Uso de negocio": [
                "Línea base",
                "Recomendación por similitud",
                "Personalización",
                "Cross-selling",
            ],
        }
    )

    st.dataframe(
        model_flow,
        width='stretch',
        hide_index=True,
    )

    # --------------------------------------------------------
    # 4. Evaluación
    # --------------------------------------------------------

    st.subheader("4️⃣ Evaluación")

    st.caption(
        "Los valores corresponden a la ejecución actual de "
        "Modelos_juntos.py."
    )

    evaluation = pd.DataFrame(
        {
            "Modelo": [
                "Popularidad (Top-K)",
                "Item-Based CF",
                "ALS",
                "FP-Growth",
            ],
            "Precision@10": [
                0.0773,
                0.1162,
                0.1631,
                0.1404,
            ],
            "Recall@10": [
                0.0243,
                0.0575,
                0.0802,
                0.1042,
            ],
            "MAP@10": [
                0.0378,
                0.0827,
                0.0969,
                0.1098,
            ],
            "Coverage@10": [
                0.0022,
                0.3931,
                0.2726,
                0.4583,
            ],
        }
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🥇 Precision@10",
        "16,31%",
        "ALS",
    )

    c2.metric(
        "🥇 Recall@10",
        "10,42%",
        "FP-Growth",
    )

    c3.metric(
        "🥇 MAP@10",
        "10,98%",
        "FP-Growth",
    )

    c4.metric(
        "🥇 Coverage@10",
        "45,83%",
        "FP-Growth",
    )

    # --------------------------------------------------------
    # 5. Motor de recomendación
    # --------------------------------------------------------

    st.subheader("5️⃣ Generación de recomendaciones")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            ### 👤 Recomendación por cliente

            **ALS / Item-Based CF**

            1. Se identifica el cliente.
            2. Se consulta su historial.
            3. El modelo calcula productos candidatos.
            4. Se ordenan por relevancia.
            5. Se entregan los Top-K productos.
            """
        )

    with c2:
        st.markdown(
            """
            ### 🛒 Recomendación por producto

            **FP-Growth**

            1. Se identifica el producto de referencia.
            2. Se buscan asociaciones históricas.
            3. Se identifican productos frecuentes en las mismas cestas.
            4. Se ordenan las asociaciones.
            5. Se entregan productos complementarios.
            """
        )

    # --------------------------------------------------------
    # 6. API
    # --------------------------------------------------------

    st.subheader("6️⃣ API de recomendaciones")

    st.info(
        """
        ⚡ **FastAPI**

        La API es la capa que permite que otras aplicaciones utilicen
        el modelo sin conocer su implementación interna.

        Una aplicación envía un identificador y recibe una respuesta
        con productos recomendados.
        """
    )

    api_col1, api_col2 = st.columns(2)

    with api_col1:
        st.markdown("**Ejemplo conceptual — recomendación por cliente**")

        st.code(
            """GET /recommend/client/12371

{
  "customer_id": 12371,
  "recommendations": [
    "Producto A",
    "Producto B",
    "Producto C"
  ]
}""",
            language="text",
        )

    with api_col2:
        st.markdown("**Ejemplo conceptual — recomendación por producto**")

        st.code(
            """GET /recommend/product/85123A

{
  "stock_code": "85123A",
  "recommendations": [
    "Producto X",
    "Producto Y",
    "Producto Z"
  ]
}""",
            language="text",
        )

    # --------------------------------------------------------
    # 7. Docker
    # --------------------------------------------------------

    st.subheader("7️⃣ Docker: empaquetar la solución")

    st.markdown(
        """
        Docker permite empaquetar la API, el modelo y sus dependencias
        en un contenedor reproducible.

        El objetivo es que el sistema pueda ejecutarse de la misma manera
        en desarrollo, pruebas y producción.
        """
    )

    st.code(
        """Dockerfile
│
├── Python
├── Dependencias
├── FastAPI
├── Modelo
└── Configuración

        ↓

Contenedor
        ↓

API de recomendaciones""",
        language="text",
    )

    # --------------------------------------------------------
    # 8. Consumidores
    # --------------------------------------------------------

    st.subheader("8️⃣ ¿Quién consume la recomendación?")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            ### 🎛️ Streamlit

            **Analítica y demostración**

            • EDA<br>
            • Modelos<br>
            • Comparación<br>
            • Demo
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            ### 🌐 Página web

            **Experiencia del cliente**

            • Recomendados para ti<br>
            • Productos relacionados<br>
            • Venta cruzada
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            ### 📣 Marketing / CRM

            **Activación comercial**

            • Campañas personalizadas<br>
            • Cross-selling<br>
            • Segmentación
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Estado real del proyecto
    # --------------------------------------------------------

    st.divider()

    st.subheader("📌 Estado de la implementación")

    status = pd.DataFrame(
        {
            "Componente": [
                "Limpieza y preparación",
                "Snowflake",
                "Entrenamiento",
                "Evaluación",
                "Streamlit",
                "FastAPI",
                "Docker",
                "Página web",
            ],
            "Estado": [
                "✅ Implementado",
                "✅ Implementado",
                "✅ Implementado",
                "✅ Implementado",
                "✅ Implementado",
                "✅ Capa de integración",
                "✅ Capa de despliegue",
                "✅ Capa de consumo",
            ],
        }
    )

    st.dataframe(
        status,
        width='stretch',
        hide_index=True,
    )

    insight(
        "La arquitectura separa el análisis y entrenamiento del consumo "
        "de las recomendaciones. Esto permite que el mismo motor pueda "
        "ser utilizado por Streamlit, una página web u otros sistemas."
    )


# ============================================================
# INICIO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🛒 Sistema Inteligente de Recomendación</h1>
        <p>
            Del problema de negocio → al análisis de datos →
            al modelo de recomendación → a una recomendación accionable.
        </p>
        <div class="authors">
            <strong>Autores:</strong>
            Daniel Ruiz · Jessica Roncancio · Luis Pacheco<br>
            Isaac Esquinca · Alejandro Zarazoza · Ismael Hernandez
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:

    st.header("🎤 Presentación")

    modo_presentacion = st.toggle(
        "Modo presentación",
        value=False,
        help="Oculta controles secundarios y deja una navegación más limpia.",
    )

    seccion = st.radio(
        "Ruta de la presentación",
        [
            "01 · Problema",
            "02 · EDA",
            "03 · Hallazgos",
            "04 · Modelos",
            "05 · Funcionamiento del modelo",
            "06 · Comparación",
            "07 · Demo recomendador",
            "08 · Cierre",
        ],
    )

    st.divider()

    st.caption(
        "Proyecto de Sistema de Recomendación · Online Retail II"
    )


# ============================================================
# 01 PROBLEMA
# ============================================================

if seccion == "01 · Problema":

    section_title(
        "01 · El problema de negocio",
        "Por qué una tienda con muchas transacciones necesita convertir "
        "datos históricos en recomendaciones.",
    )

    st.markdown(
        """
        <div class="story">
        <h3>🎯 Pregunta central</h3>
        <p>
        ¿Cómo podemos utilizar el comportamiento histórico de compra
        para recomendar productos relevantes a cada cliente y generar
        oportunidades de venta cruzada?
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("📦 Complejidad")
        st.write(
            "El negocio registra miles de transacciones y una gran "
            "variedad de productos."
        )

    with c2:
        st.subheader("👥 Personalización")
        st.write(
            "No todos los clientes compran lo mismo ni tienen "
            "el mismo comportamiento."
        )

    with c3:
        st.subheader("💰 Oportunidad")
        st.write(
            "Las relaciones entre productos pueden utilizarse para "
            "venta cruzada y recomendaciones."
        )

    st.divider()

    st.subheader("De la pregunta al proyecto")

    pasos = pd.DataFrame(
        {
            "Etapa": [
                "Problema",
                "Datos",
                "EDA",
                "Modelado",
                "Evaluación",
                "Recomendación",
            ],
            "Pregunta": [
                "¿Qué queremos mejorar?",
                "¿Qué información tenemos?",
                "¿Qué patrones existen?",
                "¿Qué modelo puede capturarlos?",
                "¿Cuál funciona mejor?",
                "¿Cómo lo usamos?",
            ],
        }
    )

    st.dataframe(
        pasos,
        width='stretch',
        hide_index=True,
    )

    insight(
        "El objetivo no es simplemente predecir una compra: es utilizar "
        "el comportamiento histórico para entregar recomendaciones "
        "relevantes y accionables."
    )


# ============================================================
# 02 EDA
# ============================================================

elif seccion == "02 · EDA":

    section_title(
        "02 · Análisis Exploratorio de Datos",
        "Primero entendemos los datos antes de entrenar los modelos.",
    )

    uploaded = None

    if not modo_presentacion:
        uploaded = st.file_uploader(
            "Opcional: cargar online_retail_II.csv",
            type=["csv"],
        )

    raw = load_eda_data(uploaded)

    if raw is None:
        st.warning(
            "No se encontró el CSV automáticamente. "
            "Carga online_retail_II.csv o ejecuta Streamlit desde "
            "la raíz del proyecto."
        )
        st.stop()

    clean, meta = clean_eda_data(raw)

    tabs = st.tabs(
        [
            "📋 Comprensión",
            "🧹 Calidad",
            "📊 Univariado",
            "🛒 Basket",
            "🔗 Bivariado",
            "⏱️ Temporal",
            "👥 Clientes",
        ]
    )

    # --------------------------------------------------------
    # Comprensión
    # --------------------------------------------------------

    with tabs[0]:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Registros originales",
            f"{len(raw):,}",
        )

        c2.metric(
            "Variables",
            f"{raw.shape[1]:,}",
        )

        c3.metric(
            "Registros limpios",
            f"{len(clean):,}",
        )

        st.subheader("Estructura")

        info = pd.DataFrame(
            {
                "Variable": raw.columns,
                "Tipo": raw.dtypes.astype(str).values,
                "Nulos": raw.isna().sum().values,
                "Únicos": raw.nunique().values,
            }
        )

        st.dataframe(
            info,
            width='stretch',
            hide_index=True,
        )

        st.subheader("Primeras observaciones")

        st.dataframe(
            raw.head(10),
            width='stretch',
        )

    # --------------------------------------------------------
    # Calidad
    # --------------------------------------------------------

    with tabs[1]:

        st.markdown("### 🧹 Calidad y limpieza de los datos")

        st.caption(
            "Evaluamos la calidad del dataset antes de utilizarlo para "
            "construir los modelos de recomendación."
        )

        # ========================================================
        # 1. VALORES NULOS
        # ========================================================

        st.markdown("#### 🔎 1. Valores nulos")

        missing = pd.DataFrame(
            {
                "Nulos": raw.isna().sum(),
                "% Nulos": raw.isna().mean() * 100,
            }
        ).sort_values(
            "Nulos",
            ascending=False,
        )

        c1, c2 = st.columns(2)

        with c1:

            st.dataframe(
                missing.style.format(
                    {"% Nulos": "{:.2f}%"}
                ),
                width='stretch',
                hide_index=False,
            )

        with c2:

            missing_plot = (
                missing[
                    missing["Nulos"] > 0
                ]
                .sort_values("% Nulos")
                .reset_index()
            )

            if not missing_plot.empty:

                fig = px.bar(
                    missing_plot,
                    x="% Nulos",
                    y=missing_plot.columns[0],
                    orientation="h",
                    title="Porcentaje de valores nulos",
                    labels={
                        "% Nulos": "% Nulos",
                        missing_plot.columns[0]: "",
                    },
                    text="% Nulos",
                )

                fig.update_traces(
                    texttemplate="%{text:.2f}%",
                    textposition="outside",
                )

                fig.update_layout(
                    height=400,
                    margin=dict(
                        l=10,
                        r=10,
                        t=50,
                        b=10,
                    ),
                )

                st.plotly_chart(
                    fig,
                    width='stretch',
                )

            else:

                st.success(
                    "✅ No se encontraron valores nulos."
                )

        # ========================================================
        # 2. INDICADORES DE CALIDAD
        # ========================================================

        st.markdown("#### 📊 2. Indicadores principales de calidad")

        # Compatibilidad Customer ID / CustomerID
        customer_col = (
            "Customer ID"
            if "Customer ID" in raw.columns
            else "CustomerID"
            if "CustomerID" in raw.columns
            else None
        )

        customer_nulos = (
            raw[customer_col].isna().sum()
            if customer_col
            else 0
        )

        cantidad_negativa = (
            (raw["Quantity"] < 0).sum()
            if "Quantity" in raw.columns
            else 0
        )

        precio_cero = (
            (raw["Price"] == 0).sum()
            if "Price" in raw.columns
            else 0
        )

        duplicados = raw.duplicated().sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📑 Duplicados",
            f"{duplicados:,}",
        )

        c2.metric(
            "📦 Quantity < 0",
            f"{cantidad_negativa:,}",
        )

        c3.metric(
            "💰 Price = 0",
            f"{precio_cero:,}",
        )

        c4.metric(
            "👥 Customer ID nulo",
            f"{customer_nulos:,}",
        )

        # ========================================================
        # 3. REGLAS DE LIMPIEZA
        # ========================================================

        st.markdown(
            "#### 🧹 3. Reglas de limpieza aplicadas"
        )

        st.caption(
            "Las reglas fueron definidas para conservar transacciones "
            "válidas y garantizar que los datos utilizados por los "
            "modelos representen adecuadamente el comportamiento de compra."
        )

        reglas_limpieza = pd.DataFrame(
            {
                "Regla de limpieza": [
                    "Eliminar registros con Customer ID nulo",
                    "Eliminar facturas canceladas",
                    "Eliminar cantidades negativas",
                    "Eliminar precios iguales a cero",
                    "Eliminar valores atípicos (Quantity ≥ 1800)",
                    "Eliminar valores atípicos (Price ≥ 250)",
                ],

                "Registros afectados": [
                    243007,
                    19494,
                    22950,
                    6202,
                    178,
                    934,
                ],

                "% del dataset": [
                    22.77,
                    1.83,
                    2.15,
                    0.58,
                    0.02,
                    0.09,
                ],

                "Justificación": [
                    (
                        "Impide identificar al cliente y construir "
                        "correctamente la matriz Cliente × Producto "
                        "requerida por Item-Based CF."
                    ),

                    (
                        "Corresponden a devoluciones o anulaciones "
                        "y no representan compras efectivas para "
                        "los modelos."
                    ),

                    (
                        "Representan devoluciones, ajustes de inventario "
                        "o correcciones operativas que pueden generar "
                        "asociaciones de compra incorrectas."
                    ),

                    (
                        "No representan ventas comerciales y afectan "
                        "el análisis del valor económico de las "
                        "transacciones."
                    ),

                    (
                        "Corresponden a cantidades excepcionalmente "
                        "grandes que pueden distorsionar las relaciones "
                        "de compra y la generación de recomendaciones."
                    ),

                    (
                        "Corresponden a precios excepcionalmente altos "
                        "que generan una elevada dispersión en el "
                        "análisis económico de los productos."
                    ),
                ],
            }
        )

        st.dataframe(
            reglas_limpieza.style.format(
                {
                    "Registros afectados": "{:,}",
                    "% del dataset": "{:.2f}%",
                }
            ),
            width='stretch',
            hide_index=True,
            column_config={
                "Regla de limpieza": st.column_config.TextColumn(
                    "Regla de limpieza",
                    width="medium",
                ),

                "Registros afectados": st.column_config.NumberColumn(
                    "Registros afectados",
                    format="%d",
                ),

                "% del dataset": st.column_config.NumberColumn(
                    "% del dataset",
                    format="%.2f%%",
                ),

                "Justificación": st.column_config.TextColumn(
                    "Justificación",
                    width="large",
                ),
            },
        )

        # ========================================================
        # 4. IMPACTO DE LAS REGLAS
        # ========================================================

        st.markdown(
            "#### 📉 4. Impacto de las reglas de limpieza"
        )

        impacto_limpieza = pd.DataFrame(
            {
                "Regla": [
                    "Customer ID nulo",
                    "Facturas canceladas",
                    "Quantity negativa",
                    "Price = 0",
                    "Quantity ≥ 1800",
                    "Price ≥ 250",
                ],

                "Registros": [
                    243007,
                    19494,
                    22950,
                    6202,
                    178,
                    934,
                ],
            }
        )

        impacto_limpieza = impacto_limpieza.sort_values(
            "Registros",
            ascending=True,
        )

        fig_impacto = px.bar(
            impacto_limpieza,
            x="Registros",
            y="Regla",
            orientation="h",
            title="Registros afectados por regla de limpieza",
            text="Registros",
        )

        fig_impacto.update_traces(
            texttemplate="%{text:,}",
            textposition="outside",
        )

        fig_impacto.update_layout(
            height=420,
            margin=dict(
                l=10,
                r=40,
                t=60,
                b=10,
            ),
            xaxis_title="Registros afectados",
            yaxis_title="",
        )

        st.plotly_chart(
            fig_impacto,
            width='stretch',
        )

        # ========================================================
        # 5. PRINCIPAL HALLAZGO
        # ========================================================

        st.markdown(
            """
            <div class="story">

            <h3>🎯 Principal hallazgo de calidad</h3>

            <p>
            El principal problema identificado corresponde a los registros
            sin <strong>Customer ID</strong>, que representan el
            <strong>22,77 % del dataset</strong>.
            </p>

            <p>
            Esta variable es especialmente importante porque el objetivo
            del proyecto es construir recomendaciones personalizadas.
            Sin identificación del cliente no podemos establecer
            correctamente la relación entre el cliente y los productos
            que ha comprado.
            </p>

            <p>
            Por esta razón, la limpieza no busca únicamente eliminar
            datos incorrectos, sino construir una base de datos adecuada
            para los modelos de recomendación.
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ========================================================
        # 6. FLUJO DE CALIDAD
        # ========================================================

        st.markdown(
            "#### 🔄 5. De los datos originales al dataset para modelar"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.markdown(
                """
                <div class="architecture-card">

                <h4>📥 Datos originales</h4>

                Transacciones históricas con:

                <br><br>

                • Nulos<br>
                • Cancelaciones<br>
                • Devoluciones<br>
                • Valores extremos<br>
                • Clientes sin identificación

                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:

            st.markdown(
                """
                <div class="architecture-arrow">
                ➜
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c3:

            st.markdown(
                """
                <div class="architecture-card">

                <h4>🤖 Dataset para modelar</h4>

                Datos preparados para:

                <br><br>

                • Matriz Cliente × Producto<br>
                • Relaciones Producto × Producto<br>
                • Patrones de compra<br>
                • Generación de recomendaciones

                </div>
                """,
                unsafe_allow_html=True,
            )

        # ========================================================
        # 7. CONCLUSIÓN
        # ========================================================

        insight(
            "La limpieza fue una etapa fundamental del proyecto: "
            "permitió transformar las transacciones históricas en un "
            "conjunto de datos consistente para identificar relaciones "
            "entre clientes y productos y generar recomendaciones "
            "más confiables."
        )

    # --------------------------------------------------------
    # Univariado
    # --------------------------------------------------------

    with tabs[2]:

        variable = st.selectbox(
            "Variable",
            [
                "Quantity",
                "Price",
                "Total",
            ],
            key="eda_univariate",
        )

        serie = clean[variable].dropna()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Media",
            f"{serie.mean():,.2f}",
        )

        c2.metric(
            "Mediana",
            f"{serie.median():,.2f}",
        )

        c3.metric(
            "P95",
            f"{serie.quantile(.95):,.2f}",
        )

        c4.metric(
            "P99",
            f"{serie.quantile(.99):,.2f}",
        )

        p99 = serie.quantile(.99)

        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                serie[serie <= p99],
                nbins=40,
                title=f"Distribución de {variable} hasta P99",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        with c2:
            fig = px.box(
                x=serie,
                title=f"Boxplot de {variable}",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

    # --------------------------------------------------------
    # Basket
    # --------------------------------------------------------

    with tabs[3]:

        basket = (
            clean.groupby("Invoice")["StockCode"]
            .nunique()
            .reset_index(
                name="Basket_Size"
            )
        )

        p99 = basket["Basket_Size"].quantile(.99)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Facturas",
            f"{len(basket):,}",
        )

        c2.metric(
            "Promedio",
            f"{basket.Basket_Size.mean():.2f}",
        )

        c3.metric(
            "Mediana",
            f"{basket.Basket_Size.median():.0f}",
        )

        c4.metric(
            "P99",
            f"{p99:.0f}",
        )

        c1, c2 = st.columns(2)

        with c1:
            fig = px.histogram(
                basket[
                    basket.Basket_Size <= p99
                ],
                x="Basket_Size",
                nbins=30,
                title="Distribución del Basket Size",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        with c2:

            categorias = pd.cut(
                basket["Basket_Size"],
                [
                    0,
                    1,
                    2,
                    5,
                    10,
                    20,
                    50,
                    np.inf,
                ],
                labels=[
                    "1",
                    "2",
                    "3-5",
                    "6-10",
                    "11-20",
                    "21-50",
                    ">50",
                ],
            )

            categorias = (
                categorias.value_counts()
                .sort_index()
                .reset_index()
            )

            categorias.columns = [
                "Rango",
                "Facturas",
            ]

            fig = px.bar(
                categorias,
                x="Rango",
                y="Facturas",
                title="Facturas por tamaño de cesta",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        insight(
            "El Basket Size conecta el EDA con la recomendación: "
            "si varios productos aparecen dentro de una misma cesta, "
            "existe una oportunidad natural de venta cruzada."
        )

    # --------------------------------------------------------
    # Bivariado
    # --------------------------------------------------------

    with tabs[4]:

        analysis = st.selectbox(
            "Análisis",
            [
                "Productos vs cantidad",
                "Productos vs facturación",
                "Países vs facturación",
                "Clientes vs frecuencia",
                "Correlaciones",
                "Coocurrencia",
            ],
            key="eda_bivariate",
        )

        top_n = st.slider(
            "Top N",
            5,
            30,
            15,
            key="eda_top_n",
        )

        if analysis == "Productos vs cantidad":

            data = (
                clean.groupby("Description")["Quantity"]
                .sum()
                .nlargest(top_n)
                .sort_values()
            )

            fig = px.bar(
                data,
                orientation="h",
                title="Productos por cantidad vendida",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        elif analysis == "Productos vs facturación":

            data = (
                clean.groupby("Description")["Total"]
                .sum()
                .nlargest(top_n)
                .sort_values()
            )

            fig = px.bar(
                data,
                orientation="h",
                title="Productos por facturación",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        elif analysis == "Países vs facturación":

            data = (
                clean.groupby("Country")["Total"]
                .sum()
                .nlargest(top_n)
                .sort_values()
            )

            fig = px.bar(
                data,
                orientation="h",
                title="Países por facturación",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        elif analysis == "Clientes vs frecuencia":

            data = (
                clean.groupby("CustomerID")["Invoice"]
                .nunique()
                .nlargest(top_n)
                .sort_values()
            )

            fig = px.bar(
                data,
                orientation="h",
                title="Clientes por frecuencia",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        elif analysis == "Correlaciones":

            corr = clean[
                [
                    "Quantity",
                    "Price",
                    "Total",
                ]
            ].corr()

            fig = px.imshow(
                corr,
                text_auto=".2f",
                title="Matriz de correlación",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        else:

            basket_matrix = (
                clean.groupby(
                    [
                        "Invoice",
                        "Description",
                    ]
                )["Quantity"]
                .sum()
                .unstack(
                    fill_value=0
                )
            )

            top_products = (
                basket_matrix.sum()
                .nlargest(20)
                .index
            )

            binary = (
                basket_matrix[
                    top_products
                ] > 0
            ).astype(int)

            cooc = binary.T.dot(binary)

            # Crear una copia mutable antes de modificar la diagonal.
            cooc_array = cooc.to_numpy(copy=True)
            np.fill_diagonal(cooc_array, 0)

            cooc = pd.DataFrame(
                cooc_array,
                index=cooc.index,
                columns=cooc.columns,
            )

            fig = px.imshow(
                cooc,
                aspect="auto",
                title="Coocurrencia — Top 20 productos",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

            pairs = []

            products = cooc.columns.tolist()

            for i in range(
                len(products)
            ):
                for j in range(
                    i + 1,
                    len(products),
                ):
                    pairs.append(
                        [
                            products[i],
                            products[j],
                            cooc.iloc[i, j],
                        ]
                    )

            pairs = (
                pd.DataFrame(
                    pairs,
                    columns=[
                        "Producto A",
                        "Producto B",
                        "Coocurrencias",
                    ],
                )
                .sort_values(
                    "Coocurrencias",
                    ascending=False,
                )
                .head(20)
            )

            st.subheader(
                "Top pares de productos"
            )

            st.dataframe(
                pairs,
                width='stretch',
                hide_index=True,
            )

            insight(
                "La coocurrencia es una de las evidencias que "
                "justifica utilizar FP-Growth para recomendaciones "
                "de venta cruzada."
            )

    # --------------------------------------------------------
    # Temporal
    # --------------------------------------------------------

    with tabs[5]:

        monthly = (
            clean.set_index("InvoiceDate")
            .resample("ME")
            .agg(
                Ventas=("Total", "sum"),
                Facturas=("Invoice", "nunique"),
            )
        )

        monthly["Ticket"] = (
            monthly["Ventas"] /
            monthly["Facturas"]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Mejor mes",
            monthly["Ventas"]
            .idxmax()
            .strftime("%Y-%ME"),
        )

        c2.metric(
            "Mayor venta mensual",
            money(
                monthly["Ventas"].max()
            ),
        )

        c3.metric(
            "Ticket medio",
            money(
                monthly["Ticket"].mean()
            ),
        )

        fig = px.line(
            monthly.reset_index(),
            x="InvoiceDate",
            y="Ventas",
            markers=True,
            title="Evolución mensual",
        )

        st.plotly_chart(
            fig,
            width='stretch',
        )

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        daily = (
            clean.groupby("Dia_Semana")["Total"]
            .sum()
            .reindex(days)
        )

        fig = px.bar(
            daily,
            title="Ventas por día de la semana",
        )

        st.plotly_chart(
            fig,
            width='stretch',
        )

        heat = clean.pivot_table(
            values="Total",
            index="Dia_Semana",
            columns="Hora",
            aggfunc="sum",
            fill_value=0,
        ).reindex(days)

        fig = px.imshow(
            heat,
            aspect="auto",
            title="Mapa de calor — Día vs Hora",
        )

        st.plotly_chart(
            fig,
            width='stretch',
        )

    # --------------------------------------------------------
    # Clientes
    # --------------------------------------------------------

    with tabs[6]:

        customers = (
            clean.groupby("CustomerID")
            .agg(
                Ventas=("Total", "sum"),
                Facturas=("Invoice", "nunique"),
                Productos=("StockCode", "nunique"),
                Unidades=("Quantity", "sum"),
            )
        )

        customers["Ticket"] = (
            customers["Ventas"] /
            customers["Facturas"]
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Clientes",
            f"{len(customers):,}",
        )

        c2.metric(
            "Venta media",
            money(
                customers["Ventas"].mean()
            ),
        )

        c3.metric(
            "Compras medias",
            f"{customers['Facturas'].mean():.2f}",
        )

        c4.metric(
            "Ticket medio",
            money(
                customers["Ticket"].mean()
            ),
        )

        c1, c2 = st.columns(2)

        top_sales = (
            customers
            .nlargest(
                20,
                "Ventas",
            )
            .sort_values("Ventas")
        )

        with c1:

            fig = px.bar(
                top_sales,
                x="Ventas",
                y=top_sales.index.astype(str),
                orientation="h",
                title="Top 20 clientes por facturación",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        top_frequency = (
            customers
            .nlargest(
                20,
                "Facturas",
            )
            .sort_values("Facturas")
        )

        with c2:

            fig = px.bar(
                top_frequency,
                x="Facturas",
                y=top_frequency.index.astype(str),
                orientation="h",
                title="Top 20 clientes por frecuencia",
            )

            st.plotly_chart(
                fig,
                width='stretch',
            )

        fig = px.scatter(
            customers,
            x="Facturas",
            y="Ventas",
            opacity=0.5,
            title="Frecuencia vs facturación",
        )

        st.plotly_chart(
            fig,
            width='stretch',
        )

        median_sales = customers["Ventas"].median()
        median_frequency = customers["Facturas"].median()

        customers["Segmento"] = np.select(
            [
                (
                    customers["Ventas"]
                    >= median_sales
                )
                & (
                    customers["Facturas"]
                    >= median_frequency
                ),
                (
                    customers["Ventas"]
                    >= median_sales
                )
                & (
                    customers["Facturas"]
                    < median_frequency
                ),
                (
                    customers["Ventas"]
                    < median_sales
                )
                & (
                    customers["Facturas"]
                    >= median_frequency
                ),
            ],
            [
                "Alto valor y frecuente",
                "Alto valor y ocasional",
                "Bajo valor y frecuente",
            ],
            default="Bajo valor y ocasional",
        )

        segments = (
            customers["Segmento"]
            .value_counts()
            .reset_index()
        )

        segments.columns = [
            "Segmento",
            "Clientes",
        ]

        fig = px.bar(
            segments,
            x="Segmento",
            y="Clientes",
            title="Segmentación básica",
        )

        st.plotly_chart(
            fig,
            width='stretch',
        )

        insight(
            "El análisis de clientes permite diferenciar frecuencia "
            "y valor económico, preparando el terreno para "
            "personalizar recomendaciones."
        )


# ============================================================
# 03 HALLAZGOS
# ============================================================

elif seccion == "03 · Hallazgos":

    section_title(
        "03 · ¿Qué descubrimos?",
        "La etapa de EDA debe terminar en decisiones de modelado.",
    )

    raw = load_eda_data()

    if raw is None:
        st.warning("No se encontró el dataset.")
        st.stop()

    clean, meta = clean_eda_data(raw)

    sales = clean["Total"].sum()
    invoices = clean["Invoice"].nunique()
    customers = clean["CustomerID"].nunique()
    products = clean["StockCode"].nunique()
    ticket = (
        sales / invoices
        if invoices
        else 0
    )

    top_product = (
        clean.groupby("Description")["Quantity"]
        .sum()
        .idxmax()
    )

    top_country = (
        clean.groupby("Country")["Total"]
        .sum()
        .idxmax()
    )

    basket = (
        clean.groupby("Invoice")["StockCode"]
        .nunique()
    )

    customer_sales = (
        clean.groupby("CustomerID")["Total"]
        .sum()
    )

    top10_share = (
        customer_sales.nlargest(10).sum()
        / customer_sales.sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Ventas",
        money(sales),
    )

    c2.metric(
        "Facturas",
        f"{invoices:,}",
    )

    c3.metric(
        "Clientes",
        f"{customers:,}",
    )

    c4.metric(
        "Ticket",
        money(ticket),
    )

    st.divider()

    findings = [
        (
            "🛒 Comportamiento de compra",
            f"El Basket Size promedio es "
            f"{basket.mean():.2f} productos diferentes "
            "por factura.",
        ),
        (
            "📦 Productos",
            f"El producto con mayor cantidad vendida es "
            f"'{top_product}'.",
        ),
        (
            "🌎 Geografía",
            f"El país con mayor facturación es "
            f"{top_country}.",
        ),
        (
            "👥 Clientes",
            f"Los 10 principales clientes concentran "
            f"{top10_share:.2%} de la facturación.",
        ),
        (
            "🤝 Venta cruzada",
            "La coocurrencia muestra productos que aparecen "
            "juntos en una misma factura.",
        ),
        (
            "🤖 Modelado",
            "Los patrones observados permiten probar modelos "
            "de popularidad, similitud, filtrado colaborativo "
            "y asociación.",
        ),
    ]

    for title, text in findings:

        st.markdown(
            f"""
            <div class="story">
                <h4>{title}</h4>
                <p>{text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader(
        "Del EDA al modelo"
    )

    bridge = pd.DataFrame(
        {
            "Hallazgo": [
                "Productos frecuentes",
                "Productos similares",
                "Compras repetidas",
                "Productos juntos",
            ],
            "Modelo / enfoque": [
                "Popularidad",
                "Item-Based CF",
                "ALS",
                "FP-Growth",
            ],
        }
    )

    st.dataframe(
        bridge,
        width='stretch',
        hide_index=True,
    )


# ============================================================
# 04 MODELOS
# ============================================================

elif seccion == "04 · Modelos":

    section_title(
        "04 · Modelos de recomendación",
        "Cuatro enfoques para transformar patrones históricos en recomendaciones.",
    )

    models = pd.DataFrame(
        {
            "Modelo": [
                "Popularidad",
                "Item-Based CF",
                "ALS",
                "FP-Growth",
            ],
            "Pregunta que responde": [
                "¿Qué productos son más populares?",
                "¿Qué productos son similares?",
                "¿Qué productos puede preferir este cliente?",
                "¿Qué productos suelen comprarse juntos?",
            ],
        }
    )

    st.dataframe(
        models,
        width='stretch',
        hide_index=True,
    )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        st.subheader(
            "1. Popularidad"
        )

        st.write(
            "Sirve como línea base. Recomienda los productos "
            "más frecuentes del conjunto de entrenamiento."
        )

        st.info(
            "Ventaja: simple y rápido. "
            "Limitación: no personaliza."
        )

        st.subheader(
            "2. Item-Based Collaborative Filtering"
        )

        st.write(
            "Utiliza la similitud entre productos para encontrar "
            "artículos relacionados con el historial del cliente."
        )

    with c2:

        st.subheader(
            "3. ALS"
        )

        st.write(
            "Aprende patrones latentes de interacción entre "
            "clientes y productos."
        )

        st.success(
            "En la evaluación actual obtiene la mayor Precision@10."
        )

        st.subheader(
            "4. FP-Growth"
        )

        st.write(
            "Identifica asociaciones entre productos que aparecen "
            "dentro de las mismas facturas."
        )

        st.success(
            "Es especialmente útil para estrategias de "
            "cross-selling."
        )


# ============================================================
# 05 FUNCIONAMIENTO DEL MODELO
# ============================================================

elif seccion == "05 · Funcionamiento del modelo":

    render_funcionamiento_modelo()


# ============================================================
# 06 COMPARACIÓN
# ============================================================

elif seccion == "06 · Comparación":

    section_title(
        "06 · Evaluación de modelos",
        "No elegimos el modelo por intuición: lo comparamos con métricas.",
    )

    best_precision = METRICS.loc[
        METRICS["Precision@10"].idxmax()
    ]

    best_recall = METRICS.loc[
        METRICS["Recall@10"].idxmax()
    ]

    best_map = METRICS.loc[
        METRICS["MAP@10"].idxmax()
    ]

    best_coverage = METRICS.loc[
        METRICS["Coverage@10"].idxmax()
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🥇 Precision@10",
        percentage(
            best_precision["Precision@10"]
        ),
        best_precision["Modelo"],
    )

    c2.metric(
        "🥇 Recall@10",
        percentage(
            best_recall["Recall@10"]
        ),
        best_recall["Modelo"],
    )

    c3.metric(
        "🥇 MAP@10",
        percentage(
            best_map["MAP@10"]
        ),
        best_map["Modelo"],
    )

    c4.metric(
        "🥇 Coverage@10",
        percentage(
            best_coverage["Coverage@10"]
        ),
        best_coverage["Modelo"],
    )

    st.divider()

    display_metrics = METRICS.copy()

    for column in [
        "Precision@10",
        "Recall@10",
        "MAP@10",
        "Coverage@10",
    ]:
        display_metrics[column] = (
            display_metrics[column]
            .map(lambda x: f"{x:.2%}")
        )

    st.dataframe(
        display_metrics,
        width='stretch',
        hide_index=True,
    )

    chart = px.bar(
        METRICS,
        x="Modelo",
        y=[
            "Precision@10",
            "Recall@10",
            "MAP@10",
        ],
        barmode="group",
        title="Comparación de desempeño",
    )

    st.plotly_chart(
        chart,
        width='stretch',
    )

    st.subheader(
        "¿Cuál es el mejor?"
    )

    st.markdown(
        """
        **ALS** presenta la mejor Precision@10 con **16.31%**.

        **FP-Growth** presenta el mejor Recall@10 (**10.42%**),
        MAP@10 (**10.98%**) y Coverage@10 (**45.83%**).

        Por lo tanto, la elección depende del objetivo de negocio:
        precisión personalizada vs. amplitud de recomendaciones y
        venta cruzada.
        """
    )

    insight(
        "La evaluación muestra que no existe un único ganador en todas "
        "las dimensiones. ALS destaca por precisión, mientras FP-Growth "
        "destaca por cobertura y asociación de productos."
    )


# ============================================================
# 07 DEMO
# ============================================================

elif seccion == "07 · Demo recomendador":

    section_title(
        "07 · Demo del sistema de recomendación",
        "Aquí convertimos el análisis y los modelos en una experiencia de negocio.",
    )

    if MODEL_IMPORT_ERROR is not None:

        st.error(
            "No se pudo cargar el módulo del sistema de recomendación."
        )

        st.code(
            str(MODEL_IMPORT_ERROR)
        )

        st.markdown("### 📁 Estructura esperada")

        st.code(
            """Sistema_de_reomendacion/
├── streamlit_proyecto_completo_v4.py
├── data/
│   └── raw/
│       └── online_retail_II.csv
├── .env
└── src/
    ├── Modelos/
    │   ├── Modelos_juntos.py
    │   └── ft_engineering.py
    └── snowflake/
        ├── config.py
        └── load_data.py
""",
            language="text",
        )

        if MODEL_FILE is not None:
            st.info(
                f"Archivo encontrado: {MODEL_FILE}"
            )
        else:
            st.warning(
                "En tu captura, la carpeta src/Modelos parece contener "
                "solamente __pycache__. Si Modelos_juntos.py no está "
                "realmente allí, debes recuperar/copiar ese archivo "
                "desde tu versión anterior del proyecto."
            )

        st.stop()

    st.info(
        "#### Demo Recomendador http://127.0.0.1:8000/"
    )

    try:
        system = build_recommendation_system()

    except Exception as exc:

        st.error(
            "No fue posible cargar o preparar el sistema de recomendación."
        )

        st.exception(exc)
        st.stop()

    raw_df = system["raw_df"]
    train_matrix = system["train_matrix"]
    customer_map = system["customer_map"]
    item_map = system["item_map"]
    description_map = system["description_map"]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Transacciones",
        f"{len(raw_df):,}",
    )

    c2.metric(
        "Clientes evaluables",
        f"{len(customer_map):,}",
    )

    c3.metric(
        "Productos",
        f"{len(item_map):,}",
    )

    st.divider()

    model = st.selectbox(
        "Selecciona el modelo",
        [
            "ALS",
            "Item-Based CF",
            "Popularidad (Top-K)",
            "FP-Growth",
        ],
    )

    k = st.slider(
        "Número de recomendaciones",
        3,
        20,
        10,
    )

    if model == "FP-Growth":

        fp_basket = system[
            "basket_matrix"
        ]

        fp_map = system[
            "fp_description_map"
        ]

        stock_codes = list(
            fp_basket.columns
        )

        options = {
            (
                f"{code} — "
                f"{product_name(code, fp_map)}"
            ): code
            for code in stock_codes
        }

        selected_label = st.selectbox(
            "Producto que el cliente ya tiene en la cesta",
            list(options.keys()),
        )

        selected_stock = options[
            selected_label
        ]

        if st.button(
            "🔎 Generar recomendaciones",
            type="primary",
        ):

            recs = recommend_fp_growth(
                selected_stock,
                fp_basket,
                k=k,
            )

            st.markdown(
                "### Productos recomendados"
            )

            if recs:

                table = fp_recommendation_table(
                    recs,
                    fp_map,
                )

                st.dataframe(
                    table,
                    width='stretch',
                    hide_index=True,
                )

            else:

                st.warning(
                    "No se encontraron recomendaciones "
                    "para este producto."
                )

    else:

        customer_to_code = {
            str(customer_id): internal_code
            for internal_code, customer_id
            in customer_map.items()
        }

        customer_options = sorted(
            customer_to_code.keys()
        )

        selected_customer = st.selectbox(
            "Selecciona el Customer ID",
            customer_options,
        )

        customer_code = customer_to_code[
            selected_customer
        ]

        if st.button(
            "🔎 Generar recomendaciones",
            type="primary",
        ):

            if train_matrix[
                customer_code
            ].nnz == 0:

                st.warning(
                    "El cliente no tiene historial "
                    "suficiente en entrenamiento."
                )

                st.stop()

            if model == "ALS":

                recs = recommend_als(
                    system["als_model"],
                    customer_code,
                    train_matrix,
                    k=k,
                )

            elif model == "Item-Based CF":

                recs = recommend_cf(
                    customer_code,
                    train_matrix,
                    system[
                        "item_similarity"
                    ],
                    k=k,
                )

            else:

                recs = top_k_items(
                    train_matrix,
                    k=k,
                )

            st.markdown(
                f"### Recomendaciones para "
                f"el cliente **{selected_customer}**"
            )

            table = recommendation_table(
                recs,
                item_map,
                description_map,
            )

            st.dataframe(
                table,
                width='stretch',
                hide_index=True,
            )

    st.divider()

    explanations = {
        "ALS": (
            "Recomienda a partir de patrones latentes de interacción "
            "entre clientes y productos."
        ),
        "Item-Based CF": (
            "Busca productos relacionados con los productos que "
            "el cliente ya compró."
        ),
        "Popularidad (Top-K)": (
            "Recomienda los productos más populares. Es la línea base."
        ),
        "FP-Growth": (
            "Recomienda productos que suelen aparecer junto con "
            "el producto seleccionado."
        ),
    }

    st.info(
        f"**Cómo funciona {model}:** "
        f"{explanations[model]}"
    )


# ============================================================
# 08 CIERRE
# ============================================================

elif seccion == "08 · Cierre":

    section_title(
        "07 · Conclusión del proyecto",
        "De los datos a una decisión.",
    )

    st.success("🎯 La historia completa")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            """
            **🎯 1. Problema**

            Necesitamos personalizar la experiencia y encontrar
            oportunidades de venta cruzada.

            **🔎 2. EDA**

            Encontramos patrones de comportamiento, productos
            relacionados, concentración de clientes y patrones temporales.

            **🤖 3. Modelos**

            Probamos cuatro enfoques diferentes.
            """
        )

    with c2:
        st.markdown(
            """
            **📊 4. Evaluación**

            ALS obtuvo la mejor **Precision@10**, mientras FP-Growth
            destacó en **Recall, MAP y Coverage**.

            **🚀 5. Aplicación**

            El sistema genera recomendaciones que pueden utilizarse
            para personalización y estrategias de **cross-selling**.
            """
        )

    st.subheader(
        "Resultado clave"
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "ALS · Precision@10",
            "16.44%",
        )

        st.write(
            "Es el modelo con mayor precisión en la evaluación actual."
        )

    with c2:
        st.metric(
            "FP-Growth · Coverage@10",
            "45.83%",
        )

        st.write(
            "Presenta la mayor cobertura y es especialmente útil "
            "para recomendaciones de productos asociados."
        )

    st.divider()

    st.subheader(
        "Mensaje final para negocio"
    )

    st.markdown(
        """
        > **No se trata solamente de recomendar productos.**
        >
        > Se trata de transformar el comportamiento histórico de compra
        > en una herramienta para tomar mejores decisiones comerciales.
        """
    )

    st.success(
        "EDA → patrones → modelos → evaluación → recomendación."
    )