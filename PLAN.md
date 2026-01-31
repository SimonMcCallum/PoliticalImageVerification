# Political Image Verification System - NZ 2026 General Election

## Project Overview

A system that allows New Zealand political parties to register campaign images/assets, and enables media companies, platforms, and the public to verify whether an image genuinely originated from a claimed political party. The system uses a privacy-first model with encrypted storage, dual hashing (cryptographic + perceptual), and a public verification API.

---

## 1. Research Summary

### 1.1 Existing Solutions Evaluated

| Solution | Type | Relevance | Recommendation |
|---|---|---|---|
| **C2PA / Content Credentials** | Open standard for media provenance | High - industry standard backed by Adobe, Microsoft, Google, Meta | **Adopt as optional layer** - good for embedding provenance in images, but low adoption as of 2025 and experts have found bypass methods |
| **Campaign Verify** (US) | Identity verification for political orgs | Medium - US-focused, SMS-only, uses authorization tokens | **Adapt the token model** - their approach of issuing verification tokens to authenticated political entities is sound |
| **Meta PDQ Hash** | Perceptual image hashing (256-bit) | High - open source, designed for image matching at scale | **Adopt as primary perceptual hash** - BSD licensed, battle-tested at Meta scale, good for badge-tolerant matching |
| **pHash / ImageHash** | Perceptual hashing libraries | High - multiple language implementations | **Use as fallback/secondary hash** - well-established, multiple algorithms available |
| **OpenSig** | Blockchain-anchored digital signatures | Medium - provides timestamped proof of existence | **Consider for audit trail** - Polygon-anchored proofs provide independent verification |
| **Google/Meta Ad Verification** | Platform-specific ad authentication | Low - proprietary, platform-locked | **Not suitable** - cannot be used outside their platforms |
| **PubMatic AI Classification** | AI-powered ad transparency | Low - commercial, US midterm focused | **Not suitable** - proprietary commercial solution |

### 1.2 NZ Regulatory Context

Key rules from the Electoral Act 1993 (as amended by Electoral Amendment Act 2025):

- **Promoter statements required**: All election advertisements must include a promoter statement (name + contact details). Fine of up to $40,000 for non-compliance.
- **Spending limits (from 1 Jan 2026)**: Parties up to $1,503,000 + $36,000/electorate candidate; registered third-party promoters up to $424,000.
- **Digital advertising**: Internet advertising counts toward spending limits and must follow the same rules as traditional media.
- **No timing restrictions**: Election ads can be published at any time except on Election Day before 7pm (TV/radio restricted until writ day, 4 October 2026).
- **Privacy Act 2020**: Political parties are explicitly exempt, but a privacy-first approach is still recommended for public trust.

### 1.3 Hashing Strategy Decision

The system requires **two types of hashing** to handle the badge/overlay requirement:

1. **Cryptographic Hash (SHA-256)**: For exact-match verification of the original submitted image. Fast, deterministic, collision-resistant. Used when comparing original-to-original.

2. **Perceptual Hash (PDQ + pHash)**: For fuzzy matching that tolerates visual modifications like:
   - Verification badge overlays
   - JPEG recompression from social media
   - Minor cropping or resizing
   - Screenshot captures
   - QR code additions

   PDQ uses a Hamming distance threshold of <=31 (out of 256 bits) for confident matches.

### 1.4 Privacy-First Architecture Decision

Given the political sensitivity of this system:

- **At-rest encryption**: All stored images encrypted with AES-256-GCM before storage
- **Encryption key management**: Server-side key management with HSM-backed keys (or AWS KMS / Azure Key Vault for cloud deployment)
- **Hash-only public access**: The public verification API only exposes hash comparisons, never the stored images themselves
- **Metadata minimization**: Store only what is needed (party ID, submission timestamp, hashes, encrypted image)
- **Audit logging**: Immutable audit trail of all submissions and verification requests
- **No personal data in verification**: Verification requests do not require user accounts or personal information

---

## 2. System Architecture

### 2.1 High-Level Components

