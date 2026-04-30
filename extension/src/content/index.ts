/**
 * Content script, injected into every http(s) page.
 * Slice 0 only announces itself. Slice 4 will add image observation,
 * OCR, hashing, and overlay rendering.
 */

// eslint-disable-next-line no-console
console.info("[PIVS] content script loaded");

// Stub so slice 0 has a real module boundary.
export {};
