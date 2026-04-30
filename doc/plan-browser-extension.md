# Browser Extension Build Plan

## Summary

A Manifest V3 browser extension that runs locally on the user's device, detects promoter statements on images encountered while browsing, computes perceptual hashes, queries the PIVS verification API, and surfaces the result as a small overlay. Users can flag images. An administrative back end receives de-duplicated reports of "carries a promoter statement but not registered".

This plan is organised as seven slices. Each slice is shippable and testable on its own, so that progress is visible and regressions are caught early. Target: working alpha before June 2026, public beta by July 2026.

## Repository layout

A new top-level folder:

```
extension/
  src/
    background/        # service worker (MV3)
    content/           # content script injected into pages
    popup/             # toolbar popup UI
    options/           # options page
    lib/
      hash/            # SHA-256, PDQ, pHash
      ocr/             # Tesseract WASM wrapper
      api/             # fetch client for PIVS API
      promoter/        # promoter-statement pattern matching
    ui/                # overlay badges, flag dialog
  public/
    icons/             # 16, 32, 48, 128 png
    manifest.json      # MV3 manifest (template)
  test/
    unit/              # Vitest unit tests
    fixtures/          # reference images with known hashes
    integration/       # mocked PIVS API tests
    e2e/               # Playwright tests
  vite.config.ts       # build config
  package.json
  tsconfig.json
  README.md
```

## Tech stack