```
+------------------+     +------------------+     +------------------+
|  Party Portal    |     |  Verification    |     |  Admin           |
|  (Submit Assets) |     |  Portal (Public) |     |  Dashboard       |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+------------------------------------------------------------------+
|                        API Gateway                                |
|                  (Rate limiting, Auth)                             |
+------------------------------------------------------------------+
         |                        |                        |
         v                        v                        v
+------------------+     +------------------+     +------------------+
|  Submission      |     |  Verification    |     |  Party           |
|  Service         |     |  Service         |     |  Management      |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         v                        v                        v
+------------------------------------------------------------------+
|                     Data Layer                                     |
|  +---------------+  +---------------+  +------------------------+ |
|  | Encrypted     |  | Hash Index    |  | Party Registry         | |
|  | Image Store   |  | (SHA + PDQ)   |  | (Auth + Metadata)      | |
|  +---------------+  +---------------+  +------------------------+ |
+------------------------------------------------------------------+
```

### 2.2 Core Services

#### A. Submission Service
- Receives images from authenticated party accounts
- Generates SHA-256 cryptographic hash of original image
- Generates PDQ perceptual hash (256-bit) of original image
- Generates pHash as secondary perceptual hash
- Encrypts original image with AES-256-GCM
- Stores encrypted image + all hashes + metadata
- Optionally generates C2PA Content Credential manifest
- Returns verification ID and embeddable badge/QR code

#### B. Verification Service
- Accepts image uploads or hash values from the public
- Computes hashes of submitted image
- Compares against hash index:
  - SHA-256 exact match first (fastest)
  - PDQ Hamming distance match (<= 31 threshold)
  - pHash distance match as fallback
- Returns verification result: verified/unverified/partial match
- Provides party attribution if verified
- No authentication required for verification

#### C. Party Management Service
- Onboarding of political parties with identity verification
- Multi-factor authentication for party accounts
- Role-based access (party admin, submitter, viewer)
- API key management for programmatic submissions
- Party profile management (logo, name, registration details)

### 2.3 Badge and QR Code System

When an image is registered, the system generates:

1. **Verification Badge**: A small overlay badge (configurable position) containing:
   - A verification icon/symbol
   - A short verification URL or QR code
   - The party name

2. **QR Code**: Encodes a URL like `https://verify.nzelection.nz/v/{verification-id}` that links to the verification result page.

3. **Embeddable Widget**: HTML/JS snippet that media companies can embed to show verification status.

**Critical Design Point**: The perceptual hash is computed on the *original image without the badge*. When verifying an image *with* a badge, the PDQ hash tolerates the badge overlay because it captures semantic/structural features rather than pixel-exact data. The badge is deliberately small enough (~5% of image area) to stay within PDQ's matching threshold.

### 2.4 Verification Flow

```
User sees political image on social media / hoarding / website
                    |
                    v
    +----------------------------------+
    | Option A: Scan QR code on image  |
    | Option B: Upload image to portal |
    | Option C: Use browser extension  |
    +----------------------------------+
                    |
                    v
    +----------------------------------+
    | System computes hashes of image  |
    | SHA-256 -> exact match check     |
    | PDQ -> fuzzy match check         |
    +----------------------------------+
                    |
            +-------+--------+
            |                |
         Match            No Match
            |                |
            v                v
    +----------------+  +------------------+
    | VERIFIED       |  | NOT VERIFIED     |
    | Party: Labour  |  | This image is    |
    | Registered:    |  | not registered   |
    | 2026-05-15     |  | by any party     |
    | Asset ID: xxx  |  +------------------+
    +----------------+
```

---

## 3. Technology Stack

### 3.1 Recommended Stack

