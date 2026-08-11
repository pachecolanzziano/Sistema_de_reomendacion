import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv


# ---------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------

# firebase_config.py
#       ↓
# firebase/
#       ↓
# src/
#       ↓
# SISTEMA_DE_RECOMENDACION/
PROJECT_ROOT = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_ROOT / ".env"


# ---------------------------------------------------------
# Cargar variables de entorno
# ---------------------------------------------------------

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# Crear / obtener conexión con Firestore
# ---------------------------------------------------------

def get_firestore_client():
    """
    Inicializa Firebase y devuelve el cliente de Firestore.

    Si Firebase ya fue inicializado, reutiliza la aplicación
    existente.
    """

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if not credentials_path:
        raise ValueError(
            "No se encontró FIREBASE_CREDENTIALS_PATH en el archivo .env"
        )

    # Si la ruta del .env es relativa, la interpretamos
    # respecto a la raíz del proyecto.
    credentials_path = Path(credentials_path)

    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path

    credentials_path = credentials_path.resolve()

    # Verificar que exista el archivo de credenciales
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales: "
            f"{credentials_path}"
        )

    # Comprobar si Firebase ya fue inicializado
    try:
        firebase_admin.get_app()

    except ValueError:
        # Firebase todavía no ha sido inicializado
        cred = credentials.Certificate(str(credentials_path))

        firebase_admin.initialize_app(cred)

    # Obtener cliente de Firestore
    db = firestore.client()

    return db