import pandas as pd
from firebase_config import get_firestore_client

# ---------------------------------------------------------
# Configuración
# ---------------------------------------------------------

COLLECTION_NAME = "transacciones"  # Debe coincidir con el usado en upload_dataset.py

# ---------------------------------------------------------
# Función principal
# ---------------------------------------------------------

def load_dataset():
    """
    Recupera TODOS los documentos de la colección especificada
    y los devuelve como un pandas DataFrame.
    """
    db = get_firestore_client()
    print("🔌 Conectado a Firestore.")

    # Obtener todos los documentos de la colección
    docs = db.collection(COLLECTION_NAME).stream()
    
    data = []
    doc_count = 0
    
    print(f"📥 Descargando documentos de la colección '{COLLECTION_NAME}'...")
    for doc in docs:
        doc_data = doc.to_dict()
        data.append(doc_data)
        doc_count += 1
        
        # Mostrar progreso cada 10,000 documentos
        if doc_count % 10000 == 0:
            print(f"   📄 {doc_count} documentos descargados...")

    # Crear DataFrame
    df = pd.DataFrame(data)
    print(f"\n✅ Descarga completada: {len(df)} registros en el DataFrame.")
    return df

# ---------------------------------------------------------
# Función para descargar solo una muestra (para pruebas)
# ---------------------------------------------------------

def load_dataset_sample(limit=1000):
    """
    Descarga solo una muestra de los primeros 'limit' documentos.
    Útil para pruebas rápidas.
    """
    db = get_firestore_client()
    docs = db.collection(COLLECTION_NAME).limit(limit).stream()
    
    data = [doc.to_dict() for doc in docs]
    df = pd.DataFrame(data)
    print(f"📊 Muestra descargada: {len(df)} registros.")
    return df

# ---------------------------------------------------------
# Ejecución
# ---------------------------------------------------------

if __name__ == "__main__":
    # Para pruebas con todos los datos:
    df = load_dataset()
    
    # Para pruebas rápidas con una muestra:
    # df = load_dataset_sample(1000)
    
    print("\n📊 Información del DataFrame:")
    print(f"Filas: {len(df)}")
    print(f"Columnas: {len(df.columns)}")
    print("\nColumnas:")
    print(df.columns.tolist())
    print("\nPrimeras 5 filas:")
    print(df.head())