| Component | Technology | Rationale |
|---|---|---|
| **Backend API** | Python (FastAPI) | Rich ecosystem for image processing, C2PA bindings, PDQ bindings available via PyPI |
| **Perceptual Hashing** | `pdqhash` (Python) + `imagehash` | PDQ is Meta's battle-tested algorithm; imagehash provides pHash fallback |
| **Cryptographic Hashing** | `hashlib` (SHA-256) | Standard library, no dependencies |
| **Image Processing** | Pillow + OpenCV | Badge overlay generation, image normalization |
| **Encryption** | `cryptography` library (AES-256-GCM) | Well-audited Python encryption library |
| **C2PA Integration** | `c2pa-python` | Official C2PA Python bindings from Content Authenticity Initiative |
| **Database** | PostgreSQL | ACID compliance, JSON support for metadata, proven at scale |
| **Hash Index** | PostgreSQL with pgvector or dedicated VP-tree | For efficient Hamming distance queries on PDQ hashes |
| **Encrypted Storage** | S3-compatible (MinIO for self-hosted, or AWS S3 with SSE) | Industry standard object storage with encryption |
| **Frontend (Public)** | Next.js or SvelteKit | Fast verification portal, SSR for SEO, good mobile experience |
| **Frontend (Party)** | Same framework | Authenticated submission portal |
| **Authentication** | OAuth 2.0 + TOTP MFA | Party accounts use strong authentication |
| **QR Code Generation** | `qrcode` (Python) | Lightweight QR code generation |
| **API Documentation** | OpenAPI / Swagger (auto-generated by FastAPI) | Self-documenting API |
| **Containerization** | Docker + Docker Compose | Consistent deployment, easy local development |

### 3.2 Alternative Stack Considerations

- **Rust backend**: Higher performance for hashing operations, native C2PA support via `c2pa-rs`. Consider if throughput becomes a bottleneck.
- **Node.js backend**: If the team is JS-focused, `c2pa-js` provides Node bindings. PDQ would need WASM or native bindings.
- **Blockchain audit trail**: OpenSig on Polygon for immutable timestamp proofs. Adds complexity but provides independent verification that an image was registered at a specific time.

---

## 4. Data Model

### 4.1 Core Entities

```
Party
├── id (UUID)
├── name (string) - e.g., "New Zealand Labour Party"
├── short_name (string) - e.g., "Labour"
├── registration_number (string) - Electoral Commission registration
├── logo_url (string, encrypted)
├── contact_email (string, encrypted)
├── created_at (timestamp)
├── status (enum: active, suspended, deregistered)
└── api_keys[] (encrypted)

PartyUser
├── id (UUID)
├── party_id (FK -> Party)
├── email (string, encrypted)
├── role (enum: admin, submitter, viewer)
├── mfa_enabled (boolean)
├── created_at (timestamp)
└── last_login (timestamp)

Asset
├── id (UUID)
├── party_id (FK -> Party)
├── submitted_by (FK -> PartyUser)
├── original_filename (string, encrypted)
├── mime_type (string)
├── file_size (integer)
├── sha256_hash (string, indexed)
├── pdq_hash (binary 256-bit, indexed)
├── phash (binary 64-bit, indexed)
├── encrypted_storage_key (string) - reference to encrypted blob
├── encryption_key_id (string) - reference to KMS key
├── badge_image_url (string) - pre-generated badge version
├── qr_code_url (string) - verification QR code
├── verification_url (string) - short URL for verification
├── c2pa_manifest (binary, optional) - C2PA content credential
├── metadata (JSON) - campaign name, target audience, etc.
├── status (enum: active, revoked, expired)
├── created_at (timestamp)
├── expires_at (timestamp, optional)
└── revoked_at (timestamp, optional)

VerificationLog
├── id (UUID)
├── asset_id (FK -> Asset, nullable)
├── match_type (enum: exact, perceptual, none)
├── pdq_distance (integer, nullable) - Hamming distance
├── phash_distance (integer, nullable)
├── source_ip_hash (string) - hashed IP for rate limiting, not tracking
├── user_agent (string)
├── created_at (timestamp)
└── result (enum: verified, unverified, partial_match, error)

AuditLog
├── id (UUID)
├── actor_id (FK -> PartyUser, nullable)
├── action (string) - e.g., "asset.submit", "asset.revoke"
├── entity_type (string)
├── entity_id (UUID)
├── details (JSON, encrypted)
├── ip_hash (string)
└── created_at (timestamp)
```

---

## 5. API Design

### 5.1 Public Verification API (No Auth Required)

