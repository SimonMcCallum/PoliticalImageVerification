/**
 * Bloom-filter snapshot service.
 *
 * On install (and on a daily alarm) the extension downloads
 * `/api/v1/extension/bloom-snapshot` from the configured API base,
 * parses it, and stores both the raw bytes (base64) and a meta record
 * in chrome.storage.local so the popup can show the EC exactly what
 * the device is holding.
 *
 * Image hashes are then checked against this local filter before any
 * server lookup happens. Only "maybe registered" hits leave the device.
 *
 * Manifest V3 compliance note
 * ---------------------------
 * The bloom filter we download is DATA, not code. The wire format is a
 * fixed-layout header followed by a raw bit array. We parse it with
 * BloomFilter.deserialize, which is bundled into the extension package
 * at build time. We never eval, never new Function(), never inject a
 * <script>, and never dynamically import a remote module. This is
 * equivalent to a dictionary app downloading a word list or a translation
 * app downloading a language pack, and is permitted under the Chrome Web
 * Store remote-code policy (which prohibits remotely hosted CODE, not
 * remotely hosted DATA).
 */

import { BloomFilter } from "./bloom";
import { debugLog } from "../debug/log";
import {
  DEFAULT_API_BASE,
  STORAGE_KEYS,
  getApiBase,
} from "../config";

export interface PersistedBloomMeta {
  loaded: boolean;
  numBits: number;
  numHashes: number;
  itemCount: number;
  estimatedFalsePositiveRate: number;
  generatedAtMillis: number;
  bytes: number;
}

function uint8ToBase64(bytes: Uint8Array): string {
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]!);
  // btoa is available in service workers and content scripts.
  return btoa(bin);
}

function base64ToUint8(b64: string): Uint8Array {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

async function setStorage(values: Record<string, unknown>): Promise<void> {
  return new Promise((resolve) => {
    chrome.storage.local.set(values, () => resolve());
  });
}

async function getStorage<T = unknown>(key: string): Promise<T | undefined> {
  return new Promise((resolve) => {
    chrome.storage.local.get(key, (v) => resolve(v[key] as T | undefined));
  });
}

/**
 * Fetch the bloom snapshot from the configured API base and persist
 * it locally. Returns the meta on success, throws on failure.
 */
export async function refreshBloomSnapshot(opts?: {
  apiBase?: string;
}): Promise<PersistedBloomMeta> {
  const apiBase = opts?.apiBase ?? (await getApiBase()) ?? DEFAULT_API_BASE;
  const url = `${apiBase.replace(/\/+$/, "")}/api/v1/extension/bloom-snapshot`;

  debugLog.push("bloom-filter-loaded", `fetching ${url}`);

  let resp: Response;
  try {
    resp = await fetch(url, { method: "GET", credentials: "omit" });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    debugLog.push("error", `bloom fetch failed: ${msg}`, { url });
    await setStorage({ [STORAGE_KEYS.bloomLastError]: msg });
    throw err;
  }

  if (!resp.ok) {
    const msg = `HTTP ${resp.status} from ${url}`;
    debugLog.push("error", msg);
    await setStorage({ [STORAGE_KEYS.bloomLastError]: msg });
    throw new Error(msg);
  }

  const buf = new Uint8Array(await resp.arrayBuffer());
  const filter = BloomFilter.deserialize(buf);

  const meta: PersistedBloomMeta = {
    loaded: true,
    numBits: filter.numBits,
    numHashes: filter.numHashes,
    itemCount: filter.itemCount,
    estimatedFalsePositiveRate: filter.estimatedFalsePositiveRate(),
    generatedAtMillis: filter.generatedAtMillis,
    bytes: buf.length,
  };

  await setStorage({
    [STORAGE_KEYS.bloomMeta]: meta,
    [STORAGE_KEYS.bloomBlobBase64]: uint8ToBase64(buf),
    [STORAGE_KEYS.bloomFetchedAt]: Date.now(),
    [STORAGE_KEYS.bloomLastError]: null,
  });

  debugLog.push(
    "bloom-filter-loaded",
    `loaded ${meta.itemCount.toLocaleString()} hashes (${buf.length} bytes)`,
    {
      url,
      numBits: meta.numBits,
      numHashes: meta.numHashes,
      estimatedFpr: meta.estimatedFalsePositiveRate,
    }
  );

  return meta;
}

/**
 * Load the stored bloom filter into memory. Returns null if no snapshot
 * has been downloaded yet.
 */
export async function loadStoredBloomFilter(): Promise<BloomFilter | null> {
  const b64 = await getStorage<string>(STORAGE_KEYS.bloomBlobBase64);
  if (!b64) return null;
  try {
    return BloomFilter.deserialize(base64ToUint8(b64));
  } catch (err) {
    debugLog.push(
      "error",
      `stored bloom blob could not be deserialised: ${
        err instanceof Error ? err.message : String(err)
      }`
    );
    return null;
  }
}
