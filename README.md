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

## Technology

- **PDQ Hash**: Meta's open-source perceptual hash from [ThreatExchange](https://github.com/facebook/ThreatExchange/tree/main/pdq)
- **Encryption**: AES-256-GCM with envelope encryption pattern
- **Auth**: JWT tokens with optional TOTP MFA
- **C2PA**: Optional Content Credentials integration planned for Phase 3

## License

To be determined.
