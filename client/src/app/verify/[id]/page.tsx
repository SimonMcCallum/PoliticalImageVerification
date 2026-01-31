"use client";

import "../../globals.css";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface VerificationByIdResult {
  verified: boolean;
  party_name: string | null;
  party_short_name: string | null;
  registered_date: string | null;
  status: string | null;
  verification_id: string;
}

export default function VerifyByIdPage() {
  const params = useParams();
  const id = params.id as string;
  const [result, setResult] = useState<VerificationByIdResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function verify() {
      try {
        const res = await fetch(`/api/v1/verify/${id}`);
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        const data = await res.json();
        setResult(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Verification failed");
      } finally {
        setLoading(false);
      }
    }

    verify();
  }, [id]);

  if (loading) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <h2>Verifying...</h2>
        <p style={{ color: "#555" }}>
          Looking up verification ID: <code>{id}</code>
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="result-unverified">
          <h2 style={{ color: "#dc2626", marginTop: 0 }}>Verification Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
        <h2>Image Verification Result</h2>
        <p style={{ color: "#555" }}>
          Verification ID: <code>{id}</code>
        </p>
      </div>

      {result?.verified ? (
        <div className="result-verified">
          <div
            style={{
              textAlign: "center",
              marginBottom: "1.5rem",
            }}
          >
            <span style={{ fontSize: "3rem" }}>&#x2705;</span>
            <h2 style={{ color: "#16a34a", margin: "0.5rem 0 0" }}>
              VERIFIED
            </h2>
            <p style={{ color: "#555" }}>
              This image is officially registered by a New Zealand political
              party.
            </p>
          </div>

          <div className="card" style={{ maxWidth: "500px", margin: "0 auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <tbody>
                <tr>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      fontWeight: 600,
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    Political Party
                  </td>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    {result.party_name}
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      fontWeight: 600,
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    Short Name
                  </td>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    {result.party_short_name}
                  </td>
                </tr>
                <tr>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      fontWeight: 600,
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    Registration Date
                  </td>
                  <td
                    style={{
                      padding: "0.75rem 0",
                      borderBottom: "1px solid #e2e8f0",
                    }}
                  >
                    {result.registered_date
                      ? new Date(result.registered_date).toLocaleDateString(
                          "en-NZ",
                          {
                            year: "numeric",
                            month: "long",
                            day: "numeric",
                          }
                        )
                      : "N/A"}
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: "0.75rem 0", fontWeight: 600 }}>
                    Status
                  </td>
                  <td style={{ padding: "0.75rem 0" }}>
                    <span
                      style={{
                        background: "#dcfce7",
                        color: "#166534",
                        padding: "0.25rem 0.75rem",
                        borderRadius: "4px",
                        fontWeight: 500,
                      }}
                    >
                      {result.status}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="result-unverified">
          <div style={{ textAlign: "center" }}>
            <span style={{ fontSize: "3rem" }}>&#x274C;</span>
            <h2 style={{ color: "#dc2626", margin: "0.5rem 0 0" }}>
              NOT VERIFIED
            </h2>
            <p style={{ color: "#555", maxWidth: "500px", margin: "1rem auto 0" }}>
              No registered image was found with this verification ID. The image
              may have been revoked, expired, or this ID may not be valid.
            </p>
            {result?.status && result.status !== "not_found" && (
              <p style={{ color: "#555" }}>
                Status: <strong>{result.status}</strong>
              </p>
            )}
          </div>
        </div>
      )}

      <div style={{ textAlign: "center", marginTop: "2rem" }}>
        <a href="/" className="btn btn-primary">
          Verify another image
        </a>
      </div>
    </div>
  );
}
