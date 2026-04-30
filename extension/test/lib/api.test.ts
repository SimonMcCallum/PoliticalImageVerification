import { describe, expect, it, vi } from "vitest";
import { PivsApiClient } from "../../src/lib/api/client";

const BASE = "http://test.local";

function mockFetch(response: Partial<Response> & { jsonBody?: unknown }) {
  return vi.fn(async () => ({
    ok: response.ok ?? true,
    status: response.status ?? 200,
    json: async () => response.jsonBody,
  })) as unknown as typeof fetch;
}

describe("PivsApiClient.verifyHash", () => {
  it("returns 'registered' for a verified response", async () => {
    const fetchImpl = mockFetch({
      jsonBody: {
        verified: true,
        result: "verified",
        match_type: "exact",
        confidence: 1.0,
        party: { name: "Test Party", short_name: "TP" },
        verification_id: "v123",
      },
    });
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.verifyHash({ sha256: "a".repeat(64) });
    expect(r.kind).toBe("registered");
    if (r.kind === "registered") {
      expect(r.partyName).toBe("Test Party");
      expect(r.matchType).toBe("exact");
    }
  });

  it("returns 'not_found' for an unverified response", async () => {
    const fetchImpl = mockFetch({
      jsonBody: {
        verified: false,
        result: "unverified",
        match_type: "none",
        confidence: 0,
      },
    });
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.verifyHash({ pdq: "b".repeat(64) });
    expect(r.kind).toBe("not_found");
  });

  it("returns 'error' for a non-2xx status", async () => {
    const fetchImpl = mockFetch({ ok: false, status: 500 });
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.verifyHash({ sha256: "x".repeat(64) });
    expect(r.kind).toBe("error");
  });

  it("returns 'error' when the fetch throws", async () => {
    const fetchImpl = vi.fn(async () => {
      throw new Error("network down");
    }) as unknown as typeof fetch;
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.verifyHash({ sha256: "x".repeat(64) });
    expect(r.kind).toBe("error");
    if (r.kind === "error") expect(r.message).toBe("network down");
  });
});

describe("PivsApiClient.report", () => {
  it("sends snake_case body and returns accepted", async () => {
    const fetchImpl = vi.fn(async (_url, init) => {
      const body = JSON.parse(init!.body as string);
      expect(body.detected_promoter_text).toBe("Authorised by A. B.");
      expect(body.page_url_host).toBe("example.com");
      return {
        ok: true,
        status: 200,
        json: async () => ({ accepted: true, report_id: "r-1" }),
      };
    }) as unknown as typeof fetch;
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.report({
      pdq: "c".repeat(64),
      detectedPromoterText: "Authorised by A. B.",
      pageUrlHost: "example.com",
    });
    expect(r.accepted).toBe(true);
    expect(r.id).toBe("r-1");
  });
});

describe("PivsApiClient.flag", () => {
  it("submits with reason and note", async () => {
    const fetchImpl = vi.fn(async (_url, init) => {
      const body = JSON.parse(init!.body as string);
      expect(body.reason).toBe("misattributed");
      expect(body.note).toBe("looks fake");
      return {
        ok: true,
        status: 200,
        json: async () => ({ accepted: true, flag_id: "f-1" }),
      };
    }) as unknown as typeof fetch;
    const client = new PivsApiClient({ baseUrl: BASE, fetchImpl });
    const r = await client.flag({
      sha256: "1".repeat(64),
      reason: "misattributed",
      note: "looks fake",
    });
    expect(r.accepted).toBe(true);
    expect(r.id).toBe("f-1");
  });
});
