#!/bin/sh
# entrypoint.sh

# Valeur par défaut si PORT non défini
PORT="${PORT:-80}"

echo "🚀 Starting server: listening on port $PORT"

# Lancement de nginx, en injectant le port dans la conf si besoin
# (pour nginx.conf custom, on suppose que listen $PORT; y est déjà)
exec nginx -g "daemon off;"
