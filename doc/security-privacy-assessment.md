# PIVS security and privacy assessment

Prepared for the Chief Electoral Officer and the Office of the Privacy Commissioner. Companion to [doc/iso-standards-applicability.md](iso-standards-applicability.md), which lists the standards the Commission can use to evaluate PIVS. This document maps the current codebase against those standards and against the New Zealand Privacy Act 2020.

The assessment was performed on commit `5e60aab` of branch `main`. Every concrete finding cites a `file:line` so it can be checked. Verified findings are marked with the file path inline.

## Executive summary

PIVS is built with privacy as an explicit design property: the public verification API is anonymous, image bytes are never persisted, IP addresses are SHA-256 hashed rather than stored, the browser extension does its work on the user's device with a downloaded bloom filter so most lookups never reach the server, and all sensitive columns (emails, MFA secrets, original filenames) are encrypted at rest with AES-256-GCM envelope encryption.

Against that strong baseline, this assessment identifies fifteen concrete findings the Commission should require resolved before adoption. Three are critical or high severity (configuration of master keys, cross-border disclosure to ip-api.com, dependency on `python-jose 3.3.0`), four are high-severity controls gaps (rate limiting, CORS, hash-format validation, retention), and the rest are medium or low. The data inventory at the end of this document records every category of personal information held.

The recommended path to adoption is to:

1. Fix the three critical/high configuration and dependency findings.
2. Implement the retention and audit-log writes that the schema already anticipates but does not exercise.
3. Eliminate the cross-border IP disclosure to ip-api.com.
4. Stand up an Incident Response Plan that distinguishes Privacy Act 2020 notifiable breaches from Electoral Act misattribution reports.
5. Commission an independent security assessment (GCSB-approved provider) against OWASP ASVS L2.

## Security findings

Severities are CRITICAL, HIGH, MEDIUM, LOW, INFO. Findings are grouped by area, then ordered by severity within area.

### Authentication and tokens

**[CRITICAL] SECRET_KEY and MASTER_ENCRYPTION_KEY default to per-process random values** ([server/app/core/config.py:13](../server/app/core/config.py), line 18)

What. The `Settings` class declares `SECRET_KEY: str = secrets.token_urlsafe(32)` and `MASTER_ENCRYPTION_KEY: str = secrets.token_hex(32)`. When the environment does not supply these values, a fresh value is generated at every process start.

Why it matters. A drifting `SECRET_KEY` invalidates every issued JWT on each restart and causes tokens minted by one worker to be rejected by another. A drifting `MASTER_ENCRYPTION_KEY` makes every previously stored Data Encryption Key, every encrypted email, every encrypted MFA secret, and every encrypted filename permanently unrecoverable. This is a silent-data-loss footgun.

Recommendation. Make both required environment variables. Fail to start if either is missing. Source `MASTER_ENCRYPTION_KEY` from an HSM or KMS in production, as the inline comment already notes.

**[HIGH] python-jose 3.3.0 is pinned, with no upgrade available** ([server/requirements.txt:7](../server/requirements.txt))

What. `python-jose[cryptography]==3.3.0` is the most recent release. CVE-2024-33663 (algorithm confusion) and CVE-2024-33664 (JWE decompression DoS) have been disclosed against this library. The current code pins `algorithms=[settings.ALGORITHM]` (server/app/core/auth.py:78), which mitigates the algorithm-confusion CVE, but the DoS CVE still applies to any endpoint that decodes a token.

Why it matters. PIVS is a JWT-backed system. The library that handles JWTs has known unfixed vulnerabilities and is effectively unmaintained.

Recommendation. Migrate to `pyjwt` or `authlib`. Both are actively maintained.

**[HIGH] No JWT refresh, no revocation, fixed 60-minute access tokens** ([server/app/core/config.py:14](../server/app/core/config.py), [server/app/core/auth.py:34](../server/app/core/auth.py) line 66)

What. Only an access token is issued. Tokens carry no `iat`, `nbf`, `jti`, `iss`, or `aud` claims. There is no denylist. Disabling a user (`is_active=False`) only takes effect on the next request, and there is no way to invalidate a held token short of rotating the `SECRET_KEY`, which logs everyone out.

