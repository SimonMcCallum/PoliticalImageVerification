#!/usr/bin/env bash
set -euo pipefail

# ══════════════════════════════════════════════════════════════════════
#  PIVS — NZ Political Image Verification System
#  Ubuntu deployment script
#
#  Installs as systemd services and integrates with system nginx.
#  Designed to coexist with other sites on the same server.
#
#  Usage:
#    sudo ./deploy.sh                  # Full install + start
#    sudo ./deploy.sh --stop           # Stop PIVS services
#    sudo ./deploy.sh --status         # Show service status
#    sudo ./deploy.sh --update         # Pull latest code and redeploy
#    sudo ./deploy.sh --uninstall      # Remove services (keeps data)
#
#  Prerequisites:
#    - Ubuntu 22.04+ / Debian 12+
#    - Git repo cloned to desired install path
#    - Run as root or with sudo
# ══════════════════════════════════════════════════════════════════════

PUBLIC_IP="103.224.130.189"
DOMAIN="${PIVS_DOMAIN:-$PUBLIC_IP}"          # set PIVS_DOMAIN for a real domain
APP_USER="pivs"
APP_GROUP="pivs"

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$PROJECT_ROOT/server"
CLIENT_DIR="$PROJECT_ROOT/client"
STORAGE_DIR="$SERVER_DIR/storage"
LOG_DIR="/var/log/pivs"
ENV_FILE="$SERVER_DIR/.env"
VENV_DIR="$SERVER_DIR/venv"

API_PORT=8000
CLIENT_PORT=3000
PG_PORT=5432

# ── Colours ───────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
step()  { echo -e "\n${CYAN}[$(date +%H:%M:%S)] $1${NC}"; }
ok()    { echo -e "  ${GREEN}OK:${NC} $1"; }
warn()  { echo -e "  ${YELLOW}WARN:${NC} $1"; }
fail()  { echo -e "  ${RED}FAIL:${NC} $1"; }

# ── Root check ────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo ./deploy.sh)"
    exit 1
fi

# ══════════════════════════════════════════════════════════════════════
#  --stop
# ══════════════════════════════════════════════════════════════════════
if [[ "${1:-}" == "--stop" ]]; then
    step "Stopping PIVS services"
    systemctl stop pivs-api.service pivs-client.service 2>/dev/null || true
    ok "Services stopped"
    systemctl status pivs-api.service pivs-client.service --no-pager 2>/dev/null || true
    exit 0
fi

# ══════════════════════════════════════════════════════════════════════
#  --status
# ══════════════════════════════════════════════════════════════════════
if [[ "${1:-}" == "--status" ]]; then
    echo -e "\n${CYAN}PIVS Service Status${NC}"
    echo "════════════════════════════════════════════"
    echo ""
    for svc in pivs-api pivs-client postgresql; do
        if systemctl is-active --quiet "$svc" 2>/dev/null; then
            echo -e "  ${GREEN}●${NC} $svc"
        else
            echo -e "  ${RED}●${NC} $svc"
        fi
    done
    echo ""

    # nginx site
    if [ -L /etc/nginx/sites-enabled/pivs ]; then
        echo -e "  ${GREEN}●${NC} nginx site (pivs)"
    else
        echo -e "  ${RED}●${NC} nginx site (pivs) — not enabled"
    fi

    echo ""
    echo "  Public URL:   http://$DOMAIN"
    echo "  API docs:     http://$DOMAIN/docs"
    echo ""
    echo "  Logs:"
    echo "    journalctl -u pivs-api -f"
    echo "    journalctl -u pivs-client -f"
    echo "    tail -f /var/log/nginx/pivs-*.log"
    echo ""
    exit 0
fi

# ══════════════════════════════════════════════════════════════════════
#  --uninstall
# ══════════════════════════════════════════════════════════════════════
if [[ "${1:-}" == "--uninstall" ]]; then
    step "Uninstalling PIVS services (data preserved)"
    systemctl stop pivs-api.service pivs-client.service 2>/dev/null || true
    systemctl disable pivs-api.service pivs-client.service 2>/dev/null || true
    rm -f /etc/systemd/system/pivs-api.service /etc/systemd/system/pivs-client.service
    rm -f /etc/nginx/sites-enabled/pivs
    systemctl daemon-reload
    nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null || true
    ok "Services removed. Database, storage, and code are preserved."
    exit 0
fi