```
POST /api/v1/verify/image
  - Upload image file
  - Returns: { verified: bool, match_type, party, asset_id, confidence }

POST /api/v1/verify/hash
  - Submit pre-computed hash { sha256?, pdq?, phash? }
  - Returns: { verified: bool, match_type, party, asset_id }

GET /api/v1/verify/{verification-id}
  - Look up by verification ID (from QR code)
  - Returns: { verified: bool, party, registered_date, status }

GET /api/v1/parties
  - List registered parties (public info only)
  - Returns: [{ id, name, short_name, logo_url }]
```

### 5.2 Party Submission API (Auth Required)

```
POST /api/v1/assets
  - Upload image + metadata
  - Returns: { asset_id, verification_url, qr_code_url, badge_image_url, hashes }

GET /api/v1/assets
  - List party's registered assets
  - Returns: paginated list

GET /api/v1/assets/{id}
  - Get asset details

PATCH /api/v1/assets/{id}
  - Update metadata or revoke

DELETE /api/v1/assets/{id}
  - Soft-delete / revoke asset

POST /api/v1/assets/{id}/badge
  - Generate badge overlay with custom position
  - Returns: { badge_image_url }

POST /api/v1/assets/bulk
  - Bulk upload multiple assets
```

### 5.3 Admin API (Admin Auth Required)

```
POST /api/v1/parties
  - Register new party

PATCH /api/v1/parties/{id}
  - Update party details

POST /api/v1/parties/{id}/users
  - Add user to party

GET /api/v1/admin/audit-log
  - View audit trail

GET /api/v1/admin/stats
  - Verification statistics
```

---

## 6. Security & Privacy Design

### 6.1 Encryption Architecture

```
+------------------+     +------------------+     +------------------+
|  Image Upload    | --> |  Hash Generation | --> |  Encryption      |
|  (TLS in transit)|     |  (plaintext,     |     |  (AES-256-GCM)   |
|                  |     |   in memory only)|     |                  |
+------------------+     +------------------+     +------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |  Encrypted Blob  |
                                                  |  Storage (S3)    |
                                                  +------------------+

Key Management:
- Data Encryption Keys (DEKs): Unique per asset, generated server-side
- Key Encryption Keys (KEKs): Stored in HSM / KMS
- Envelope encryption: DEK encrypted by KEK, stored alongside blob
```

### 6.2 Security Measures

- **Transport**: TLS 1.3 for all connections
- **Authentication**: OAuth 2.0 with PKCE for party portal, TOTP MFA mandatory for party admins
- **Authorization**: RBAC with party-scoped permissions
- **Rate Limiting**: IP-based and token-based rate limits on verification API
- **Input Validation**: Strict file type validation (JPEG, PNG, WebP, SVG, PDF)
- **Image Sanitization**: Strip EXIF/metadata before hashing (prevents metadata leakage)
- **SQL Injection**: Parameterized queries via ORM (SQLAlchemy)
- **CORS**: Strict origin policy for API
- **CSP**: Content Security Policy headers on web portals
- **Audit Trail**: Immutable, append-only audit log
- **Key Rotation**: Automated KEK rotation schedule
- **Penetration Testing**: Pre-launch security audit recommended

### 6.3 Privacy Measures

- Verification requests are anonymous (no login required)
- IP addresses are hashed in logs (cannot be reversed)
- No cookies or tracking on verification portal
- Stored images are encrypted and only decryptable by the system (not publicly accessible)
- Party user PII (email, name) encrypted at rest
- Data retention policy: assets expire after election cycle unless renewed
- GDPR-aligned data handling even though NZ Privacy Act exempts political parties

---

## 7. Badge and Overlay System Design

### 7.1 Badge Specifications

The verification badge should be:
- **Small**: Maximum 5% of image area to stay within PDQ tolerance
- **Positioned**: Configurable (corner placement, default bottom-right)
- **Semi-transparent**: Does not fully obscure underlying content
- **Contains**: Verification icon + short URL or QR code
- **Consistent**: Standard design across all parties (builds public recognition)

### 7.2 Badge Generation Process

```
1. Original image submitted
2. Hashes computed on ORIGINAL (no badge)
3. Badge generated with verification URL
4. Badge composited onto image copy
5. Both original hash and badged image stored
6. Party receives both versions
```

