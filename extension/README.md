# PIVS browser extension

A Manifest V3 browser extension that checks images carrying a New Zealand
section 204F promoter statement against the PIVS verification register.

This folder is the slice-0 scaffold of the plan in
[../doc/plan-browser-extension.md](../doc/plan-browser-extension.md).

## Develop

```bash
cd extension
npm install
npm run dev       # starts Vite in watch mode; output goes to dist/
npm test          # runs Vitest unit tests
npm run typecheck # tsc with --noEmit
npm run build     # produces an unpacked extension in dist/
```

## Load in Chrome or Edge

1. Run `npm run build` (or `npm run dev` for hot reload).
2. Open `chrome://extensions/` (or `edge://extensions/`).
3. Turn on "Developer mode".
4. Click "Load unpacked" and select the `dist/` folder.

## Layout

```
src/
  background/   MV3 service worker (context menu, future API wiring)
  content/      content script injected into every page
  popup/        toolbar popup UI (html + ts + css)
  lib/
    api/        typed client for PIVS API
    hash/       SHA-256 (Web Crypto). PDQ and pHash arrive in slice 1.
test/
  lib/          Vitest unit tests
public/
  manifest.json MV3 manifest
  icons/        placeholder icons (slice 7 will replace with real brand)
```

## API the extension talks to

- `POST /api/v1/verify/hash` (public): look up a hash in the register.
- `POST /api/v1/extension/report` (public, rate-limited): report an image
  that carries a promoter statement but is not in the register.
- `POST /api/v1/extension/flag` (public, rate-limited): user-initiated flag.

The host origin is configured in `public/manifest.json` under
`host_permissions`. Default dev origin is `http://localhost:8000`.

## What lives in which slice

Slice 0 (this commit) ships:
- Vite + CRXJS build, TypeScript, Vitest.
- Background service worker with a "Flag this political image" context menu.
- Content script stub.
- Popup UI stub.
- Typed API client for verify-hash, report, and flag.
- SHA-256 via Web Crypto.

Subsequent slices (see the plan doc) add PDQ and pHash, API round-trips
against a running PIVS server, OCR via `tesseract.js`, image observation
in the content script, overlay rendering, context-menu flagging, and
store packaging.
