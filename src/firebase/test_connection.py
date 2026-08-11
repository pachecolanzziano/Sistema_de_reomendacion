from firebase_config import get_firestore_client


def main():
    print("Intentando conectar con Firestore...")

    db = get_firestore_client()

    print("Conexión exitosa con Firestore.")
    print(f"Cliente: {db}")


if __name__ == "__main__":
    main()