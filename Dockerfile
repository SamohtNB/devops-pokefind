### Stage “backend” ###
FROM python:3.10-slim AS backend
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY backend .  

# Copier le modèle depuis le dossier backend
COPY backend/src/model.pth .

EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

### Stage “frontend” ###
FROM node:18-alpine AS frontend
WORKDIR /app

COPY frontend/package*.json ./
RUN npm install
COPY frontend .
RUN npm run build

FROM nginx:alpine AS nginx
COPY --from=frontend /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
