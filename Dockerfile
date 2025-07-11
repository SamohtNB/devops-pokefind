### Stage « backend » ###
FROM python:3.10-slim AS backend
WORKDIR /app

# Créer un utilisateur non-root
RUN addgroup --system app && adduser --system --group app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/src ./src
COPY backend/src/model.pth ./model.pth

ENV PYTHONUNBUFFERED=1
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]


### Stage « builder » pour le frontend ###
FROM node:18-alpine AS builder
WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend ./
RUN npm run build


### Stage « frontend » final ###
FROM nginx:alpine AS frontend
COPY --from=builder /app/build /usr/share/nginx/html

# Copier une config nginx personnalisée (SPA fallback, caching…)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
