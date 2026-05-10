/**
 * Popup script.
 *
 * Surfaces the runtime state of the extension to the user (and to the
 * Electoral Commission during transparency reviews):
 *   - API base it is configured to talk to
 *   - whether the bloom filter is loaded and when it was last fetched
 *   - the bloom-filter metadata (size, FPR, hashes per lookup, etc.)
 *   - a live event log when debug mode is on
 *
 * Also provides a manual "Refresh bloom filter" action that asks the
 * service worker to re-download the snapshot.
 */

import { debugLog, type DebugEvent } from "../lib/debug/log";
import {
  DEFAULT_API_BASE,
  STORAGE_KEYS,
  getApiBase,
} from "../lib/config";

const STATUS_EL = document.getElementById("status");
const TOGGLE_EL = document.getElementById("debug-toggle") as HTMLInputElement | null;
const PANEL_EL = document.getElementById("debug-panel");
const EVENTS_EL = document.getElementById("debug-events");
const CLEAR_BTN = document.getElementById("debug-clear");
const EXPORT_BTN = document.getElementById("debug-export");
const REFRESH_BTN = document.getElementById("refresh-bloom");
const REFRESH_STATUS = document.getElementById("refresh-status");

const API_BASE_EL = document.getElementById("api-base");
const FETCHED_AT_EL = document.getElementById("bloom-fetched");

const BLOOM_LOADED = document.getElementById("bloom-loaded");
const BLOOM_ITEMS = document.getElementById("bloom-items");
const BLOOM_BITS = document.getElementById("bloom-bits");
const BLOOM_K = document.getElementById("bloom-k");
const BLOOM_FPR = document.getElementById("bloom-fpr");
const BLOOM_GENERATED = document.getElementById("bloom-generated");
const BLOOM_BYTES = document.getElementById("bloom-bytes");

interface PersistedBloomMeta {
  loaded: boolean;
  numBits: number;
  numHashes: number;
  itemCount: number;
  estimatedFalsePositiveRate: number;
  generatedAtMillis: number;
  bytes: number;
}

async function readDebugFlag(): Promise<boolean> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return false;
  return new Promise((resolve) => {
    chrome.storage.local.get(STORAGE_KEYS.debugMode, (v) =>
      resolve(Boolean(v[STORAGE_KEYS.debugMode]))
    );
  });
}

async function writeDebugFlag(on: boolean): Promise<void> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return;
  return new Promise((resolve) => {
    chrome.storage.local.set({ [STORAGE_KEYS.debugMode]: on }, () => resolve());
  });
}

async function readBloomMeta(): Promise<PersistedBloomMeta | null> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return null;
  return new Promise((resolve) => {
    chrome.storage.local.get(STORAGE_KEYS.bloomMeta, (v) =>
      resolve((v[STORAGE_KEYS.bloomMeta] as PersistedBloomMeta) ?? null)
    );
  });
}

async function readFetchedAt(): Promise<number | null> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return null;
  return new Promise((resolve) => {
    chrome.storage.local.get(STORAGE_KEYS.bloomFetchedAt, (v) =>
      resolve((v[STORAGE_KEYS.bloomFetchedAt] as number | null) ?? null)
    );
  });
}

async function readLastError(): Promise<string | null> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return null;
  return new Promise((resolve) => {
    chrome.storage.local.get(STORAGE_KEYS.bloomLastError, (v) =>
      resolve((v[STORAGE_KEYS.bloomLastError] as string | null) ?? null)
    );
  });
}

function renderEvent(e: DebugEvent): HTMLLIElement {
  const li = document.createElement("li");
  const time = new Date(e.ts).toLocaleTimeString();
  const kind = document.createElement("span");
  kind.className = `kind kind-${e.kind}`;
  kind.textContent = e.kind;

  const summary = document.createElement("span");
  summary.className = "summary";
  summary.textContent = e.summary;

  const ts = document.createElement("span");
  ts.className = "ts";
  ts.textContent = time;

  li.append(ts, kind, summary);

  if (e.details) {
    const det = document.createElement("pre");
    det.className = "details";
    det.textContent = JSON.stringify(e.details, null, 2);
    li.appendChild(det);
  }
  return li;
}

