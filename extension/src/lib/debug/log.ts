/**
 * Transparent activity log for the extension.
 *
 * The Electoral Commission, security reviewers, and any curious user
 * must be able to see exactly what the extension is doing on their
 * device. The debug log records every step that touches an image:
 *
 *   - "image-seen": the content script noticed an image candidate
 *   - "ocr-result": OCR ran, with a boolean for promoter detection
 *   - "hash-computed": SHA-256/PDQ/pHash were computed locally
 *   - "bloom-check": the local bloom filter was queried, with the result
 *   - "api-call": a hash was sent to the server, with the response
 *   - "overlay-shown": a badge was rendered on the page
 *   - "flag-submitted": a user submitted a flag
 *
 * The log is held in memory (and optionally mirrored to chrome.storage
 * when debug mode is enabled). It can be inspected from the popup
 * Debug tab or exported to a JSON file. There is a hard cap of
 * MAX_ENTRIES so memory cannot grow without bound.
 */

export type DebugEventKind =
  | "image-seen"
  | "ocr-result"
  | "hash-computed"
  | "bloom-check"
  | "api-call"
  | "overlay-shown"
  | "flag-submitted"
  | "report-submitted"
  | "bloom-filter-loaded"
  | "error";

export interface DebugEvent {
  /** Unix millis. */
  ts: number;
  kind: DebugEventKind;
  /** Short, human-readable summary. */
  summary: string;
  /**
   * Structured details. Image bytes are NEVER stored here. Hashes,
   * page hosts, OCR text, and counts are fine.
   */
  details?: Record<string, unknown>;
}

const MAX_ENTRIES = 500;

class DebugLog {
  private buffer: DebugEvent[] = [];
  private enabled = false;
  private listeners = new Set<(e: DebugEvent) => void>();

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  isEnabled(): boolean {
    return this.enabled;
  }

  push(kind: DebugEventKind, summary: string, details?: Record<string, unknown>): void {
    const event: DebugEvent = {
      ts: Date.now(),
      kind,
      summary,
      details,
    };
    this.buffer.push(event);
    if (this.buffer.length > MAX_ENTRIES) {
      this.buffer.splice(0, this.buffer.length - MAX_ENTRIES);
    }
    if (this.enabled) {
      // eslint-disable-next-line no-console
      console.info(`[PIVS] ${kind}: ${summary}`, details ?? "");
    }
    for (const fn of this.listeners) fn(event);
  }

  entries(): readonly DebugEvent[] {
    return this.buffer.slice();
  }

  clear(): void {
    this.buffer = [];
  }

  subscribe(fn: (e: DebugEvent) => void): () => void {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  /** Export the log as a JSON string suitable for "Save log" in the popup. */
  exportJson(): string {
    return JSON.stringify(
      {
        exportedAt: new Date().toISOString(),
        entries: this.buffer,
      },
      null,
      2
    );
  }
}

export const debugLog = new DebugLog();