Why it matters. A stolen token is usable for up to an hour with no kill switch. For a regulator-facing system, recovering from a token compromise should be a per-user action, not a global one.

Recommendation. Add `iat`, `jti`, and `aud` claims. Implement a short access token plus a refresh token. Add a `token_version` column on `PartyUser` checked in `get_current_user`, incrementable to revoke a single user.

**[MEDIUM] HS256 with a shared symmetric secret** ([server/app/core/auth.py:44](../server/app/core/auth.py))

What. The signing algorithm is `HS256`. Anyone with read access to `SECRET_KEY` can mint tokens for any role, including `ELECTORAL_COMMISSION`.

Why it matters. The blast radius of a configuration leak is wider than it needs to be.

Recommendation. Move to RS256 or EdDSA so that only the signer holds the private key. Verifiers carry the public key.

**[MEDIUM] No login throttling, lockout, or timing-flat error path** ([server/app/api/auth.py:32](../server/app/api/auth.py))

What. `/auth/login` has no rate limiter, no failed-attempt counter, and no captcha. When a username does not exist the code returns immediately, while when it does exist a bcrypt comparison runs. This is a timing oracle for username enumeration.

Why it matters. Permits online password guessing and account enumeration against admin and EC accounts.

Recommendation. Run bcrypt against a dummy hash when the user is missing, flattening the timing. Add per-IP and per-username rate limiting (nginx `limit_req` or Redis-backed `slowapi`). Soft lockout after N failures. For EC accounts, consider WebAuthn.

**[MEDIUM] MFA not required for high-privilege roles** ([server/app/api/auth.py:50](../server/app/api/auth.py))

What. MFA is optional. There is no policy gate forcing `ADMIN` or `ELECTORAL_COMMISSION` users to enrol.

Why it matters. A phished password is a single point of compromise for the whole register.

Recommendation. Require MFA enrolment for `ADMIN` and `ELECTORAL_COMMISSION` users before any privileged endpoint will work. Redirect to `/mfa/setup` when `mfa_enabled` is false.

**[MEDIUM] MFA confirmation accepts the code as a bare parameter** ([server/app/api/auth.py:97](../server/app/api/auth.py))

What. `confirm_mfa` declares `code: str` as a bare FastAPI parameter, which FastAPI treats as a query-string parameter for a POST without a body model.

Why it matters. TOTP codes may end up in access logs, browser history, and referrer headers.

Recommendation. Wrap in a Pydantic body model.

**[LOW] Password complexity is length-only** ([server/app/api/auth.py:142](../server/app/api/auth.py) line 167)

What. Only `len(new_password) < 8` is enforced.

Recommendation. Use a banned-password list (HIBP top 100k) or `zxcvbn`. Lift to 12 for `ADMIN` and `ELECTORAL_COMMISSION`.

### Authorization

**[HIGH] EC list endpoints decrypt every user's email in bulk** ([server/app/api/ec_user_management.py:42](../server/app/api/ec_user_management.py) line 77, [server/app/api/party_admin.py:65](../server/app/api/party_admin.py) line 80)

What. `GET /ec/users` decrypts every user's email and returns it as JSON, as does `GET /parties/{id}/members` for the party admin.

Why it matters. Encryption at rest is undone the moment one EC or party-admin token leaks. This is the most concentrated PII exposure in the system.

Recommendation. Mask emails by default (`s***@example.com`). Require an explicit reveal action, audit-logged and rate-limited.

**[MEDIUM] Inconsistent role gating on duplicate endpoints** ([server/app/api/parties.py:218](../server/app/api/parties.py) vs [server/app/api/party_admin.py:83](../server/app/api/party_admin.py))

What. `POST /parties/{party_id}/users` in parties.py uses `require_admin` with no `user.party_id == party_id` check. The candidate-creation endpoint in party_admin.py does check. The result is that an `ADMIN` user in party A can create a user inside party B via parties.py.

Why it matters. Breaks the per-party isolation that the rest of the codebase enforces.

