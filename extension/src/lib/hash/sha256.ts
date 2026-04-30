/**
 * SHA-256 using the Web Crypto API. Works in service workers, content
 * scripts, and Node (which polyfills crypto.subtle from globalThis).
 */

export async function sha256Hex(bytes: ArrayBuffer | Uint8Array): Promise<string> {
  // Normalise to a fresh Uint8Array so the input is always a plain
  // ArrayBuffer-backed view (SharedArrayBuffer is rejected by Web Crypto).
  const view = bytes instanceof Uint8Array ? new Uint8Array(bytes) : new Uint8Array(bytes);
  const digest = await crypto.subtle.digest("SHA-256", view);
  return bufferToHex(digest);
}

function bufferToHex(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  const out = new Array<string>(bytes.length);
  for (let i = 0; i < bytes.length; i++) {
    out[i] = bytes[i]!.toString(16).padStart(2, "0");
  }
  return out.join("");
}
