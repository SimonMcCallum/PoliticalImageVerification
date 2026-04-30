/**
 * Typed client for the PIVS public and extension API.
 *
 * The extension talks to two endpoint groups:
 *  - /api/v1/verify/hash  : check a hash against the register
 *  - /api/v1/extension/*  : report unregistered-with-promoter and flag
 *
 * All methods return structured results rather than raising so that
 * UI code can render "network error" as a first-class outcome.
 */

export type VerifyResult =
  | {
      kind: "registered";
      partyName: string;
      partyShortName: string;
      verificationId: string | null;
      confidence: number;
      matchType: "exact" | "perceptual";
    }
  | { kind: "not_found" }
  | { kind: "error"; message: string };

export interface VerifyHashRequest {
  sha256?: string;
  pdq?: string;
  phash?: string;
}

export interface ReportRequest {
  sha256?: string;
  pdq?: string;
  phash?: string;
  detectedPromoterText?: string;
  pageUrlHost?: string;
}

export type FlagReason =
  | "misattributed"
  | "promoter_statement_fake"
  | "content_concern"
  | "other";

export interface FlagRequest {
  sha256?: string;
  pdq?: string;
  phash?: string;
  reason: FlagReason;
  note?: string;
  pageUrlHost?: string;
}

export interface ClientOptions {
  /** Base URL of the PIVS API, without trailing slash. */
  baseUrl: string;
  /** Replace in tests. */
  fetchImpl?: typeof fetch;
}

export class PivsApiClient {
  private baseUrl: string;
  private fetchImpl: typeof fetch;

  constructor(opts: ClientOptions) {
    this.baseUrl = opts.baseUrl.replace(/\/+$/, "");
    this.fetchImpl = opts.fetchImpl ?? fetch;
  }

  async verifyHash(req: VerifyHashRequest): Promise<VerifyResult> {
    try {
      const resp = await this.fetchImpl(`${this.baseUrl}/api/v1/verify/hash`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      if (!resp.ok) {
        return { kind: "error", message: `HTTP ${resp.status}` };
      }
      const data = (await resp.json()) as {
        verified: boolean;
        match_type: "exact" | "perceptual" | "none";
        confidence: number;
        party?: { name: string; short_name: string };
        verification_id?: string | null;
      };
      if (!data.verified || data.match_type === "none" || !data.party) {
        return { kind: "not_found" };
      }
      return {
        kind: "registered",
        partyName: data.party.name,
        partyShortName: data.party.short_name,
        verificationId: data.verification_id ?? null,
        confidence: data.confidence,
        matchType: data.match_type,
      };
    } catch (err) {
      return {
        kind: "error",
        message: err instanceof Error ? err.message : "unknown",
      };
    }
  }

  async report(req: ReportRequest): Promise<{ accepted: boolean; id?: string }> {
    const resp = await this.fetchImpl(`${this.baseUrl}/api/v1/extension/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sha256: req.sha256,
        pdq: req.pdq,
        phash: req.phash,
        detected_promoter_text: req.detectedPromoterText,
        page_url_host: req.pageUrlHost,
      }),
    });
    if (!resp.ok) return { accepted: false };
    const data = (await resp.json()) as { accepted: boolean; report_id?: string };
    return { accepted: data.accepted, id: data.report_id };
  }

  async flag(req: FlagRequest): Promise<{ accepted: boolean; id?: string }> {
    const resp = await this.fetchImpl(`${this.baseUrl}/api/v1/extension/flag`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sha256: req.sha256,
        pdq: req.pdq,
        phash: req.phash,
        reason: req.reason,
        note: req.note,
        page_url_host: req.pageUrlHost,
      }),
    });
    if (!resp.ok) return { accepted: false };
    const data = (await resp.json()) as { accepted: boolean; flag_id?: string };
    return { accepted: data.accepted, id: data.flag_id };
  }
}