Recommendation. Add the party-scope check, or restrict that route to `ELECTORAL_COMMISSION`.

**[MEDIUM] `require_admin` is also used for cross-party platform actions** ([server/app/api/parties.py:145](../server/app/api/parties.py))

What. `create_party`, `get_party`, `update_party` all use `require_admin`, which any party `ADMIN` passes. No party-scope check.

Recommendation. Restrict party CRUD to `ELECTORAL_COMMISSION`. Introduce a separate dependency for "party-scoped admin" and use it where appropriate. Audit existing call sites.

### Cryptography

**[INFO] AES-256-GCM via the `cryptography` library, envelope encryption with per-asset DEKs** ([server/app/services/encryption.py:25](../server/app/services/encryption.py))

The baseline is strong. 96-bit random nonces from `os.urandom`. Per-asset DEKs wrapped by a master KEK. AEAD without AAD. Recommendation: pass non-empty AAD (asset id or user id bytes) so a stolen ciphertext cannot be replayed onto another row.

**[MEDIUM] No key rotation mechanism for the master KEK** ([server/app/services/encryption.py:17](../server/app/services/encryption.py))

What. `_get_kek` returns a single static key. There is no key version, no list of historical KEKs, and no re-wrap job.

Why it matters. A KEK exposure forces a single big-bang migration with downtime to re-encrypt the database.

Recommendation. Prefix encrypted blobs with a key version byte. Support a list of historical KEKs for decryption. Add a re-wrap job.

### Transport and CORS

**[HIGH] CORS allows all methods and headers with credentials** ([server/app/main.py:98](../server/app/main.py))

What. `allow_methods=["*"]`, `allow_headers=["*"]`, `allow_credentials=True`.

Why it matters. With credentials, any allowed origin can perform arbitrary cross-site actions on the user's behalf if cookies are introduced later. The current bearer-token model partly mitigates this, but the configuration is a footgun.

Recommendation. Allow only the methods you use (`GET`, `POST`, `PATCH`, `DELETE`) and the headers you accept (`Authorization`, `Content-Type`). Set `allow_credentials=False` while the API is bearer-token only.

**[MEDIUM] Plain localhost origins in CORS for production builds** ([server/app/main.py:78](../server/app/main.py))

What. `http://localhost` and `http://127.0.0.1` are hard-coded into every deployment's CORS list.

Recommendation. Gate the localhost entries on a non-production environment.

**[MEDIUM] No HSTS, HTTPS redirect, trusted-host middleware, or security-header middleware** ([server/app/main.py](../server/app/main.py))

