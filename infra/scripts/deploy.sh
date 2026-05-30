#!/bin/bash
# Deploy script para UNIR Platform API
# Uso: bash infra/scripts/deploy.sh

set -e

echo "=== UNIR Platform API - Deploy ==="

cd "$(dirname "$0")/../.."

# 1. Git pull
echo "[1/4] Atualizar código..."
git pull origin main

# 2. Docker build
echo "[2/4] Build Docker image..."
docker compose build api

# 3. Parar serviço atual
echo "[3/4] Parar serviço atual..."
docker compose down api 2>/dev/null || true

# 4. Iniciar novo
echo "[4/4] Iniciar novo serviço..."
docker compose up -d api

echo "=== Deploy concluído ==="
echo "API: http://localhost:8001"
echo "Docs: http://localhost:8001/docs"
