# firebase_config.py (MODIFICADO)
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage  # <-- AÑADIR storage
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)

def get_firestore_client():
    """Inicializa Firebase y devuelve el cliente de Firestore."""
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if not credentials_path:
        raise ValueError("No se encontró FIREBASE_CREDENTIALS_PATH en .env")
    credentials_path = Path(credentials_path)
    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path
    credentials_path = credentials_path.resolve()
    if not credentials_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales: {credentials_path}")

    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(str(credentials_path))
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')  # <-- NUEVO
        })

    return firestore.client()

# ============================================
# NUEVA FUNCIÓN PARA CLOUD STORAGE
# ============================================

def get_storage_client():
    """
    Inicializa Firebase (si no está inicializado) y devuelve
    el cliente de Cloud Storage.
    """
    # Asegurar que Firebase está inicializado
    try:
        firebase_admin.get_app()
    except ValueError:
        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if not credentials_path:
            raise ValueError("No se encontró FIREBASE_CREDENTIALS_PATH en .env")
        credentials_path = Path(credentials_path)
        if not credentials_path.is_absolute():
            credentials_path = PROJECT_ROOT / credentials_path
        credentials_path = credentials_path.resolve()
        if not credentials_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de credenciales: {credentials_path}")
        
        cred = credentials.Certificate(str(credentials_path))
        firebase_admin.initialize_app(cred, {
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
        })

    # Obtener el bucket por defecto
    bucket = storage.bucket()
    return bucket