# ══════════════════════════════════════════════════════════════════════
#  --update  (pull + redeploy without full install)
# ══════════════════════════════════════════════════════════════════════
if [[ "${1:-}" == "--update" ]]; then
    step "Pulling latest code"
    sudo -u "$APP_USER" git -C "$PROJECT_ROOT" pull --ff-only || {
        warn "git pull failed — do you have local changes?"
        exit 1
    }
    ok "Code updated"

    step "Updating Python dependencies"
    sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -q -r "$SERVER_DIR/requirements.txt"
    ok "Python deps updated"

    step "Rebuilding Next.js client"
    pushd "$CLIENT_DIR" > /dev/null
    sudo -u "$APP_USER" NEXT_PUBLIC_API_URL="http://$DOMAIN" npx next build
    popd > /dev/null
    ok "Client rebuilt"

    step "Restarting services"
    systemctl restart pivs-api.service pivs-client.service
    ok "Services restarted"
    exit 0
fi

# ══════════════════════════════════════════════════════════════════════
#  FULL INSTALL / DEPLOY
# ══════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}  ════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  NZ Political Image Verification System — Deploy${NC}"
echo -e "${CYAN}  Target: Ubuntu / Debian${NC}"
echo -e "${CYAN}  Public: http://$DOMAIN${NC}"
echo -e "${CYAN}  ════════════════════════════════════════════════════${NC}"

# ── 1. System packages ────────────────────────────────────────────────
step "Installing system dependencies"
apt-get update -qq
apt-get install -y -qq \
    python3 python3-venv python3-pip python3-dev \
    postgresql postgresql-contrib \
    nginx \
    nodejs npm \
    gcc libjpeg-dev libpng-dev libwebp-dev zlib1g-dev \
    tesseract-ocr tesseract-ocr-eng \
    curl git > /dev/null 2>&1
ok "System packages installed"

# Ensure Node.js is recent enough (need >= 18 for Next.js 15)
NODE_MAJOR=$(node --version 2>/dev/null | sed 's/v\([0-9]*\).*/\1/')
if [[ "$NODE_MAJOR" -lt 18 ]]; then
    warn "Node.js $NODE_MAJOR is too old for Next.js 15. Installing Node 20..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - > /dev/null 2>&1
    apt-get install -y -qq nodejs > /dev/null 2>&1
    ok "Node.js $(node --version) installed"
else
    ok "Node.js v$NODE_MAJOR is sufficient"
fi

# ── 2. Application user ──────────────────────────────────────────────
step "Creating application user"
if id "$APP_USER" &>/dev/null; then
    ok "User '$APP_USER' already exists"
else
    useradd --system --shell /usr/sbin/nologin --home-dir "$PROJECT_ROOT" "$APP_USER"
    ok "Created system user '$APP_USER'"
fi

# ── 3. Directory permissions ─────────────────────────────────────────
step "Setting up directories"
mkdir -p "$STORAGE_DIR"/{assets,badges,qrcodes,promoter,email_incoming,email_results}
mkdir -p "$LOG_DIR"
chown -R "$APP_USER:$APP_GROUP" "$PROJECT_ROOT"
chown -R "$APP_USER:$APP_GROUP" "$LOG_DIR"
ok "Directories ready"

# ── 4. PostgreSQL ─────────────────────────────────────────────────────
step "Configuring PostgreSQL"
systemctl enable postgresql
systemctl start postgresql

# Generate a random password for the pivs DB user
PG_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Create user + database if they don't exist
sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='pivs'" | grep -q 1 || {
    sudo -u postgres psql -c "CREATE USER pivs WITH PASSWORD '$PG_PASS';"
    ok "Created PostgreSQL user 'pivs'"
}
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='pivs'" | grep -q 1 || {
    sudo -u postgres psql -c "CREATE DATABASE pivs OWNER pivs;"
    ok "Created PostgreSQL database 'pivs'"
}
# Always update password to match what we'll write to .env
sudo -u postgres psql -c "ALTER USER pivs WITH PASSWORD '$PG_PASS';" > /dev/null
ok "PostgreSQL configured"

# ── 5. Python virtual environment ─────────────────────────────────────
step "Setting up Python environment"
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
    ok "Virtual environment created"
fi
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -q --upgrade pip
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -q -r "$SERVER_DIR/requirements.txt"
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -q gunicorn
ok "Python dependencies installed"

# ── 6. Production .env ────────────────────────────────────────────────
step "Generating production environment"
if [ -f "$ENV_FILE" ] && ! grep -q "dev-secret" "$ENV_FILE" 2>/dev/null; then
    ok ".env already exists with production values"
    # Still update the PG password
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://pivs:${PG_PASS}@localhost:${PG_PORT}/pivs|" "$ENV_FILE"
else
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    MASTER_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    cat > "$ENV_FILE" <<ENVEOF
# Production environment — generated by deploy.sh on $(date '+%Y-%m-%d %H:%M')
DATABASE_URL=postgresql+asyncpg://pivs:${PG_PASS}@localhost:${PG_PORT}/pivs
SECRET_KEY=${SECRET_KEY}
MASTER_ENCRYPTION_KEY=${MASTER_KEY}
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=${STORAGE_DIR}
VERIFICATION_BASE_URL=http://${DOMAIN}/verify
EMAIL_PROCESSING_ENABLED=false
ENVEOF

    chown "$APP_USER:$APP_GROUP" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    ok "Production .env generated (secrets in $ENV_FILE)"
