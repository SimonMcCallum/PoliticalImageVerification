# NZ Political Image Verification System

A verification system for political campaign images in the New Zealand 2026 General Election. Allows political parties to register their official campaign images and enables the public, media companies, and platforms to verify whether an image genuinely originated from a claimed party.

## Architecture

- **Server**: Python/FastAPI with PostgreSQL, AES-256-GCM encryption, dual hashing (SHA-256 + PDQ perceptual hash)
- **Client**: Next.js (React) with public verification portal and authenticated party portal
- **Storage**: Encrypted at rest with envelope encryption (per-asset DEKs wrapped by master KEK)

## Quick Start (Docker)

```bash
docker compose up --build
```

This starts:
- PostgreSQL on port 5432
- API server on port 8000 (Swagger docs at http://localhost:8000/docs)
- Client on port 3000

### Seed Development Data

After the containers are running:

```bash
docker compose exec server python -m seed
```

This creates 7 NZ political parties with admin accounts. Default credentials:
- `admin_labour` / `changeme123`
- `admin_national` / `changeme123`
- `sysadmin` / `admin_changeme`

**Change all passwords before any non-development use.**

## Local Development (without Docker)

### Server

```bash
cd server
python -m venv .venv
.venv/Scripts/activate     # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL connection string
uvicorn app.main:app --reload --port 8000
```

### Client

```bash
cd client
npm install
npm run dev
```

## API Overview

### Public (no auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/verify/image` | Upload image to verify |
| `POST` | `/api/v1/verify/hash` | Verify by pre-computed hashes |
| `GET` | `/api/v1/verify/{id}` | Look up by verification ID (QR code) |
| `GET` | `/api/v1/parties` | List registered parties |

### Authenticated (party users)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Log in, get JWT token |
| `POST` | `/api/v1/assets` | Register a campaign image |
| `GET` | `/api/v1/assets` | List party's registered images |
| `PATCH` | `/api/v1/assets/{id}` | Update/revoke an asset |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/parties` | Register a new party |
| `POST` | `/api/v1/parties/{id}/users` | Add user to a party |

## How Verification Works

1. **Submission**: A party user uploads an image. The system computes:
   - SHA-256 cryptographic hash (exact matching)
   - PDQ perceptual hash (fuzzy matching, tolerates badge overlays, compression, resizing)
   - pHash (secondary perceptual hash fallback)

2. **Storage**: The original image is encrypted with AES-256-GCM and stored. Only hashes are used for matching.

3. **Verification**: When someone uploads an image to verify:
   - SHA-256 checked first for exact match
   - PDQ Hamming distance checked (threshold <= 31 out of 256 bits)
   - pHash checked as fallback
   - Result returned with party attribution and confidence score

4. **Badge Tolerance**: The verification badge is kept under 5% of image area so that PDQ perceptual hashing still matches the original unbadged image.

## Running Tests

```bash
cd server
pip install -r requirements-test.txt
pytest tests/ -v
```

Tests use SQLite (via aiosqlite) instead of PostgreSQL, so no database setup is needed. The test suite includes:

- **Unit tests**: Encryption, hashing, badge/QR generation, storage
- **Integration tests**: Auth login, asset submission/listing/revocation, verification by image/hash/ID, party management

All 68 tests run in ~17 seconds.

## Production Deployment

### 1. Generate secrets

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(48))"
python -c "import secrets; print('MASTER_ENCRYPTION_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with the generated secrets and your domain
```

### 3. Deploy with Docker Compose

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This starts:
- PostgreSQL (internal only, not exposed)
- API server with Gunicorn (multi-worker, behind nginx)
- Next.js client (behind nginx)
- Nginx reverse proxy on ports 80/443 with rate limiting

### 4. Seed initial data

```bash
docker compose -f docker-compose.prod.yml exec server python -m seed
```

### 5. TLS (HTTPS)

For production, configure TLS in `nginx/nginx.conf` by uncommenting the TLS server block and placing your certificates in `nginx/certs/`.

### Server Configuration

Production environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key | Yes |
| `MASTER_ENCRYPTION_KEY` | 64-char hex key for AES-256 encryption | Yes |
| `POSTGRES_PASSWORD` | Database password | Yes |
| `VERIFICATION_BASE_URL` | Public URL for verification links | Yes |
| `WEB_WORKERS` | Gunicorn worker count (default: CPUs * 2 + 1) | No |
| `LOG_LEVEL` | Logging level (default: info) | No |

## Technology

- **PDQ Hash**: Meta's open-source perceptual hash from [ThreatExchange](https://github.com/facebook/ThreatExchange/tree/main/pdq)
- **Encryption**: AES-256-GCM with envelope encryption pattern
- **Auth**: JWT tokens with optional TOTP MFA
- **C2PA**: Optional Content Credentials integration planned for Phase 3

## License

To be determined.