function renderBloomMeta(meta: PersistedBloomMeta | null) {
  if (!BLOOM_LOADED) return;
  if (!meta || !meta.loaded) {
    BLOOM_LOADED.textContent = "no";
    if (BLOOM_ITEMS) BLOOM_ITEMS.textContent = "-";
    if (BLOOM_BITS) BLOOM_BITS.textContent = "-";
    if (BLOOM_K) BLOOM_K.textContent = "-";
    if (BLOOM_FPR) BLOOM_FPR.textContent = "-";
    if (BLOOM_GENERATED) BLOOM_GENERATED.textContent = "-";
    if (BLOOM_BYTES) BLOOM_BYTES.textContent = "-";
    return;
  }
  BLOOM_LOADED.textContent = "yes";
  if (BLOOM_ITEMS) BLOOM_ITEMS.textContent = meta.itemCount.toLocaleString();
  if (BLOOM_BITS) BLOOM_BITS.textContent = meta.numBits.toLocaleString();
  if (BLOOM_K) BLOOM_K.textContent = String(meta.numHashes);
  if (BLOOM_FPR) {
    const pct = meta.estimatedFalsePositiveRate * 100;
    BLOOM_FPR.textContent = `${pct.toFixed(3)}%`;
  }
  if (BLOOM_GENERATED) {
    BLOOM_GENERATED.textContent = new Date(meta.generatedAtMillis).toISOString();
  }
  if (BLOOM_BYTES) {
    BLOOM_BYTES.textContent = `${meta.bytes.toLocaleString()} bytes`;
  }
}

function setRefreshStatus(text: string, kind: "ok" | "error" | "" = "") {
  if (!REFRESH_STATUS) return;
  REFRESH_STATUS.textContent = text;
  REFRESH_STATUS.className = `refresh-status refresh-status--${kind || "neutral"}`;
}

async function refreshDisplay() {
  const apiBase = await getApiBase();
  if (API_BASE_EL) API_BASE_EL.textContent = apiBase || DEFAULT_API_BASE;

  const fetchedAt = await readFetchedAt();
  if (FETCHED_AT_EL) {
    FETCHED_AT_EL.textContent = fetchedAt
      ? new Date(fetchedAt).toLocaleString()
      : "never";
  }

  const meta = await readBloomMeta();
  renderBloomMeta(meta);

  const lastError = await readLastError();
  if (lastError) {
    setRefreshStatus(`Last refresh failed: ${lastError}`, "error");
  } else if (meta?.loaded) {
    setRefreshStatus("Bloom filter loaded.", "ok");
  } else {
    setRefreshStatus(
      "Bloom filter not loaded. Click Refresh to download it now.",
      ""
    );
  }
}

async function requestRefresh(): Promise<void> {
  if (!REFRESH_BTN) return;
  REFRESH_BTN.setAttribute("disabled", "true");
  setRefreshStatus("Downloading bloom filter…", "");
  try {
    const resp = await chrome.runtime.sendMessage({ type: "pivs.refreshBloom" });
    if (resp?.ok) {
      setRefreshStatus("Bloom filter refreshed.", "ok");
    } else {
      setRefreshStatus(`Refresh failed: ${resp?.error ?? "unknown error"}`, "error");
    }
  } catch (err) {
    setRefreshStatus(
      `Refresh failed: ${err instanceof Error ? err.message : String(err)}`,
      "error"
    );
  } finally {
    REFRESH_BTN.removeAttribute("disabled");
    void refreshDisplay();
  }
}

async function init() {
  if (STATUS_EL) STATUS_EL.textContent = "Ready.";

  const enabled = await readDebugFlag();
  if (TOGGLE_EL) TOGGLE_EL.checked = enabled;
  if (PANEL_EL) PANEL_EL.hidden = !enabled;
  debugLog.setEnabled(enabled);

  await refreshDisplay();

  if (EVENTS_EL) {
    EVENTS_EL.innerHTML = "";
    for (const e of debugLog.entries()) {
      EVENTS_EL.appendChild(renderEvent(e));
    }
  }

  debugLog.subscribe((e) => {
    if (!EVENTS_EL) return;
    EVENTS_EL.appendChild(renderEvent(e));
  });

  TOGGLE_EL?.addEventListener("change", async () => {
    const on = !!TOGGLE_EL.checked;
    debugLog.setEnabled(on);
    await writeDebugFlag(on);
    if (PANEL_EL) PANEL_EL.hidden = !on;
  });

  CLEAR_BTN?.addEventListener("click", () => {
    debugLog.clear();
    if (EVENTS_EL) EVENTS_EL.innerHTML = "";
  });

  EXPORT_BTN?.addEventListener("click", () => {
    const blob = new Blob([debugLog.exportJson()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pivs-debug-${new Date().toISOString()}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  REFRESH_BTN?.addEventListener("click", () => {
    void requestRefresh();
  });

  // Reflect storage changes (e.g. background worker refresh) live.
  chrome.storage?.onChanged?.addListener((changes, area) => {
    if (area !== "local") return;
    if (
      STORAGE_KEYS.bloomMeta in changes ||
      STORAGE_KEYS.bloomFetchedAt in changes ||
      STORAGE_KEYS.bloomLastError in changes
    ) {
      void refreshDisplay();
    }
  });
}

void init();
