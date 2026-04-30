import { describe, expect, it } from "vitest";
import { sha256Hex } from "../../src/lib/hash/sha256";

describe("sha256Hex", () => {
  it("computes SHA-256 for empty input (RFC 6234)", async () => {
    const empty = new Uint8Array(0);
    const hex = await sha256Hex(empty);
    expect(hex).toBe(
      "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    );
  });

  it("computes SHA-256 for 'abc' (FIPS 180-2 test vector)", async () => {
    const bytes = new TextEncoder().encode("abc");
    const hex = await sha256Hex(bytes);
    expect(hex).toBe(
      "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    );
  });

  it("produces a 64-character hex string", async () => {
    const bytes = new TextEncoder().encode("Political Image Verification");
    const hex = await sha256Hex(bytes);
    expect(hex).toMatch(/^[0-9a-f]{64}$/);
  });
});