Recommendation. Add `TrustedHostMiddleware`. Set Strict-Transport-Security at the proxy. Add a middleware that emits `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and a tight `Content-Security-Policy` for the docs UI.

**[LOW] Global exception handler leaks raw exception strings** ([server/app/main.py:106](../server/app/main.py))

Recommendation. Return a static message. Log the trace server-side only.

### Input validation

**[HIGH] Hash fields accepted without format validation** ([server/app/schemas/extension.py:14](../server/app/schemas/extension.py), [server/app/schemas/verification.py:34](../server/app/schemas/verification.py))

What. `sha256`, `pdq`, and `phash` are `str | None` with only `max_length`. No hex check, no fixed length, no regex.

Why it matters. Garbage values flow into SQL `WHERE` clauses on indexed columns. This is not SQL injection (SQLAlchemy parameterises), but it lets an attacker pollute verification logs and geo stats, submit junk reports that match prefixes, and exhaust the DB indexes.

Recommendation. Add Pydantic patterns: `^[0-9a-fA-F]{64}$` for sha256 and pdq, `^[0-9a-fA-F]{16}$` for phash.

**[MEDIUM] `metadata` JSON has no schema, no size cap, no key/value sanitisation** ([server/app/api/assets.py:164](../server/app/api/assets.py))

Recommendation. Validate with a Pydantic model with whitelisted fields and a max byte cap. Ensure the frontend renders metadata as text only.

**[MEDIUM] No magic-byte check on uploads** ([server/app/api/assets.py:67](../server/app/api/assets.py))

What. The code trusts `file.content_type` (client-controlled) and the filename.

Recommendation. Sniff magic bytes server-side. Refuse SVG unless required. If SVG is kept, sanitise via a strict allowlist or render server-side only.

### Rate limiting

**[HIGH] In-process rate limiter is unsafe in production** ([server/app/api/extension.py:45](../server/app/api/extension.py))

What. The rate limiter is a `dict` in Python process memory. With `gunicorn --workers N`, the effective rate is `N` times the declared limit. Behind a load balancer, multiply again. The dict is also unbounded.

Why it matters. The declared `RATE_LIMIT_EXTENSION_FLAG_PER_MINUTE: 10` is in fact `10 * workers * instances`. Login, verify, and reset-token endpoints have no rate limiting at all.

Recommendation. Move to nginx `limit_req_zone` (keyed on `$binary_remote_addr`) or Redis-backed `slowapi`. Apply to `/auth/login`, `/auth/reset-password/confirm`, `/verify/*`, and authenticated submission endpoints. Add a bounded LRU or periodic sweep on the in-memory map until the move happens.

### Secrets management

See the CRITICAL finding on `SECRET_KEY` and `MASTER_ENCRYPTION_KEY` defaults under Authentication.

**[LOW] SMTP and IMAP credentials in plaintext config** ([server/app/core/config.py:46](../server/app/core/config.py))

Recommendation. Use `SecretStr`. Confirm they are not echoed in startup logs.

### Logging and audit

**[HIGH] AuditLog model is defined but never written** ([server/app/models/verification.py:48](../server/app/models/verification.py))

What. The `audit_logs` table exists with `actor_id`, `action`, `entity_type`, `entity_id`, `details_encrypted`, `ip_hash`. A grep across the server confirms no `AuditLog(...)` constructor call anywhere. Verified.

Why it matters. Privileged actions (EC password resets, party updates, asset revocations, candidate creation, bulk email decryption) have no audit trail. This is also a precondition for being able to scope a notifiable privacy breach under the Privacy Act 2020.

Recommendation. Wire `AuditLog` writes into every privileged mutation and every bulk-decryption read.

**[INFO] IP hashing uses unsalted SHA-256** ([server/app/core/auth.py:62](../server/app/core/auth.py), [server/app/api/verification.py:34](../server/app/api/verification.py), [server/app/api/extension.py:61](../server/app/api/extension.py))

What. `hashlib.sha256(ip.encode()).hexdigest()`. With the IPv4 space at ~4.3 billion, an unsalted SHA-256 is reversible by precomputation. The defence is pseudonymisation against operators, not against an attacker who exfiltrates the hashes.

Recommendation. HMAC with a long-lived server-side pepper, or truncate to 16 hex chars after HMAC.

### SQL injection

**[INFO] All queries use SQLAlchemy parameterised `select(...)` calls.** No string interpolation. UUIDs parsed via `uuid.UUID(...)` before hitting `where`. No SQL injection surface found.

### Dependency hygiene

In addition to the python-jose finding above, `passlib==1.7.4` ([server/requirements.txt:8](../server/requirements.txt)) is dormant (last release 2020). It works with `bcrypt==4.2.1` but emits warnings. Plan a migration to `argon2-cffi` or direct `bcrypt`.

FastAPI 0.115.6, cryptography 44.0.0, pydantic 2.10.4 are current as of late 2024 and free of known CVEs as of this audit.

### Extension security

**[MEDIUM] No response-size cap on `/extension/bloom-snapshot` client side** ([extension/src/lib/bloom/snapshot.ts:99](../extension/src/lib/bloom/snapshot.ts))

What. The fetch has no `Content-Length` check, no MIME check beyond what `host_permissions` enforces, and no size cap before allocating a `Uint8Array`.

Why it matters. A misrouted or hijacked API host could serve a multi-gigabyte blob and OOM the service worker.

Recommendation. Cap the response (for example 5 MB). Assert the `Content-Type` starts with `application/octet-stream`. Consider signing the bloom blob.

**[LOW] Bloom parser allocates based on attacker-supplied `numBits`** ([extension/src/lib/bloom/bloom.ts:147](../extension/src/lib/bloom/bloom.ts))

What. `numBits` is read from the blob and used to allocate. Truncation is checked but the value itself is not capped.

Recommendation. Sanity-cap `numBits` (for example, `<= 2_000_000`) and `numHashes` (`<= 32`) before allocation.

**[INFO] No JS execution from server-supplied data.** The bloom blob is parsed as bytes only. No `eval`, no `Function`, no remote import. Manifest V3 remote-code policy compliant.

### Browser extension manifest

**[MEDIUM] `host_permissions` ships with localhost in the production manifest** ([extension/public/manifest.json:29](../extension/public/manifest.json))

Recommendation. Strip the localhost entry from the production build. Use a separate `manifest.dev.json` for development.

**[LOW] `content_scripts` matches `http://*/*` and `https://*/*`** ([extension/public/manifest.json:19](../extension/public/manifest.json))

