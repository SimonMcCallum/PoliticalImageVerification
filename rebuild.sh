#!/bin/bash
# PIVS rebuild & restart script
# Usage: sudo bash rebuild.sh [--no-cache]

set -e

COMPOSE="/home/simon/docker/docker-compose.yml"
NOCACHE=""

if [ "$1" = "--no-cache" ]; then
    NOCACHE="--no-cache"
    echo "=== Building with --no-cache ==="
fi

echo "=== Building pivs-server and pivs-client ==="
docker compose -f "$COMPOSE" build $NOCACHE pivs-server pivs-client

echo ""
echo "=== Recreating containers ==="
docker compose -f "$COMPOSE" up -d pivs-server pivs-client

echo ""
echo "=== Restarting pivs-nginx (picks up config changes) ==="
docker restart pivs-nginx

echo ""
echo "=== Waiting 5 seconds for startup ==="
sleep 5

echo ""
echo "=== Container status ==="
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E 'pivs|NAMES'

echo ""
echo "=== Server health check ==="
docker exec pivs-nginx curl -sf http://localhost/health 2>&1 || echo "FAILED - server not responding"

echo ""
echo "=== Client check (verify page returns HTML) ==="
docker exec pivs-nginx curl -sf http://localhost/verify/ 2>&1 | head -5 || echo "FAILED - client not responding"

echo ""
echo "=== Subpath API check ==="
docker exec pivs-nginx curl -sf http://localhost/verify/health 2>&1 || echo "FAILED - /verify/health not routing"

echo ""
echo "=== Server logs (last 10 lines) ==="
docker logs pivs-server --tail 10 2>&1

echo ""
echo "=== Done ==="
