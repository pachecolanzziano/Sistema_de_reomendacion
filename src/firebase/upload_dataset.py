from pathlib import Path
from datetime import datetime, timezone

from firebase_config import get_firestore_client


# ---------------------------------------------------------
# Configuración
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = PROJECT_ROOT / "src" / "DataSetLimpio.csv"

COLLECTION_NAME = "datasets"
DOCUMENT_ID = "retail_dataset"

# Límite interno de seguridad.
# Firestore permite documentos de hasta 1 MiB.
MAX_CSV_SIZE = 900 * 1024


# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------

def upload_dataset():
    """
    Lee DataSetLimpio.csv y lo almacena como un único
    documento dentro de Firestore.
    """

    # -----------------------------------------------------
    # 1. Verificar que exista el CSV
    # -----------------------------------------------------

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo CSV: {CSV_PATH}"
        )

    print(f"CSV encontrado: {CSV_PATH}")

    # -----------------------------------------------------
    # 2. Leer el CSV como texto
    # -----------------------------------------------------

    csv_text = CSV_PATH.read_text(
        encoding="utf-8"
    )

    # -----------------------------------------------------
    # 3. Calcular tamaño
    # -----------------------------------------------------

    csv_size = len(csv_text.encode("utf-8"))

    print(f"Tamaño del CSV: {csv_size / 1024:.2f} KB")

    if csv_size > MAX_CSV_SIZE:
        raise ValueError(
            "El CSV es demasiado grande para nuestra estrategia "
            "de almacenar todo el contenido en un único documento "
            f"de Firestore.\n"
            f"Tamaño: {csv_size / 1024:.2f} KB\n"
            f"Límite interno: {MAX_CSV_SIZE / 1024:.2f} KB"
        )

    # -----------------------------------------------------
    # 4. Obtener conexión
    # -----------------------------------------------------

    db = get_firestore_client()

    # -----------------------------------------------------
    # 5. Crear referencia al documento
    # -----------------------------------------------------

    document_ref = (
        db.collection(COLLECTION_NAME)
        .document(DOCUMENT_ID)
    )

    # -----------------------------------------------------
    # 6. Construir documento
    # -----------------------------------------------------

    data = {
        "filename": CSV_PATH.name,
        "csv_data": csv_text,
        "size_bytes": csv_size,
        "uploaded_at": datetime.now(timezone.utc),
    }

    # -----------------------------------------------------
    # 7. Guardar documento
    # -----------------------------------------------------

    document_ref.set(data)

    print()
    print("Dataset cargado correctamente.")
    print(f"Colección: {COLLECTION_NAME}")
    print(f"Documento: {DOCUMENT_ID}")


# ---------------------------------------------------------
# Ejecución
# ---------------------------------------------------------

if __name__ == "__main__":
    upload_dataset()