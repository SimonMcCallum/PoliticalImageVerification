# Installing the PIVS browser extension (Chrome and Edge, developer build)

This page explains how to install the in-development PIVS extension on
Chrome or Microsoft Edge so you can check political images against the
NZ Electoral Commission's verification register while you browse.

The official Chrome Web Store and Edge Add-ons listings are not yet
published. Until they are, the only way to install is the developer
"Load unpacked" path described here. **If you are an ordinary voter
who just wants the extension, please wait for the public listings.
This page is for engineers, the Electoral Commission, security
reviewers, and anyone showing the extension to others before public
release.**

## What the extension does

When you visit a web page, the extension:

1. Looks at images on the page.
2. Runs OCR on each image to see whether it carries a section 204F
   promoter statement (for example, "Authorised by ...").
3. If it does, computes a perceptual hash of the image on your device.
4. Checks the hash against a local bloom filter of registered images.
5. Only when the bloom filter says "maybe registered", queries the
   Commission's verification API to confirm.
6. Shows a small, dismissable badge on the image:
   - green tick: registered by the named party
   - blue tick: registered by the Commission as authority-supplied
   - amber: carries a promoter statement but is not in the register

You can also right-click any image and select "Flag this political
image" to send the Commission a private flag with a reason code.

The extension does not store browsing history, does not collect any
personal information, and never uploads image bytes. Hashes only.

## What you need

- Google Chrome (114+) or Microsoft Edge (114+).
- A local copy of this repository.
- Node.js 18 or newer, plus `npm`.

## Build the extension

Run these commands once, from inside the repository:

```bash
cd extension
npm install
npm run build
```

Vite builds the unpacked extension into a folder named `dist`.
The path you will load into Chrome/Edge is therefore:

```
<your repo path>/extension/dist
```

**Common mistake:** loading `extension/` directly will fail with
"Manifest file is missing or unreadable". The manifest is generated
into `extension/dist/manifest.json` by `npm run build`. Always point
the browser at `dist`, not at the source folder.

If you change source files, run `npm run build` again, then click the
"reload" arrow on the extension card in `chrome://extensions/` /
`edge://extensions/`. While developing you can also use `npm run dev`,
which rebuilds `dist` automatically when files change.

## Install in Chrome

1. Open `chrome://extensions/`.
2. Switch on **Developer mode** (top right).
3. Click **Load unpacked**.
4. Select the `extension/dist` folder.

The PIVS icon appears in the Chrome toolbar. Pin it for easy access.

## Install in Microsoft Edge

The same `dist/` build works in Edge.

1. Open `edge://extensions/`.
2. Switch on **Developer mode** (bottom left).
3. Click **Load unpacked**.
4. Select the `extension/dist` folder.

If you would rather install via a store listing once it is available,
two paths will eventually exist:

- The Microsoft Edge Add-ons store, where the same Manifest V3 build
  is published natively. Recommended for ordinary users on Edge.
- The Chrome Web Store, which Edge can install from after toggling
  "Allow extensions from other stores" in `edge://extensions`. This
  shows a warning during install and is therefore not recommended for
  the general public.

The release pipeline pushes to both stores on a tagged release.

## Use the extension

After installing:

1. Click the PIVS icon in the toolbar to see the popup.
2. Browse normally. The extension does its work in the background.
3. When you encounter a political image, look at the corner of the
   image for a green, blue, or amber badge. Click the badge for
   details.
4. Right-click any image and choose "Flag this political image" if
   something looks wrong. You can pick a reason and add an optional
   short note.

## Why we can download the bloom filter from a server (Manifest V3)

The Chrome Web Store's Manifest V3 policy prohibits extensions from
loading remotely hosted **code** (no `eval`, no `new Function()`, no
dynamically imported scripts from a CDN, no injected `<script>` tags
that point at remote URLs).

The bloom filter we download from `simonmccallum.org.nz/api/v1/extension/bloom-snapshot`
is **data, not code**. It is a fixed-layout binary blob: a small
header followed by a bit array. The extension never executes any
byte of it. The parsing logic (`BloomFilter.deserialize`) ships with
the extension package and is reviewed at submission time. This is the
same pattern a dictionary app uses for word lists, or a translation
app for language packs, and is permitted under MV3.

## Debug (transparency) mode

To support transparency for the Electoral Commission, security
reviewers, and curious users, the extension has a **Debug activity**
panel built in. It shows exactly what the extension is doing on
your device.

1. Open the popup.
2. Tick **Show debug activity (transparency mode)**.

You will see:

- **Bloom filter status**: whether the local register snapshot is
  loaded, how many items it covers, how many bits the filter uses,
  how many hash lookups per query, the estimated false-positive rate,
  and the timestamp it was generated.
- **Live event log**: a scrolling list of every relevant step the
  extension takes:
  - `image-seen`: an image candidate was observed in the page.
  - `ocr-result`: OCR ran. The result records whether a promoter
    statement was detected.
  - `hash-computed`: the perceptual hash was computed locally.
  - `bloom-check`: the local bloom filter was queried. The entry
    shows whether the result was "definitely not in register" or
    "maybe in register".
  - `api-call`: a hash was sent to the verification API. The entry
    shows the endpoint, the response category (registered, not found,
    error), and the latency.
  - `overlay-shown`: a badge was rendered on the page.
  - `flag-submitted` / `report-submitted`: a flag or breach report
    left the device.
  - `error`: any unexpected failure.

You can:

- **Clear** the log to start a fresh session.
- **Export JSON** to download the entire log to disk. Use this to
  share an audit trail with security reviewers or the Commission.

The log is stored in memory only. It is not transmitted anywhere
unless you press "Export JSON" yourself.

## Permissions explained

The extension requests:

- `storage`: remembers your debug-mode preference and the local bloom
  filter snapshot.
- `contextMenus`: adds the "Flag this political image" right-click item.
- `scripting`: needed by Manifest V3 to inject the content script.
- `alarms`: schedules the daily bloom-filter refresh so the local
  copy of the register stays current.
- `host_permissions` for `https://simonmccallum.org.nz/*` (production
  endpoint) and `http://localhost:8000/*` (developer build). These
  are the only origins the extension is allowed to call.
- The content script is allowed to run on `http://*/*` and `https://*/*`
  because political images can appear on any site. The content script
  reads images and runs local OCR, but does not exfiltrate page text,
  cookies, or form data.

## Uninstalling

In `chrome://extensions/` or `edge://extensions/`, find PIVS and click
**Remove**. Removing the extension also clears its locally stored
debug log and bloom filter snapshot.

## Reporting a problem

If something does not work or you want to question the extension's
behaviour, please open an issue in this repository or contact the
project team. Independent inspection of the extension's source code is
welcome and expected.
