/**
 * Single source of truth for runtime config: API base URL, storage keys,
 * and refresh cadence. Values come from chrome.storage.local with
 * sensible defaults so the extension works out of the box against the
 * production deployment at simonmccallum.org.nz/verify.
 */

export const DEFAULT_API_BASE = "https://simonmccallum.org.nz/verify";

export const STORAGE_KEYS = {
  apiBase: "pivs.apiBase",
  bloomMeta: "pivs.bloomMeta",
  bloomBlobBase64: "pivs.bloomBlobBase64",
  bloomFetchedAt: "pivs.bloomFetchedAt",
  bloomLastError: "pivs.bloomLastError",
  debugMode: "pivs.debugMode",
} as const;

export const REFRESH_ALARM = "pivs.refreshBloom";
/** Daily refresh by default. */
export const REFRESH_PERIOD_MINUTES = 24 * 60;

export async function getApiBase(): Promise<string> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) {
    return DEFAULT_API_BASE;
  }
  return new Promise((resolve) => {
    chrome.storage.local.get(STORAGE_KEYS.apiBase, (v) => {
      const stored = v[STORAGE_KEYS.apiBase];
      resolve(typeof stored === "string" && stored.length > 0 ? stored : DEFAULT_API_BASE);
    });
  });
}