fi

# ── 7. Seed database ─────────────────────────────────────────────────
step "Checking database seed"
PARTY_COUNT=$(sudo -u postgres psql -d pivs -tAc "SELECT COUNT(*) FROM parties" 2>/dev/null || echo "0")
if [[ "$PARTY_COUNT" == "0" || -z "$PARTY_COUNT" ]]; then
    warn "Database empty, running seed..."
    pushd "$SERVER_DIR" > /dev/null
    sudo -u "$APP_USER" PYTHONIOENCODING=utf-8 "$VENV_DIR/bin/python" -c "
import asyncio, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from seed import seed
asyncio.run(seed())
"
    popd > /dev/null
    ok "Database seeded"
else
    ok "Database has $PARTY_COUNT parties"
fi

# ── 8. Build Next.js client ──────────────────────────────────────────
step "Building Next.js client"
pushd "$CLIENT_DIR" > /dev/null
if [ ! -d "node_modules" ]; then
    sudo -u "$APP_USER" npm install 2>&1 | tail -1
fi
sudo -u "$APP_USER" NEXT_PUBLIC_API_URL="http://$DOMAIN" npx next build 2>&1 | tail -5
popd > /dev/null
ok "Next.js built for production"

# ── 9. systemd service: pivs-api ─────────────────────────────────────
step "Installing systemd service: pivs-api"
cat > /etc/systemd/system/pivs-api.service <<SVCEOF
[Unit]
Description=PIVS API Server (FastAPI/Gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$SERVER_DIR
EnvironmentFile=$ENV_FILE
Environment=PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin
ExecStart=$VENV_DIR/bin/gunicorn app.main:app -c gunicorn.conf.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pivs-api

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$STORAGE_DIR $LOG_DIR
ReadOnlyPaths=$SERVER_DIR

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable pivs-api.service
systemctl restart pivs-api.service
ok "pivs-api.service installed and started"

# Wait for API to be ready
for i in $(seq 1 15); do
    sleep 2
    if curl -sf http://127.0.0.1:$API_PORT/health > /dev/null 2>&1; then
        ok "API health check passed"
        break
    fi
    if [[ $i -eq 15 ]]; then
        fail "API did not start. Check: journalctl -u pivs-api -n 50"
        exit 1
    fi
done

# ── 10. systemd service: pivs-client ─────────────────────────────────
step "Installing systemd service: pivs-client"
cat > /etc/systemd/system/pivs-client.service <<SVCEOF
[Unit]
Description=PIVS Web Client (Next.js)
After=network.target pivs-api.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$CLIENT_DIR
Environment=NODE_ENV=production
Environment=NEXT_PUBLIC_API_URL=http://$DOMAIN
Environment=PORT=$CLIENT_PORT
ExecStart=$(which npx) next start --port $CLIENT_PORT
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pivs-client

# Security hardening
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable pivs-client.service
systemctl restart pivs-client.service
ok "pivs-client.service installed and started"

# ── 11. nginx site config ────────────────────────────────────────────
step "Configuring nginx site"
cat > /etc/nginx/sites-available/pivs <<'NGINXEOF'
# PIVS — NZ Political Image Verification System
# Managed by deploy.sh — do not edit manually.

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=pivs_verify:10m rate=30r/m;
limit_req_zone $binary_remote_addr zone=pivs_submit:10m rate=10r/m;

upstream pivs_api {
    server 127.0.0.1:8000;
    keepalive 4;
}

upstream pivs_client {
    server 127.0.0.1:3000;
    keepalive 4;
}

server {
    listen 80;
    listen [::]:80;
    server_name PLACEHOLDER_DOMAIN;

    # Security headers
    add_header X-Frame-Options        "SAMEORIGIN"                  always;
    add_header X-Content-Type-Options "nosniff"                     always;
    add_header X-XSS-Protection       "1; mode=block"               always;
    add_header Referrer-Policy        "strict-origin-when-cross-origin" always;

    # Upload limit (50 MB for campaign images)
    client_max_body_size 50M;

    # Timeouts for large uploads
    proxy_connect_timeout 60s;
    proxy_send_timeout    120s;
    proxy_read_timeout    120s;

    # ── API routes ────────────────────────────────────────────────
    # Rate-limited verification (public)
    location /api/v1/verify/ {
        limit_req zone=pivs_verify burst=10 nodelay;
        proxy_pass http://pivs_api;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Rate-limited asset submission (authenticated)
    location /api/v1/assets {
        limit_req zone=pivs_submit burst=5 nodelay;
        proxy_pass http://pivs_api;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # All other API routes (auth, parties, etc.)
    location /api/ {
        proxy_pass http://pivs_api;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API docs (FastAPI Swagger)
    location /docs {
        proxy_pass http://pivs_api;
        proxy_set_header Host $host;
    }
    location /openapi.json {
        proxy_pass http://pivs_api;
        proxy_set_header Host $host;
    }

    # Health check (for monitoring / uptime checks)
    location /health {
        proxy_pass http://pivs_api;
        access_log off;
    }

    # ── Frontend ──────────────────────────────────────────────────
    location / {
        proxy_pass http://pivs_client;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Next.js HMR / WebSocket (only active in dev, harmless in prod)
        proxy_http_version 1.1;
        proxy_set_header Upgrade    $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # ── Logging ───────────────────────────────────────────────────
    access_log /var/log/nginx/pivs-access.log;
    error_log  /var/log/nginx/pivs-error.log;
}

# ── TLS block (uncomment after obtaining certificates) ────────────
# server {
#     listen 443 ssl http2;
#     listen [::]:443 ssl http2;
#     server_name PLACEHOLDER_DOMAIN;
#
#     ssl_certificate     /etc/letsencrypt/live/PLACEHOLDER_DOMAIN/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/PLACEHOLDER_DOMAIN/privkey.pem;
#     ssl_protocols       TLSv1.2 TLSv1.3;
#     ssl_ciphers         HIGH:!aNULL:!MD5;
#
#     # ... same location blocks as the HTTP server above ...
# }
NGINXEOF

# Substitute the domain/IP into the config
sed -i "s/PLACEHOLDER_DOMAIN/$DOMAIN/g" /etc/nginx/sites-available/pivs

# Enable the site (does not touch other sites)
ln -sf /etc/nginx/sites-available/pivs /etc/nginx/sites-enabled/pivs

# Test and reload nginx
if nginx -t 2>&1; then
    systemctl reload nginx
    ok "nginx site 'pivs' enabled and loaded"
else
    fail "nginx config test failed — check /etc/nginx/sites-available/pivs"
    exit 1
fi

# ── 12. Firewall ──────────────────────────────────────────────────────
step "Checking firewall"
if command -v ufw &>/dev/null; then
    ufw allow 'Nginx Full' > /dev/null 2>&1 || true
    ok "ufw: Nginx Full allowed"
else
    warn "ufw not found — ensure port 80 (and 443) are open"
fi

# ── 13. Final checks ─────────────────────────────────────────────────
step "Running deployment checks"

if curl -sf http://127.0.0.1/health > /dev/null 2>&1; then
    ok "nginx -> API health check passed"
else
    warn "nginx -> API not responding via port 80 (may need a moment)"
fi

if curl -sf -o /dev/null http://127.0.0.1/ 2>/dev/null; then
    ok "nginx -> Client proxy working"
else
    warn "nginx -> Client not yet responding (Next.js may still be starting)"
fi

# ── Summary ───────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}  ════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  PIVS Deployment Complete${NC}"
echo -e "${GREEN}  ════════════════════════════════════════════════════${NC}"
echo ""
echo "  Public URL:      http://$DOMAIN"
echo "  Party Portal:    http://$DOMAIN/party"
echo "  API Docs:        http://$DOMAIN/docs"
echo "  Health Check:    http://$DOMAIN/health"
echo ""
echo "  Services:"
echo "    systemctl status pivs-api"
echo "    systemctl status pivs-client"
echo ""
echo "  Logs:"
echo "    journalctl -u pivs-api -f"
echo "    journalctl -u pivs-client -f"
echo "    tail -f /var/log/nginx/pivs-access.log"
echo ""
echo "  Management:"
echo "    sudo $0 --status     # Check all services"
echo "    sudo $0 --stop       # Stop PIVS services"
echo "    sudo $0 --update     # Pull + rebuild + restart"
echo "    sudo $0 --uninstall  # Remove services (keeps data)"
echo ""
if [[ "$DOMAIN" == "$PUBLIC_IP" ]]; then
echo -e "  ${YELLOW}TLS: For HTTPS, point a domain at $PUBLIC_IP then run:${NC}"
echo "    sudo apt install certbot python3-certbot-nginx"
echo "    sudo certbot --nginx -d yourdomain.nz"
echo ""
fi