Necessary for the use case but reviewers will scrutinise it. Document the data-flow guarantee in the extension README. Add a unit test that asserts no network call is made on a bloom miss.

**[INFO] `permissions` is appropriately scoped:** `storage`, `contextMenus`, `scripting`, `alarms`. No `tabs`, no `webNavigation`, no `<all_urls>` in `permissions`. Good least-privilege posture.

## Privacy assessment against the Privacy Act 2020

Each Information Privacy Principle is assessed against the codebase. The rating scale is STRONG, ADEQUATE, GAP, or NOT_APPLICABLE.

### IPP 1: Purpose of collection

**Rating: ADEQUATE.** Collection is purposive and minimal. Public verification requires no account ([server/app/api/verification.py:185](../server/app/api/verification.py)). Party-user collection is the minimum needed for authenticated submission. The weakest link is the absence of an in-code purpose statement surfaced to users at the point of collection.

### IPP 2: Source of personal information

**Rating: ADEQUATE with caveat.** Party admins create user accounts on behalf of party members and candidates ([server/app/api/parties.py:244](../server/app/api/parties.py)), which is third-party collection. The codebase has no machine-checkable evidence of candidate consent at account-creation time. The password-reset email channel does eventually reach the individual.

### IPP 3: Awareness at point of collection

**Rating: GAP.** No collection notice is surfaced from the API or rendered in the login flow. The `note` field on `ExtensionFlag` ([server/app/models/extension.py:113](../server/app/models/extension.py)) accepts free text from an anonymous user. A short collection statement should be displayed in the extension before submit, and the login page should link to a privacy notice. This is a documentation-and-UI fix.

### IPP 4: Manner of collection

**Rating: ADEQUATE.** Hashes are computed locally on the user's device (extension) or in transient memory on the server (verification endpoint). Image bytes are never persisted ([server/app/api/verification.py:192](../server/app/api/verification.py)). The geolocation lookup at [server/app/services/geolocation.py:43](../server/app/services/geolocation.py) does send the raw IP to a third party, treated separately under IPP 12.

### IPP 5: Storage and security

**Rating: STRONG with one configuration risk.** Envelope encryption with per-asset DEKs ([server/app/services/encryption.py](../server/app/services/encryption.py)). Emails, MFA secrets, and filenames are encrypted at rest. Passwords are bcrypt-hashed. Verification IPs are stored only as SHA-256 hashes ([server/app/models/verification.py:37](../server/app/models/verification.py)). The configuration risk is the CRITICAL finding above on the `MASTER_ENCRYPTION_KEY` default. The in-process rate limiter is also a storage and security weakness for production multi-worker deployments.

### IPP 6: Access by the individual

**Rating: GAP.** No self-service endpoint by which a user can request a copy of personal information held about them. EC users can list every party user with decrypted email ([server/app/api/ec_user_management.py:42](../server/app/api/ec_user_management.py)), but the data subject themselves has no `GET /me` or data-export route. Recommendation: add `GET /api/v1/auth/me/export`.

### IPP 7: Correction by the individual

