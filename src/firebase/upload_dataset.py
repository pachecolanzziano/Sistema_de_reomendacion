from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from firebase_config import get_firestore_client

# ---------------------------------------------------------
# Configuración
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "src" / "DataSetLimpio.csv"
COLLECTION_NAME = "transacciones"  # Nombre de la colección donde irán los documentos
BATCH_SIZE = 500  # Máximo de operaciones por lote

# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------

def upload_dataset_in_batches():
    """
    Lee DataSetLimpio.csv por partes (chunks) y sube cada fila
    como un documento individual a Firestore, en lotes de BATCH_SIZE.
    """
    # 1. Verificar que el CSV exista
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {CSV_PATH}")
    print(f"📁 CSV encontrado: {CSV_PATH}")

    # 2. Conectar a Firestore
    db = get_firestore_client()
    print("🔌 Conectado a Firestore.")

    # 3. Leer el CSV por partes (chunks) para ahorrar memoria
    total_rows = 0
    total_batches = 0
    chunk_size = 10000  # Número de filas por chunk

    print("📤 Iniciando carga por lotes...")
    for chunk in pd.read_csv(CSV_PATH, chunksize=chunk_size):
        batch = db.batch()
        batch_count = 0

        for _, row in chunk.iterrows():
            # Convertir la fila a diccionario
            doc_data = row.to_dict()
            
            # Crear un nuevo documento con ID automático
            doc_ref = db.collection(COLLECTION_NAME).document()
            batch.set(doc_ref, doc_data)
            
            batch_count += 1
            total_rows += 1

            # Si llegamos al límite del lote, lo ejecutamos
            if batch_count >= BATCH_SIZE:
                batch.commit()
                total_batches += 1
                print(f"✅ Lote {total_batches} subido ({total_rows} registros hasta ahora)")
                
                # Empezar un nuevo lote
                batch = db.batch()
                batch_count = 0

        # Subir el último lote del chunk (si quedaron operaciones pendientes)
        if batch_count > 0:
            batch.commit()
            total_batches += 1
            print(f"✅ Lote {total_batches} subido ({total_rows} registros hasta ahora)")

    print("\n🎉 ¡Carga completada!")
    print(f"📊 Total de registros: {total_rows}")
    print(f"📂 Colección: {COLLECTION_NAME}")
    print(f"📦 Total de lotes: {total_batches}")

    # 4. Guardar metadatos de la carga en otro documento (opcional)
    metadata_ref = db.collection("_metadata").document("dataset_info")
    metadata_ref.set({
        "collection_name": COLLECTION_NAME,
        "total_records": total_rows,
        "uploaded_at": datetime.now(timezone.utc),
        "source_file": CSV_PATH.name,
        "batch_size": BATCH_SIZE,
        "total_batches": total_batches
    })
    print("📋 Metadatos guardados en _metadata/dataset_info")

# ---------------------------------------------------------
# Ejecución
# ---------------------------------------------------------

if __name__ == "__main__":
    upload_dataset_in_batches()