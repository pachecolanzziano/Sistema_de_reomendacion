# load_dataset.py (MODIFICADO)
import pandas as pd
import io
from firebase_config import get_storage_client  # <-- CAMBIAR import

BLOB_PATH = "datasets/DataSetLimpio.csv"  # <-- Misma ruta que en upload

def load_dataset():
    """Lee el CSV desde Cloud Storage y devuelve un DataFrame."""
    # 1. Conectar a Cloud Storage
    bucket = get_storage_client()
    print("🔌 Conectado a Cloud Storage.")

    # 2. Verificar que el archivo existe
    blob = bucket.blob(BLOB_PATH)
    if not blob.exists():
        raise FileNotFoundError(f"No se encontró el archivo en Cloud Storage: {BLOB_PATH}")
    print(f"📁 Archivo encontrado: {BLOB_PATH}")
    print(f"📏 Tamaño: {blob.size / (1024*1024):.2f} MB")

    # 3. Descargar el archivo a memoria
    print("📥 Descargando archivo...")
    data = blob.download_as_text()
    print("✅ Archivo descargado.")

    # 4. Cargar en DataFrame
    df = pd.read_csv(io.StringIO(data))
    print(f"📊 DataFrame cargado: {len(df)} registros, {len(df.columns)} columnas")
    return df

def load_dataset_sample(n_rows=1000):
    """Lee solo las primeras N filas del CSV (para pruebas rápidas)."""
    # 1. Conectar a Cloud Storage
    bucket = get_storage_client()
    blob = bucket.blob(BLOB_PATH)
    if not blob.exists():
        raise FileNotFoundError(f"No se encontró el archivo en Cloud Storage: {BLOB_PATH}")

    # 2. Descargar solo las primeras líneas
    # (Esto es más eficiente que descargar todo el archivo)
    import requests
    url = f"https://storage.googleapis.com/{bucket.name}/{BLOB_PATH}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Error al descargar el archivo: {response.status_code}")
    
    # Leer solo las primeras n filas
    from io import StringIO
    lines = response.text.split('\n')
    header = lines[0]
    sample = header + '\n' + '\n'.join(lines[1:n_rows+1])
    df = pd.read_csv(StringIO(sample))
    print(f"📊 Muestra cargada: {len(df)} registros")
    return df

if __name__ == "__main__":
    # Para pruebas completas:
    df = load_dataset()
    print(df.head())
    
    # O para pruebas rápidas:
    # df = load_dataset_sample(1000)
    # print(df.head())