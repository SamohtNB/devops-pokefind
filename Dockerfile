# syntax=docker/dockerfile:1.4

### Stage « backend » ###
FROM python:3.10-slim AS backend
WORKDIR /app

# (optionnel) créer un utilisateur non-root
RUN addgroup --system app && adduser --system --group app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier code, modèle et classes.json
COPY backend/src ./src
COPY backend/src/model.pth ./model.pth
COPY backend/src/classes.json ./classes.json

ENV PYTHONUNBUFFERED=1
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]


### Stage « builder » pour le frontend ###
FROM node:18-alpine AS builder

# Injecter l'URL du backend au build
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
RUN npm run build


### Stage « frontend » final ###
FROM nginx:alpine AS frontend
COPY --from=builder /app/build /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
