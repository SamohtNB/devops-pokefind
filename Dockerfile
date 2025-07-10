FROM python:3.10-slim
WORKDIR /app

# 1. Installer les dépendances
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copier le code FastAPI
COPY backend/src/ ./src/

# 3. Copier le modèle entraîné (sans slash au début)
COPY backend/src/model.pth .

# 4. Copier le dossier data/raw pour la détection automatique des classes
COPY data/raw/ data/raw/

EXPOSE 8000

# 5. Variables d’env pour app.py
ENV MODEL_PATH="model.pth"
ENV RAW_DIR="data/raw"

# 6. Lancement de l’API
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
