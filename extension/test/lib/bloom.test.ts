import { describe, expect, it } from "vitest";
import { BloomFilter } from "../../src/lib/bloom/bloom";
import { loadBloomFixture } from "../fixtures/loadBloomFixture";

describe("BloomFilter basics", () => {
  it("returns false for items never inserted", () => {
    const f = BloomFilter.forItems(1000, 0.01);
    expect(f.mightContain("a".repeat(64))).toBe(false);
  });

  it("returns true for inserted items (no false negatives)", () => {
    const f = BloomFilter.forItems(1000, 0.01);
    const inserted = Array.from({ length: 200 }, (_, i) => `hash-${i}`);
    for (const h of inserted) f.add(h);
    for (const h of inserted) {
      expect(f.mightContain(h)).toBe(true);
    }
  });

  it("yields a false positive rate roughly under the target", () => {
    const target = 0.01;
    const n = 1000;
    const f = BloomFilter.forItems(n, target);
    for (let i = 0; i < n; i++) f.add(`registered-${i}`);

    let fp = 0;
    const trials = 5000;
    for (let i = 0; i < trials; i++) {
      if (f.mightContain(`unregistered-${i}`)) fp++;
    }
    const rate = fp / trials;
    // Allow ~3x slack because the analytic FPR is an approximation
    // and stochastic variation can push small samples high.
    expect(rate).toBeLessThan(target * 3);
  });

  it("estimatedFalsePositiveRate increases with insertion", () => {
    const f = BloomFilter.forItems(100, 0.01);
    expect(f.estimatedFalsePositiveRate()).toBe(0);
    for (let i = 0; i < 100; i++) f.add(`x-${i}`);
    expect(f.estimatedFalsePositiveRate()).toBeGreaterThan(0);
    expect(f.estimatedFalsePositiveRate()).toBeLessThan(0.05);
  });
});

describe("BloomFilter serialization", () => {
  it("round-trips through serialize/deserialize", () => {
    const f = BloomFilter.forItems(500, 0.01);
    const items = Array.from({ length: 100 }, (_, i) => `item-${i}`);
    for (const x of items) f.add(x);

    const blob = f.serialize();
    const g = BloomFilter.deserialize(blob);

    expect(g.numBits).toBe(f.numBits);
    expect(g.numHashes).toBe(f.numHashes);
    expect(g.itemCount).toBe(f.itemCount);
    for (const x of items) {
      expect(g.mightContain(x)).toBe(true);
    }
  });

  it("rejects a blob with bad magic", () => {
    const bogus = new Uint8Array(64);
    expect(() => BloomFilter.deserialize(bogus)).toThrow();
  });

  it("exposes meta with item count and generation time", () => {
    const f = BloomFilter.forItems(100, 0.01);
    f.add("a");
    f.add("b");
    const meta = f.meta();
    expect(meta.itemCount).toBe(2);
    expect(meta.numBits).toBeGreaterThan(0);
    expect(meta.numHashes).toBeGreaterThan(0);
    expect(meta.generatedAtMillis).toBeGreaterThan(0);
  });
});

describe("BloomFilter wire-format compatibility with Python service", () => {
  it("decodes a server-generated snapshot and answers the same queries", () => {
    const { blob, meta } = loadBloomFixture();
    const f = BloomFilter.deserialize(blob);

    expect(f.numBits).toBe(meta.numBits);
    expect(f.numHashes).toBe(meta.numHashes);
    expect(f.itemCount).toBe(meta.itemCount);
    expect(f.generatedAtMillis).toBe(meta.generatedAtMillis);

    // Every "inserted" item from the fixture must hit the filter.
    for (const x of meta.inserted) {
      expect(f.mightContain(x)).toBe(true);
    }
    // Most "absent" items should miss. Allow ~5% slack for FP variance.
    const fps = meta.absent.filter((x) => f.mightContain(x)).length;
    expect(fps / meta.absent.length).toBeLessThan(0.05);
  });
});