**Rating: ADEQUATE.** Fields likely to need correction (email, promoter statement, password, MFA via re-setup) are editable by the user themselves or via party admin / EC. No "statement of correction" mechanism exists.

### IPP 8: Accuracy before use or disclosure

**Rating: ADEQUATE.** The verification result returns a confidence score and a match type ([server/app/api/verification.py:124](../server/app/api/verification.py)). The system does not assert "this image is fake", only "registered or unregistered". Email accuracy is gated by an `email_verified_for_processing` flag that is reset on change ([server/app/api/party_admin.py:180](../server/app/api/party_admin.py)).

### IPP 9: Retention

**Rating: GAP.** This is the most material privacy gap in the codebase. No retention period is defined anywhere. No scheduled job purges verification logs, extension flags, or expired assets. `Asset.expires_at` is declared but never set at submission. Verified: `expires_at` is read in three places but never assigned.

Recommendation. Define retention periods in [server/app/core/config.py](../server/app/core/config.py) and implement a periodic cleanup task. Suggested: verification logs 24 months, extension flags 12 months after triage, revoked assets 30 days, email jobs 30 days after completion, registered assets indefinite while the party is active. Approve the schedule with the Chief Archivist under the Public Records Act.

### IPP 10: Limits on use

**Rating: ADEQUATE.** Use is consistent with the stated purpose. Hashed IPs are used for anti-abuse. Geo statistics are aggregate-only. The one to watch is `ec_list_users`, which is a powerful capability that should be limited by role granularity and audited (see AuditLog gap).

### IPP 11: Limits on disclosure

**Rating: ADEQUATE.** Public disclosure is confined to party identity on a verified asset. Disclosure to the EC role is consistent with its regulatory function. Inter-party isolation is enforced in most places. The cross-party gap noted under Authorization findings is the exception.

### IPP 12: Disclosure outside New Zealand

**Rating: GAP.** Every public verification disclosed a raw IP address to ip-api.com over plain HTTP ([server/app/services/geolocation.py:43](../server/app/services/geolocation.py)). The IP is personal information under the Privacy Act. The disclosure is over plain HTTP, which is an additional security concern. Comments in the code recommend offline MaxMind GeoLite2 lookups.

Recommendation. Switch to MaxMind GeoLite2 (in-process) or drop the geo feature entirely before EC adoption.

### IPP 13: Unique identifiers

**Rating: STRONG.** No government-issued personal identifier (IRD, NHI, driver licence, passport) is collected, stored, or required. UUIDs are opaque internal identifiers. The verification ID identifies an image, not a person. This is the cleanest of the 13 IPPs.

## Notifiable breach compliance

The Privacy Act 2020 sections 114 to 120 require notification to the Privacy Commissioner and to affected individuals where a privacy breach has caused or is likely to cause serious harm.

What PIVS provides today:

- Encrypted PII at rest limits the harm radius of a database breach.
- Hashed IPs reduce the personal information exposed by a log dump.
- No public-side identifiers means a snapshot leak does not expose verifier identities.

What is missing:

1. The `AuditLog` row is never written, so there is no who-accessed-what trail with which to scope an incident.
2. There is no breach-detection runtime, no anomaly threshold, and no notification workflow.
3. There is no documented Incident Response Plan in `doc/`.
4. There is no administrative tool for issuing a breach notification.

### Naming-collision flag

The extension endpoints at [server/app/api/extension.py:71](../server/app/api/extension.py) (`/api/v1/extension/report`) and line 154 (`/api/v1/extension/flag`) handle reports of misattributed political images. These are not Privacy Act 2020 notifiable privacy breaches. They are content-integrity reports about political advertising. The model docstring at [server/app/models/extension.py:1](../server/app/models/extension.py) uses "breach" in the electoral-integrity sense (Electoral Act 1993, section 204F promoter statements), not the privacy-breach sense.

A Privacy Commissioner reading "breach report" in an extension UI could reasonably assume a privacy-breach channel. A member of the public seeing the same word may use it to report what they believe is a privacy breach, in which case the system will triage it as an electoral matter rather than escalate to the OPC.

