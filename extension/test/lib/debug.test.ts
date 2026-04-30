import { afterEach, describe, expect, it, vi } from "vitest";
import { debugLog } from "../../src/lib/debug/log";

afterEach(() => {
  debugLog.clear();
  debugLog.setEnabled(false);
});

describe("debugLog", () => {
  it("records events and returns them in order", () => {
    debugLog.push("image-seen", "img on example.com", { src: "/foo.jpg" });
    debugLog.push("hash-computed", "sha256 done");
    const entries = debugLog.entries();
    expect(entries).toHaveLength(2);
    expect(entries[0]!.kind).toBe("image-seen");
    expect(entries[0]!.summary).toContain("example.com");
    expect(entries[1]!.kind).toBe("hash-computed");
  });

  it("never grows beyond the cap", () => {
    for (let i = 0; i < 600; i++) {
      debugLog.push("image-seen", `image ${i}`);
    }
    expect(debugLog.entries().length).toBeLessThanOrEqual(500);
    // The most recent event survives.
    const last = debugLog.entries().at(-1)!;
    expect(last.summary).toBe("image 599");
  });

  it("notifies subscribers on each event", () => {
    const fn = vi.fn();
    const unsub = debugLog.subscribe(fn);
    debugLog.push("api-call", "POST /verify/hash");
    expect(fn).toHaveBeenCalledTimes(1);
    unsub();
    debugLog.push("api-call", "POST /verify/hash again");
    expect(fn).toHaveBeenCalledTimes(1); // unsubscribed
  });

  it("exports as JSON", () => {
    debugLog.push("bloom-check", "miss", { hash: "abc" });
    const out = debugLog.exportJson();
    const parsed = JSON.parse(out);
    expect(parsed.entries).toHaveLength(1);
    expect(parsed.entries[0].kind).toBe("bloom-check");
  });

  it("setEnabled toggles console mirroring without breaking buffering", () => {
    debugLog.setEnabled(true);
    debugLog.push("overlay-shown", "amber");
    debugLog.setEnabled(false);
    expect(debugLog.entries()).toHaveLength(1);
  });
});
