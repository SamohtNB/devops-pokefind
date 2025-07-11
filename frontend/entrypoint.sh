#!/bin/sh

# Par défaut, port interne nginx
PORT="${PORT:-80}"
# Port sur lequel on accède depuis l'hôte
HOST_PORT="${HOST_PORT:-3000}"

# On affiche un lien cliquable vers localhost
echo "🚀 Votre application est disponible ici → http://localhost:${HOST_PORT}"

# On démarre Nginx
exec nginx -g "daemon off;"