### 7.3 Verification Tolerance Testing

Before launch, the system must be tested to ensure PDQ matching works correctly with:
- Badge overlays at various positions and sizes
- JPEG compression at various quality levels (social media typically uses 70-85%)
- Screenshots (adds OS chrome, potential color profile changes)
- Resizing (social media auto-resize)
- Cropping (up to 20% should still match)
- Color space conversions (sRGB to P3 etc.)
- Multiple badge additions (e.g., party adds their own + verification badge)

---

## 8. Integration Points

### 8.1 Social Media Integration

- **Browser Extension**: Chrome/Firefox extension that automatically checks images on Facebook, Instagram, Twitter/X against the verification API
- **Embeddable Widget**: `<script>` tag that websites can include to show verification badges
- **Meta/Google Ad Library**: Cross-reference with platform ad transparency reports

### 8.2 Media Company Integration

- **REST API**: Full API access for media companies to batch-verify images
- **Webhook Notifications**: Subscribe to new asset registrations by party
- **RSS/Atom Feed**: Public feed of newly registered assets (hashes only, not images)

### 8.3 Electoral Commission Integration

- **Party Registry Sync**: Validate party registrations against Electoral Commission data
- **Compliance Reporting**: Help track that registered ads include promoter statements
- **Data Export**: Provide aggregate statistics to Electoral Commission

### 8.4 Physical Media (Hoardings/Billboards)

- **QR Code Generation**: High-resolution QR codes suitable for print at various sizes
- **Short URLs**: Memorable verification URLs (e.g., `verify.nz/L2026a1b2`)
- **NFC Tags**: Optional NFC-encoded verification links for accessible verification

---

## 9. Development Phases

### Phase 1: Foundation (Core MVP)
- Project scaffolding (Python/FastAPI backend, database schema)
- Party registration and authentication system
- Image submission with SHA-256 + PDQ hashing
- Basic verification API (image upload -> match result)
- Encrypted image storage
- Basic web portal for verification
- Unit and integration tests

### Phase 2: Badge System & Public Portal
- Badge overlay generation system
- QR code generation
- Public verification web portal (mobile-friendly)
- Verification result pages with party attribution
- PDQ tolerance testing and threshold tuning
- API documentation (OpenAPI/Swagger)

### Phase 3: Enhanced Verification
- pHash as secondary matching algorithm
- C2PA Content Credential integration (optional embed)
- Browser extension for social media verification
- Embeddable verification widget for websites
- Bulk upload support for parties
- Rate limiting and abuse prevention

### Phase 4: Integrations & Scale
- Media company API access and onboarding
- Electoral Commission data integration
- Webhook notifications
- Performance optimization (hash index, caching)
- Load testing for election-day traffic
- Security audit / penetration test

### Phase 5: Production Hardening
- Monitoring and alerting (Prometheus/Grafana or cloud-native)
- Automated backups with encrypted snapshots
- Disaster recovery plan
- CDN for verification portal
- Accessibility audit (WCAG 2.1 AA)
- Documentation for parties, media, public

---

## 10. Key Technical Decisions to Make

### 10.1 Decisions Requiring Input

1. **Hosting**: Self-hosted (NZ sovereignty) vs. cloud (AWS Sydney / Azure Australia East)?
   - Recommendation: NZ-hosted or AU-region cloud for data sovereignty

2. **Domain/Branding**: Government-backed (elections.govt.nz subdomain) vs. independent?
   - Recommendation: Independent non-profit with Electoral Commission endorsement

3. **Blockchain Audit Trail**: Include OpenSig/Polygon timestamping for immutable proof?
   - Recommendation: Not for MVP, consider for Phase 4+

4. **C2PA Depth**: Full C2PA manifest embedding vs. hash-only approach?
   - Recommendation: Hash-only for MVP, C2PA as optional enhancement in Phase 3

5. **Open Source**: Fully open source vs. open-core?
   - Recommendation: Fully open source (MIT/Apache 2.0) for transparency and trust

