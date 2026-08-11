# upload_dataset.py (MODIFICADO)
from pathlib import Path
from datetime import datetime, timezone
from firebase_config import get_storage_client  # <-- CAMBIAR import

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_PATH = PROJECT_ROOT / "src" / "DataSetLimpio.csv"
BLOB_PATH = "datasets/DataSetLimpio.csv"  # <-- Ruta dentro del bucket

def upload_dataset():
    """Sube el CSV completo a Cloud Storage."""
    # 1. Verificar que el CSV exista
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {CSV_PATH}")
    print(f"📁 CSV encontrado: {CSV_PATH}")
    print(f"📏 Tamaño: {CSV_PATH.stat().st_size / (1024*1024):.2f} MB")

    # 2. Conectar a Cloud Storage
    bucket = get_storage_client()
    print("🔌 Conectado a Cloud Storage.")

    # 3. Subir el archivo
    blob = bucket.blob(BLOB_PATH)
    blob.upload_from_filename(str(CSV_PATH))

    print("\n🎉 ¡Carga completada!")
    print(f"📂 Bucket: {bucket.name}")
    print(f"📄 Archivo: {BLOB_PATH}")

    # 4. Guardar metadatos en Firestore (opcional, pero útil)
    from firebase_config import get_firestore_client
    db = get_firestore_client()
    metadata_ref = db.collection("_metadata").document("dataset_info")
    metadata_ref.set({
        "storage_path": BLOB_PATH,
        "bucket": bucket.name,
        "uploaded_at": datetime.now(timezone.utc),
        "size_bytes": CSV_PATH.stat().st_size,
        "source_file": CSV_PATH.name,
        "total_records": 0  # Puedes actualizarlo después de leer el CSV
    })
    print("📋 Metadatos guardados en Firestore.")

if __name__ == "__main__":
    upload_dataset()