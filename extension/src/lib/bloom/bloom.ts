/**
 * Bloom filter for "is this hash possibly in the register?".
 *
 * The extension downloads a bloom filter snapshot from the server.
 * Every image hash is checked locally against the filter. Only
 * "maybe present" hashes are escalated to a real server lookup,
 * which gives strong privacy: most lookups never leave the device,
 * and the server cannot tell which images a user is browsing.
 *
 * False positive rate is tuned at filter generation time.
 *
 * Hashing strategy uses Kirsch-Mitzenmacher: derive k indices from
 * two base hashes (FNV-1a 32-bit and djb2 32-bit), so the filter is
 * cheap to query in a content script.
 *
 * Wire format (versioned, little-endian):
 *   bytes 0..3   magic "PIBF"
 *   bytes 4      version (uint8, currently 1)
 *   byte  5      reserved
 *   bytes 6..9   numBits (uint32 LE)
 *   bytes 10..11 numHashes k (uint16 LE)
 *   bytes 12..19 itemCount (uint64 LE, items inserted)
 *   bytes 20..27 generatedAt (uint64 LE, unix millis)
 *   bytes 28..   bit array, ceil(numBits / 8) bytes
 *
 * Total size for ~5,000 items at 0.1% FPR:
 *   m = -n*ln(p)/(ln(2)^2) ~ 71,800 bits ~ 9 KB
 * Easily fits in an extension package or a one-shot download.
 */

const MAGIC = "PIBF";
const VERSION = 1;
const HEADER_BYTES = 28;

export interface BloomFilterMeta {
  numBits: number;
  numHashes: number;
  itemCount: number;
  generatedAtMillis: number;
}

export class BloomFilter {
  readonly numBits: number;
  readonly numHashes: number;
  readonly bits: Uint8Array;
  itemCount: number;
  generatedAtMillis: number;

  constructor(numBits: number, numHashes: number, bits?: Uint8Array) {
    if (numBits <= 0 || !Number.isInteger(numBits)) {
      throw new Error("numBits must be a positive integer");
    }
    if (numHashes <= 0 || !Number.isInteger(numHashes)) {
      throw new Error("numHashes must be a positive integer");
    }
    this.numBits = numBits;
    this.numHashes = numHashes;
    const byteLen = Math.ceil(numBits / 8);
    if (bits !== undefined) {
      if (bits.length !== byteLen) {
        throw new Error(`bits length ${bits.length} does not match expected ${byteLen}`);
      }
      this.bits = bits;
    } else {
      this.bits = new Uint8Array(byteLen);
    }
    this.itemCount = 0;
    this.generatedAtMillis = Date.now();
  }

  /**
   * Build a bloom filter sized for an expected number of items
   * and a target false positive rate.
   */
  static forItems(expectedItems: number, falsePositiveRate: number): BloomFilter {
    if (expectedItems <= 0) throw new Error("expectedItems must be > 0");
    if (falsePositiveRate <= 0 || falsePositiveRate >= 1) {
      throw new Error("falsePositiveRate must be in (0, 1)");
    }
    const ln2 = Math.log(2);
    const numBits = Math.max(
      8,
      Math.ceil(-(expectedItems * Math.log(falsePositiveRate)) / (ln2 * ln2))
    );
    const numHashes = Math.max(1, Math.round((numBits / expectedItems) * ln2));
    return new BloomFilter(numBits, numHashes);
  }

  /** Insert a hex string (e.g. a hash) into the filter. */
  add(hex: string): void {
    const [h1, h2] = baseHashes(hex);
    for (let i = 0; i < this.numHashes; i++) {
      const idx = combine(h1, h2, i, this.numBits);
      this.bits[idx >>> 3]! |= 1 << (idx & 7);
    }
    this.itemCount++;
  }

  /**
   * Test a hex string. Returns true if the value is "maybe in the
   * filter" (with a small false positive rate), false if it is
   * definitely not present.
   */
  mightContain(hex: string): boolean {
    const [h1, h2] = baseHashes(hex);
    for (let i = 0; i < this.numHashes; i++) {
      const idx = combine(h1, h2, i, this.numBits);
      if ((this.bits[idx >>> 3]! & (1 << (idx & 7))) === 0) return false;
    }
    return true;
  }

  /** Empirical false positive rate estimate for the current population. */
  estimatedFalsePositiveRate(): number {
    const n = this.itemCount;
    const m = this.numBits;
    const k = this.numHashes;
    return Math.pow(1 - Math.exp((-k * n) / m), k);
  }

  meta(): BloomFilterMeta {
    return {
      numBits: this.numBits,
      numHashes: this.numHashes,
      itemCount: this.itemCount,
      generatedAtMillis: this.generatedAtMillis,
    };
  }

  /** Serialise to a self-describing binary blob. */
  serialize(): Uint8Array {
    const out = new Uint8Array(HEADER_BYTES + this.bits.length);
    const enc = new TextEncoder();
    out.set(enc.encode(MAGIC), 0);
    out[4] = VERSION;
    out[5] = 0;
    const view = new DataView(out.buffer);
    view.setUint32(6, this.numBits, true);
    view.setUint16(10, this.numHashes, true);
    view.setBigUint64(12, BigInt(this.itemCount), true);
    view.setBigUint64(20, BigInt(this.generatedAtMillis), true);
    out.set(this.bits, HEADER_BYTES);
    return out;
  }

  /** Deserialise from a blob produced by serialize(). */
  static deserialize(blob: Uint8Array): BloomFilter {
    if (blob.length < HEADER_BYTES) {
      throw new Error("bloom filter blob too short");
    }
    const dec = new TextDecoder();
    const magic = dec.decode(blob.slice(0, 4));
    if (magic !== MAGIC) throw new Error(`bad magic: ${magic}`);
    if (blob[4] !== VERSION) throw new Error(`bad version: ${blob[4]}`);
    const view = new DataView(blob.buffer, blob.byteOffset, blob.byteLength);
    const numBits = view.getUint32(6, true);
    const numHashes = view.getUint16(10, true);
    const itemCount = Number(view.getBigUint64(12, true));
    const generatedAt = Number(view.getBigUint64(20, true));
    const byteLen = Math.ceil(numBits / 8);
    if (blob.length < HEADER_BYTES + byteLen) {
      throw new Error("bloom filter blob truncated");
    }
    const bits = blob.slice(HEADER_BYTES, HEADER_BYTES + byteLen);
    const f = new BloomFilter(numBits, numHashes, bits);
    f.itemCount = itemCount;
    f.generatedAtMillis = generatedAt;
    return f;
  }
}

/**
 * Two 32-bit hashes (FNV-1a and djb2) over the UTF-8 bytes of the input.
 * Returned as unsigned 32-bit ints.
 */
function baseHashes(s: string): [number, number] {
  let fnv = 0x811c9dc5 >>> 0;
  let djb2 = 5381 >>> 0;
  for (let i = 0; i < s.length; i++) {
    const c = s.charCodeAt(i);
    fnv = (fnv ^ c) >>> 0;
    fnv = Math.imul(fnv, 0x01000193) >>> 0;
    djb2 = (Math.imul(djb2, 33) + c) >>> 0;
  }
  return [fnv, djb2];
}

function combine(h1: number, h2: number, i: number, mod: number): number {
  // Kirsch-Mitzenmacher: idx = (h1 + i*h2) mod m, with a final mix.
  const v = (h1 + Math.imul(i, h2)) >>> 0;
  return v % mod;
}
