/**
 * Popup script.
 *
 * - Renders a status line.
 * - Lets the user toggle debug (transparency) mode.
 * - When debug mode is on, shows the bloom-filter metadata and a live
 *   tail of every relevant event the extension has produced.
 *
 * The popup reads its data from the in-memory debugLog plus
 * chrome.storage for the persistent toggle and bloom-filter meta.
 */

import { debugLog, type DebugEvent } from "../lib/debug/log";

const STATUS_EL = document.getElementById("status");
const TOGGLE_EL = document.getElementById("debug-toggle") as HTMLInputElement | null;
const PANEL_EL = document.getElementById("debug-panel");
const EVENTS_EL = document.getElementById("debug-events");
const CLEAR_BTN = document.getElementById("debug-clear");
const EXPORT_BTN = document.getElementById("debug-export");

const BLOOM_LOADED = document.getElementById("bloom-loaded");
const BLOOM_ITEMS = document.getElementById("bloom-items");
const BLOOM_BITS = document.getElementById("bloom-bits");
const BLOOM_K = document.getElementById("bloom-k");
const BLOOM_FPR = document.getElementById("bloom-fpr");
const BLOOM_GENERATED = document.getElementById("bloom-generated");

const DEBUG_KEY = "pivs.debugMode";
const BLOOM_META_KEY = "pivs.bloomMeta";

interface PersistedBloomMeta {
  loaded: boolean;
  numBits: number;
  numHashes: number;
  itemCount: number;
  estimatedFalsePositiveRate: number;
  generatedAtMillis: number;
}

async function readDebugFlag(): Promise<boolean> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return false;
  return new Promise((resolve) => {
    chrome.storage.local.get(DEBUG_KEY, (v) => resolve(Boolean(v[DEBUG_KEY])));
  });
}

async function writeDebugFlag(on: boolean): Promise<void> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return;
  return new Promise((resolve) => {
    chrome.storage.local.set({ [DEBUG_KEY]: on }, () => resolve());
  });
}

async function readBloomMeta(): Promise<PersistedBloomMeta | null> {
  if (typeof chrome === "undefined" || !chrome.storage?.local) return null;
  return new Promise((resolve) => {
    chrome.storage.local.get(BLOOM_META_KEY, (v) =>
      resolve((v[BLOOM_META_KEY] as PersistedBloomMeta) ?? null)
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
}

async function init() {
  if (STATUS_EL) STATUS_EL.textContent = "Ready.";

  const enabled = await readDebugFlag();
  if (TOGGLE_EL) TOGGLE_EL.checked = enabled;
  if (PANEL_EL) PANEL_EL.hidden = !enabled;
  debugLog.setEnabled(enabled);

  const meta = await readBloomMeta();
  renderBloomMeta(meta);

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
}

void init();
