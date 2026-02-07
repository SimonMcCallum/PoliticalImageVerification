"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface VerificationResult {
  verified: boolean;
  result: string;
  match_type: string;
  confidence: number;
  party?: { name: string; short_name: string };
  asset_id?: string;
  verification_id?: string;
  registered_date?: string;
  pdq_distance?: number;
  phash_distance?: number;
}

export default function ImageVerifier() {
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    // Show preview
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API_BASE}/api/v1/verify/image`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data: VerificationResult = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
      "image/webp": [".webp"],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  });

  return (
    <div>
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? "active" : ""}`}
      >
        <input {...getInputProps()} />
        {preview ? (
          <div>
            <img
              src={preview}
              alt="Uploaded"
              style={{
                maxWidth: "100%",
                maxHeight: "300px",
                borderRadius: "8px",
              }}
            />
            <p style={{ color: "#555", marginTop: "0.5rem" }}>
              Drop a different image or click to change
            </p>
          </div>
        ) : (
          <div>
            <p style={{ fontSize: "1.25rem", fontWeight: 500, margin: "0 0 0.5rem" }}>
              {isDragActive
                ? "Drop the image here..."
                : "Drag & drop a political image here"}
            </p>
            <p style={{ color: "#555", margin: 0 }}>
              or click to select a file (JPEG, PNG, WebP up to 50MB)
            </p>
          </div>
        )}
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "2rem" }}>
          <p style={{ fontSize: "1.125rem" }}>Verifying image...</p>
          <p style={{ color: "#555" }}>
            Computing hashes and searching the registry
          </p>
        </div>
      )}

      {error && (
        <div className="result-unverified" style={{ marginTop: "1.5rem" }}>
          <h3 style={{ margin: "0 0 0.5rem", color: "#dc2626" }}>Error</h3>
          <p style={{ margin: 0 }}>{error}</p>
        </div>
      )}

      {result && !loading && (
        <div
          className={result.verified ? "result-verified" : "result-unverified"}
          style={{ marginTop: "1.5rem" }}
        >
          {result.verified ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem" }}>
                <span style={{ fontSize: "2rem" }}>&#x2705;</span>
                <div>
                  <h2 style={{ margin: 0, color: "#16a34a" }}>
                    VERIFIED
                  </h2>
                  <p style={{ margin: 0, color: "#555" }}>
                    This image is registered by a political party
                  </p>
                </div>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <tbody>
                  <tr>
                    <td style={{ padding: "0.5rem 0", fontWeight: 500 }}>Party</td>
                    <td style={{ padding: "0.5rem 0" }}>{result.party?.name}</td>
                  </tr>
                  <tr>
                    <td style={{ padding: "0.5rem 0", fontWeight: 500 }}>Match Type</td>
                    <td style={{ padding: "0.5rem 0" }}>
                      {result.match_type === "exact"
                        ? "Exact match"
                        : `Perceptual match (${Math.round(result.confidence * 100)}% confidence)`}
                    </td>
                  </tr>
                  <tr>
                    <td style={{ padding: "0.5rem 0", fontWeight: 500 }}>Registered</td>
                    <td style={{ padding: "0.5rem 0" }}>
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
                    <td style={{ padding: "0.5rem 0", fontWeight: 500 }}>Verification ID</td>
                    <td style={{ padding: "0.5rem 0", fontFamily: "monospace" }}>
                      {result.verification_id}
                    </td>
                  </tr>
                  {result.pdq_distance !== null && result.pdq_distance !== undefined && (
                    <tr>
                      <td style={{ padding: "0.5rem 0", fontWeight: 500 }}>PDQ Distance</td>
                      <td style={{ padding: "0.5rem 0" }}>
                        {result.pdq_distance} / 31 (lower is better)
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </>
          ) : (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <span style={{ fontSize: "2rem" }}>&#x274C;</span>
                <div>
                  <h2 style={{ margin: 0, color: "#dc2626" }}>
                    NOT VERIFIED
                  </h2>
                  <p style={{ margin: 0, color: "#555" }}>
                    This image is not registered by any political party in our
                    system. This does not necessarily mean it is fake &mdash; the
                    party may not have registered it yet.
                  </p>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