- TypeScript 5.x
- Vite + [CRXJS Vite Plugin](https://crxjs.dev/vite-plugin) for MV3 extension builds
- Vitest for unit and integration tests
- Playwright for end-to-end tests (loads a persistent browser with the unpacked extension)
- Hash libraries:
  - SHA-256: `crypto.subtle` (built in)
  - PDQ: `@darwin-digital-trust/pdq` (JS port) or `pdq-wasm` (Meta's C++ ported to WebAssembly). Must match the Hamming distance of 31 bits used server side.
  - pHash: `image-hash-js` or a small hand-ported implementation from the Python `imagehash` package
- OCR: `tesseract.js` (WASM build, ships as its own worker). English language data only to keep the bundle small.

Bundle target: under 5 MB total including Tesseract data, to stay inside Chrome Web Store friendly limits.

## Server-side work required

The core API is already suitable. Several additions support the extension. All but the authority-supplied registration flow have already landed:

1. `POST /api/v1/extension/report` (anonymous, rate-limited by IP hash). Body: `{ sha256?, pdq?, phash?, detected_promoter_text, page_url_host }`. Only the URL host is stored, never the full path. De-duplicated by perceptual hash. **Done.**
2. `POST /api/v1/extension/flag` (anonymous, rate-limited). Body: `{ sha256?, pdq?, phash?, reason, note?, page_url_host }`. Reason codes are a fixed enum. **Done.**
3. Admin views under `/api/v1/ec/review-queue/*` (role `require_electoral_commission`): list reports and flags ordered by observed_count, dismiss/triage/refer transitions, summary counts. **Done.**
4. `GET /api/v1/extension/bloom-snapshot` (anonymous). Returns a versioned binary bloom filter of all active asset hashes. The extension downloads this and queries it locally so the server cannot see which images a user is browsing. **Done.**
5. `POST /api/v1/admin/assets/authority-supplied` for manual registration of a confirmed-but-unregistered image into the distinct authority-supplied category. **Pending in slice 6.**

The bloom filter wire format is byte-compatible across the Python and TypeScript implementations, locked in by a fixture file checked into `extension/test/fixtures/bloom-snapshot.bin` and exercised by the JS test suite.

## Slice plan

Each slice ends with a working extension that can be loaded unpacked into Chrome, and a passing test suite.

### Slice 0. Scaffold and CI

**Build**
- Create `extension/` folder and Vite + CRXJS setup.
- Manifest V3 with `host_permissions` limited to the PIVS API origin.
- Package scripts: `npm run dev` (watches and hot reloads), `npm run build`, `npm run test`, `npm run e2e`.
- GitHub Actions workflow that runs lint, unit tests, and builds the extension zip on every PR.

**Test**
- `npm run build` produces a loadable `dist/` directory.
- Playwright smoke test: launch Chromium with the unpacked extension, open `chrome://extensions`, assert the extension is listed and enabled.

**Done when:** The empty extension loads and the CI pipeline is green.

### Slice 1. Hash computation in the browser

**Build**
- `lib/hash/sha256.ts`: `hashSha256(blob): Promise<string>` using Web Crypto.
- `lib/hash/pdq.ts`: wrap the PDQ WASM module and return a 256-bit hex string.
- `lib/hash/phash.ts`: pure TS port of the imagehash pHash algorithm.

**Test**
- Unit tests against fixtures. Fixture set: 20 reference images also processed by the server's hashing service. Store expected hashes in `test/fixtures/hashes.json`. Assert extension computes bit-identical SHA-256, byte-identical PDQ, and Hamming distance 0 pHash.
- Tolerance tests: register image A. Apply JPEG compression, 10 percent resize, and a badge overlay. Assert Hamming distance to the PDQ of the original is under the 31-bit threshold.

**Done when:** Hash parity with the server is proven for the fixture set.

### Slice 2. API client and register lookup

**Build**
- `lib/api/client.ts`: `verifyHash({ sha256, pdq, phash })` wrapping `POST /api/v1/verify/hash`. **Done in slice 0.**
- Exponential backoff on 429, one retry on 5xx, no retry on 4xx.
- Error type that distinguishes network error, server error, and "not found" (a successful response with no match). **Done.**

**Test**
- Unit: mock `fetch` and assert correct request shape, retries, and result decoding. **Done (6 tests).**
- Integration: run against a local PIVS instance in a `docker-compose` test fixture. Register a known image via the party API, then verify by hash from the extension code and expect a match. Deregister, verify again, expect "not found". Test runs in CI.

**Done when:** The extension can verify any image's hash against a running PIVS server.

### Slice 2b. Local bloom filter snapshot

**Build**
- `lib/bloom/bloom.ts`: bloom filter sized for a target false-positive rate, with serialise/deserialise and a `mightContain` query. Wire format is versioned and byte-compatible with the Python service. **Done.**
- `services/bloom.py` on the server, with the matching wire format. **Done.**
- `GET /api/v1/extension/bloom-snapshot` endpoint that builds the snapshot from active assets and serves it as `application/octet-stream`. **Done.**
- A background task in the extension's service worker that downloads the snapshot on install, refreshes it daily, and stores both the blob and a meta record in `chrome.storage.local`.
- Content-script lookup path: when an image carries a promoter statement, query the local filter first. Only escalate to `/verify/hash` on a maybe-hit.

**Test**
- Unit (JS): inserted items always match, false-positive rate within target on a 5,000-item population, serialise/deserialise round trip. **Done (8 tests).**
- Unit (Python): same suite plus byte-format wire-pinning fixtures. **Done (8 tests).**
- Wire-compat: a Python-generated bloom blob is decoded by the JS implementation and answers the same queries with the same results. **Done (1 fixture-driven test).**
- Integration: server endpoint includes seeded asset hashes; extension downloads, deserialises, and finds them.

**Done when:** Most images never trigger a network round-trip. The server cannot tell which images a user is browsing unless a bloom hit needs confirmation.

### Slice 2c. Debug (transparency) mode

**Build**
- `lib/debug/log.ts`: a capped in-memory event log with kinds for `image-seen`, `ocr-result`, `hash-computed`, `bloom-check`, `api-call`, `overlay-shown`, `flag-submitted`, `report-submitted`, and `error`. Subscribers, JSON export, in-memory only by default. **Done.**
- Popup UI: a "Show debug activity (transparency mode)" toggle, a bloom-filter-meta block, and a live tail of events with per-kind colour coding. Clear and Export JSON buttons. **Done.**
- Persistent toggle in `chrome.storage.local`. **Done (toggle + bloom meta read).**

**Test**
- Unit: log capping at 500 entries, subscribe/unsubscribe semantics, JSON export shape, console mirroring under enabled/disabled flag. **Done (5 tests).**
- E2E: open the popup with debug mode on, simulate a verification, assert the new event appears in the rendered list within 500 ms.

**Done when:** Anyone (Commission, security reviewer, ordinary user) can see exactly what the extension is doing on their device, and export the log.

### Slice 3. Promoter-statement detection

**Build**
- `lib/ocr/tesseract.ts`: wrapper around `tesseract.js` running in a Web Worker.
- `lib/promoter/patterns.ts`: regex and fuzzy-match patterns for section 204F statements. Start with "Authorised by" and common variants. Mirror the threshold used in the server's `ocr.py` (0.8 SequenceMatcher equivalent).
- `lib/promoter/detect.ts`: given an image, run OCR, apply patterns, return `{ matched: boolean, text?: string, confidence: number }`.

**Test**
- Unit: a curated corpus of 40 images. 20 with promoter statements (including hoarding photographs, social media cards, printed flyers) and 20 without (landscape photos, memes, stock imagery). Assert precision above 0.95 and recall above 0.85 on the positive set, and fewer than one false positive on the negative set.
- Performance test: median OCR time on a 1200 by 1200 image must be under 2 seconds on a mid-range laptop.

**Done when:** The extension can reliably decide "does this image carry a section 204F promoter statement?".

### Slice 4. Content script and overlays

**Build**
- Content script observes `IntersectionObserver` entries for images above a minimum display size.
- Runs a simple size/aspect filter to skip icons, avatars, and sprites.
- For candidate images: runs OCR. If a promoter statement is present, computes the perceptual hash and calls the API client.
- Renders a small badge overlay in one of three states: registered (green tick with party name), authority-supplied (blue tick with note), or unregistered-with-promoter (amber). Overlays are HTML elements positioned absolutely, always dismissable, never blocking.
- Basic keyboard and screen-reader accessibility (aria-label, focus ring).

**Test**
- Playwright E2E tests against a harness page that renders 10 images with a mix of registered and unregistered items. Assert the correct badges appear within 5 seconds and can be dismissed.
- Accessibility test using `@axe-core/playwright` on the harness page and on the badge component in isolation.
- Cross-site test: run the harness through localhost HTTPS, a fake Facebook-style DOM (iframes, infinite scroll), and a fake news-site DOM (lazy loading). Assert badges still render in all three.

**Done when:** Badges appear correctly on a harness page across common site patterns.

### Slice 5. User flagging

**Build**
- Right-click context menu item "Flag this political image". Mobile equivalent: long-press handler (Firefox Android only, Chrome and Edge mobile do not support extensions natively; Safari via the macOS wrapper).
- Flag dialog with four reason codes (misattributed, promoter statement appears fake, content concern, other) and an optional 280-character note.
- POST to `/api/v1/extension/flag`. Rate-limited locally to 10 flags per hour per install.

**Test**
- Unit: rate limiter and payload shape.
- E2E: trigger the context menu on a harness image, select a reason, submit, and assert the request was sent with the expected shape. Mock server returns 200. Assert a brief success toast is shown.

**Done when:** Users can flag an image and the flag is delivered to the server.

### Slice 6. Admin queue and authority-supplied registration (server side)

**Build**
- New endpoints listed above: `/extension/report`, `/extension/flag`, `/admin/review-queue`, `/admin/assets/authority-supplied`.
- Admin dashboard UI in the existing Next.js client to display the queue, search by promoter name, and register an image under the authority-supplied category.
- Authority-supplied assets tagged distinctly in the database and surfaced in `/verify/hash` responses with a `source: "authority_supplied"` field so the extension can render the blue badge.

**Test**
- Unit: admin endpoint authorisation checks (non-EC users cannot see the queue).
- Integration: submit 10 reports with the same hash and assert the queue shows one de-duplicated row with `observed_count: 10`.
- E2E: extension reports an image; admin UI shows the entry; admin clicks "register as authority-supplied"; extension sees a blue badge on next encounter.

**Done when:** The full loop works: extension reports, admin resolves, extension sees the resolution.

### Slice 7. Packaging, privacy, and distribution

**Build**
- Privacy policy page, hosted alongside the core PIVS site.
- Store listing copy, icons, screenshots.
- `manifest.json` final form: minimum permissions. Expected: `contextMenus`, `storage`, `scripting` (if needed), `host_permissions` for the PIVS API only. No `<all_urls>` except for the content script match, and even there scoped to `http` and `https` only.
- Release automation: GitHub Actions workflow that, on a tagged release, produces signed `.zip` artefacts for Chrome Web Store and Microsoft Edge Add-ons.

**Test**
- Independent privacy review (short engagement): confirm no image bytes leave the device, no tracking, no analytics.
- Security review (GCSB-approved provider) of the built extension and its API surface.
- Accessibility audit of the badge component and popup.
- Submit to Chrome Web Store for review.

**Done when:** The extension is published as a public beta to the Chrome and Edge stores.

## Testing strategy at a glance

| Layer | Tool | What it covers |
|---|---|---|
| Unit | Vitest | Hash parity, OCR logic, pattern matching, API client, rate limiter |
| Integration (server) | Vitest with Docker Compose PIVS | Verify-by-hash round trips, report and flag endpoints, admin queue |
| E2E | Playwright | Content script badge rendering, context menu, flag dialog, admin workflow |
| Accessibility | axe-core | Badges and popup pass WCAG 2.1 AA |
| Performance | Playwright with `performance.mark` | OCR under 2 s; per-page CPU under 5 percent on a 20-image page |
| Cross-browser | Manual matrix (Chrome, Edge, Firefox, Safari) | Badge rendering, context menu, permissions |
| Regression | Snapshot tests for badge DOM | Visual and structural stability |

Every slice above has its own acceptance criteria and is merged only when its test suite is green in CI.

## Milestone schedule

Indicative, assuming one engineer at roughly half time. Adjust based on availability.

| Milestone | Calendar weeks from start | Gate |
|---|---|---|
| Slice 0 scaffold + CI | 1 | CI passes on empty extension |
| Slice 1 hashing parity | 2 to 3 | Server/client hash fixtures match |
| Slice 2 API client | 4 | Integration test against local PIVS |
| Slice 3 OCR | 5 to 6 | Corpus precision/recall targets met |
| Slice 4 content script and overlays | 7 to 8 | E2E badges on harness |
| Slice 5 flagging | 9 | E2E flag round-trip |
| Slice 6 admin queue | 10 to 11 | Full extension-to-admin loop |
| Slice 7 store submission | 12 | Submitted to Chrome and Edge stores |

Buffer three to four weeks for store review and remediation.

## Risks tied to the plan

| Risk | Mitigation |
|---|---|
| PDQ JS/WASM output differs bit-for-bit from the Python `pdqhash` library | Slice 1 has explicit parity tests against a fixture set. If parity fails, fall back to pHash for perceptual matching and register PDQ as a future enhancement. |
| Tesseract bundle size pushes the extension past Chrome's practical size ceiling | Use the smallest English training data, dynamic import on first use, and consider shipping OCR in the service worker rather than in content scripts. |
| OCR false positives create user complaints | Conservative confidence threshold, easy overlay dismissal, and a user setting to turn off OCR entirely. |
| Chrome Web Store review delays | Submit a draft listing early (slice 0 already creates the developer account). Maintain a side-load developer build path in case reviewers ask for changes close to the election. |
| Mobile story is uneven (Edge mobile and Chrome mobile do not support extensions) | Plan confirms Firefox Android and Safari iOS via the macOS wrapper. Communicate clearly in voter-education materials which devices support the extension. |
| Backend does not yet have `/extension/report` and admin queue | Slice 6 is scheduled before public launch. Slice 4 can ship behind a feature flag that disables reports until slice 6 lands. |

## Out of scope

- Content moderation, automatic takedown, or any form of blocking.
- Detection of AI-generated content, deepfakes, or manipulation detection beyond the simple "is this image in the register" question.
- Social features, share, or public flag counts. Flags are administrative triage input only.
