FROM python:3.10-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code FastAPI
COPY backend/src/ ./src/
# Copie du modèle entraîné
COPY model.pth .
# Copie du dossier data/raw pour détecter les classes
COPY data/raw/ data/raw/

EXPOSE 8000
ENV MODEL_PATH="model.pth"
ENV RAW_DIR="data/raw"

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