6. **Multi-election Support**: NZ-only vs. adaptable for other countries?
   - Recommendation: Design for NZ 2026, but keep architecture adaptable

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Party adoption is low | System is useless without registered content | Early engagement with major parties, simple onboarding |
| Perceptual hash false positives | Incorrect verification | Multiple hash algorithms, configurable thresholds, human review option |
| Perceptual hash false negatives (badge too large) | Badge causes mismatch | Strict badge size limits, pre-launch tolerance testing |
| Adversarial image manipulation | Evade detection | PDQ is resistant to common transforms; add DINOv2-based hashing in future |
| System becomes target for attacks | DDoS, data breach | Rate limiting, WAF, encrypted storage, security audit |
| Regulatory changes | New requirements | Modular architecture allows adaptation |
| Election-day traffic spike | System unavailable when most needed | CDN, auto-scaling, load testing in advance |
| Party impersonation during registration | Fake party registers | Manual verification against Electoral Commission registry |

---

## 12. Research Sources

### Image Verification & Hashing
- [Meta ThreatExchange / PDQ Hash](https://github.com/facebook/ThreatExchange/tree/main/pdq) - BSD licensed perceptual hashing
- [pHash](https://www.phash.org/) - Open source perceptual hash library
- [Python ImageHash](https://github.com/JohannesBuchner/imagehash) - Multiple perceptual hash algorithms
- [PHASER Forensic Framework](https://www.sciencedirect.com/science/article/pii/S2666281723001993) - Perceptual hash evaluation

### Content Provenance
- [C2PA Standard](https://c2pa.org/) - Coalition for Content Provenance and Authenticity
- [Content Authenticity Initiative](https://contentauthenticity.org/how-it-works) - How content credentials work
- [C2PA Rust SDK](https://github.com/contentauth/c2pa-rs) - Reference implementation
- [C2PA JavaScript SDK](https://github.com/contentauth/c2pa-js) - Browser/Node.js implementation
- [C2PA Python SDK](https://opensource.contentauthenticity.org/docs/introduction/) - Python bindings
- [C2PA Privacy Analysis](https://worldprivacyforum.org/posts/privacy-identity-and-trust-in-c2pa/) - World Privacy Forum review

### Political Ad Verification
- [Campaign Verify](https://www.campaignverify.org/) - US political identity verification
- [Campaign Verify Process](https://www.campaignverify.org/our-process) - How verification works
- [PubMatic AI Transparency](https://pubmatic.com/blog/ai-powered-transparency-for-the-2026-political-ad-cycle/) - AI ad classification

### NZ Electoral Regulations
- [Electoral Act 1993 - Election Advertisement Definition](https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM3486918.html)
- [Election 2026 Advertising Rules (RNZ)](https://www.rnz.co.nz/news/political/585452/election-2026-how-does-campaign-advertising-work-and-what-are-the-rules)
- [Electoral Commission - About Election Advertising](https://elections.nz/guidance-and-rules/advertising-and-campaigning/about-election-advertising/)
- [Election Integrity 2026](https://elections.nz/media-and-news/2025/ensuring-election-integrity-for-2026-and-the-future/)
- [Electoral Law Changes](https://www.justice.govt.nz/about/news-and-media/news/electoral-law-changes/)

### Privacy & Encryption
- [NZ Privacy Act 2020](https://www.legislation.govt.nz/act/public/2020/0031/latest/LMS23223.html)
- [Privacy Principles](https://www.privacy.org.nz/privacy-act-2020/privacy-principles/)
- [Zero-Knowledge Encryption Guide](https://www.hivenet.com/post/zero-knowledge-encryption-the-ultimate-guide-to-unbreakable-data-security)

### Digital Signatures & Blockchain
- [OpenSig](https://opensig.net/) - Open-source digital signatures on Polygon
- [Sigstore](https://www.sigstore.dev/) - Open-source software signing
- [Numbers Protocol](https://medium.com/overtheblock/digital-authenticity-provenance-and-verification-in-ai-generated-media-c871cbd99130) - Digital media provenance

### QR Codes for Political Advertising
- [Bitly QR Codes for Political Ads](https://bitly.com/blog/qr-codes-for-political-ads/)
- [Anedot Political QR Codes](https://www.anedot.com/blog/political-marketing-qr-codes)