Recommendation. Rename throughout: "misattribution report" or "promoter-statement integrity report" instead of "breach report". Provide a separate, explicitly labelled channel for actual privacy incidents.

## Data inventory

Every category of personal information held by PIVS:

| Category | Source code | Collected from | Retention | Who can see it | Encryption state |
|---|---|---|---|---|---|
| Party user account (username, email, password hash, MFA secret, role, last_login) | server/app/models/party.py:57-104 | Party admin (on behalf of user) | Indefinite, no purge job | Self via login; party admins for own party; EC role (all users) | Email and MFA secret AES-256-GCM encrypted, password bcrypt-hashed |
| Candidate account | same shape; party_admin.py:83-138 | Party admin or EC | Indefinite | Same | Same |
| EC user account | server/app/models/party.py:23 | EC | Indefinite | Self only | Same |
| Verification logs | server/app/models/verification.py:25-43 | Public, anonymous | Indefinite, no purge (GAP) | EC role aggregated | Plain; IP is hashed |
| Extension reports | server/app/models/extension.py:44-96 | Public, anonymous, via extension | Indefinite (GAP) | EC role via review queue | Plain; page host only, never full URL |
| Extension flags | server/app/models/extension.py:99-134 | Public, anonymous, via extension | Indefinite (GAP) | EC role via review queue | Plain; free-text note may incidentally contain PII |
| Geo statistics | server/app/models/geo_stats.py:16-33 | Public, aggregate only | Indefinite; non-identifying | EC role | Plain (not PI) |
| Audit logs | server/app/models/verification.py:48-64 | Defined but never written | N/A | N/A | details column exists but unused |
| Email processing jobs | server/app/models/email_job.py:22-53 | Party user (when enabled) | No purge job | Owning user | Hashed sender; image stored encrypted |
| Share links | server/app/models/share_link.py:13-43 | Party submitter | `expires_at` enforced | Anyone holding the token | Token stored as hash only |
| Asset blobs (image, badge, promoter overlay, QR, thumbnail) | server/app/models/asset.py:18-75 | Party submitter | Indefinite (`expires_at` never set) | Owning party; EC role | Original image AES-256-GCM with per-asset DEK; other versions plain |

## Recommendations ordered by privacy-risk reduction per unit of effort

1. Stop sending raw IPs to ip-api.com. Replace [server/app/services/geolocation.py:43](../server/app/services/geolocation.py) with an offline MaxMind GeoLite2 lookup, or drop the geo feature. Every public verification is currently a cross-border disclosure under IPP 12.
2. Define and implement retention periods. Add `*_RETENTION_DAYS` settings and a scheduled job that purges `VerificationLog`, `ExtensionFlag`, completed `EmailProcessingJob`, and revoked-then-aged `Asset` rows. Approve with the Chief Archivist under the Public Records Act.
3. Rename "breach" to "misattribution" or "integrity" in the extension data model and UI to remove confusion with Privacy Act notifiable breaches.
4. Wire up AuditLog. The table exists but is never written. Add writes at every privileged action and every bulk-decryption read.
5. Add `GET /api/v1/auth/me/export` to satisfy IPP 6.
6. Surface a collection notice (IPP 3) at party login, candidate activation email, and extension first-run.
7. Enforce `MASTER_ENCRYPTION_KEY` and `SECRET_KEY` from environment. Fail-fast on missing values.
8. Move rate limiting out of the in-process dict to nginx or Redis. Extend to login, verify, and reset endpoints.
9. Replace `python-jose 3.3.0` with `pyjwt` or `authlib`.
10. Tighten CORS to a method and header allowlist. Set `allow_credentials=False`.
11. Add an Incident Response Plan to `doc/`, naming the Privacy Officer, the 72-hour notification clock, and a template for the s.117 notification to the Commissioner.
12. Restrict bulk email decryption in `ec_list_users`. Mask by default. Audit-log each reveal.
13. Commission an independent security assessment against OWASP ASVS L2 by a GCSB-approved provider before public launch.

Items 1 to 5 are pre-conditions for adoption. Items 6 to 13 are required before any public-facing launch but can be sequenced.
