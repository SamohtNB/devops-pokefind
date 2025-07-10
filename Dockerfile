FROM python:3.10-slim

# 1. Crée et définis le répertoire de travail
WORKDIR /app

# 2. Copie et installe les dépendances Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copie le code de l’API
COPY backend/src/ ./src/

# 4. (Optionnel) Copie un .env si tu veux des valeurs par défaut
#    tu peux aussi passer tes variables MLflow / DagsHub au runtime
# COPY .env .

# 5. Expose le port 8000 (FastAPI)
EXPOSE 8000

# 6. Définit les variables d’environnement pour la production
#    Remplace ou surcharge avec docker-compose / ton orchestrateur si besoin
ENV MLFLOW_TRACKING_URI=https://dagshub.com/Marco2a94/final-project.mlflow
ENV MLFLOW_TRACKING_USERNAME=Marco2a94
# ENV MLFLOW_TRACKING_PASSWORD=ton_token_dagshub

# Copie du modèle entraîné dans l'image
COPY model.pth .

# 7. Commande de lancement de l’app FastAPI
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
