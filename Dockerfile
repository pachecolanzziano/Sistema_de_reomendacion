# Imagen para servir la API de recomendaciones (ALS + FP-Growth + baseline).
#
# IMPORTANTE: antes de construir esta imagen, genera los artefactos
# entrenados corriendo (con acceso a Snowflake, fuera de Docker):
#     python -m src.api.train_and_export
# Eso crea src/api/artifacts/ (als_model.npz, train_matrix.npz, artifacts.pkl),
# que este Dockerfile copia dentro de la imagen. Sin esa carpeta, el
# contenedor arranca pero falla al buscar los artefactos.
#
# Construir (desde la raíz del proyecto, donde está este archivo):
#     docker build -t recomendador-api .
# Correr:
#     docker run -p 8000:8000 recomendador-api

FROM python:3.11-slim

# <-- Colócalo aquí mero:
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# (Aquí continúa el resto de tus copias de archivos hacia abajo...)

WORKDIR /app

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Solo lo que main.py necesita en runtime: código de servir + artefactos ya
# entrenados. NO se copian ft_engineering2.py, train_and_export.py, ni
# src/snowflake — el contenedor no necesita conectarse a Snowflake.
COPY src/api/main.py src/api/Modelos_top.py /app/src/api/
COPY src/api/static /app/src/api/static
COPY src/api/artifacts /app/src/api/artifacts
COPY src/__init__.py /app/src/__init__.py
COPY src/api/__init__.py /app/src/api/__init__.py

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
