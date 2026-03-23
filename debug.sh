#!/bin/bash
# PIVS routing debug script
# Usage: sudo bash debug.sh

echo "=== 1. Container status ==="
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'pivs|nginx-proxy|NAMES'

echo ""
echo "=== 2. pivs-client responding? (wget) ==="
docker exec pivs-client wget -qS -O /dev/null http://localhost:3000/verify/ 2>&1 | head -10

echo ""
echo "=== 3. pivs-client without basePath? ==="
docker exec pivs-client wget -qS -O /dev/null http://localhost:3000/ 2>&1 | head -10

echo ""
echo "=== 4. pivs-nginx → client routing ==="
docker exec pivs-nginx wget -qS -O /dev/null http://localhost/verify/ 2>&1 | head -10

echo ""
echo "=== 5. pivs-nginx → API health ==="
docker exec pivs-nginx wget -qS -O /dev/null http://localhost/health 2>&1 | head -10

echo ""
echo "=== 6. pivs-nginx → /verify/health ==="
docker exec pivs-nginx wget -qS -O /dev/null http://localhost/verify/health 2>&1 | head -10

echo ""
echo "=== 7. pivs-nginx config check ==="
docker exec pivs-nginx nginx -T 2>&1 | grep -E "include.*mime|location /verify|proxy_pass" | head -20

echo ""
echo "=== 8. NPM config files mentioning pivs or simonmccallum ==="
find /home/simon/docker/nginx-proxy-manager/data/nginx -name "*.conf" 2>/dev/null | while read f; do
    if grep -ql "simonmccallum\|pivs" "$f" 2>/dev/null; then
        echo "--- $f ---"
        cat "$f"
        echo ""
    fi
done

echo ""
echo "=== 9. pivs-server logs (last 15 lines) ==="
docker logs pivs-server --tail 15 2>&1

echo ""
echo "=== 10. pivs-nginx logs (last 15 lines) ==="
docker logs pivs-nginx --tail 15 2>&1

echo ""
echo "=== Done ==="
