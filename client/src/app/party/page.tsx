"use client";

import "../globals.css";
import { useState, FormEvent } from "react";

interface Asset {
  id: string;
  verification_id: string;
  mime_type: string;
  file_size: number;
  status: string;
  created_at: string;
  sha256_hash: string;
  pdq_hash: string;
  verification_url: string;
  qr_code_url: string;
}

export default function PartyPortal() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<Asset | null>(null);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setLoginError(null);

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          password,
          mfa_code: mfaCode || null,
        }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }

      const data = await res.json();
      setToken(data.access_token);
      await loadAssets(data.access_token);
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    }
  }

  async function loadAssets(accessToken: string) {
    const res = await fetch("/api/v1/assets", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (res.ok) {
      const data = await res.json();
      setAssets(data);
    }
  }

  async function handleUpload(e: FormEvent) {
    e.preventDefault();
    if (!token) return;

    const form = e.target as HTMLFormElement;
    const fileInput = form.elements.namedItem("file") as HTMLInputElement;
    const file = fileInput?.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/v1/assets", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Upload failed");
      }

      const data: Asset = await res.json();
      setUploadResult(data);
      await loadAssets(token);
      form.reset();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  // Not logged in - show login form
  if (!token) {
    return (
      <div className="container">
        <h2 style={{ textAlign: "center" }}>Party Portal</h2>
        <p style={{ textAlign: "center", color: "#555" }}>
          Log in with your party account to submit and manage campaign images.
        </p>

        <div className="card" style={{ maxWidth: "400px", margin: "0 auto" }}>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="label">Username</label>
              <input
                className="input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="label">Password</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="label">MFA Code (if enabled)</label>
              <input
                className="input"
                type="text"
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                placeholder="Optional"
              />
            </div>
            {loginError && (
              <p style={{ color: "#dc2626", margin: "0 0 1rem" }}>
                {loginError}
              </p>
            )}
            <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
              Log In
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Logged in - show dashboard
  return (
    <div className="container">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <h2 style={{ margin: 0 }}>Party Portal</h2>
        <button
          className="btn"
          style={{ background: "#e2e8f0" }}
          onClick={() => { setToken(null); setAssets([]); }}
        >
          Log Out
        </button>
      </div>

      {/* Upload Form */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0 }}>Submit a Campaign Image</h3>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label className="label">Image File</label>
            <input
              className="input"
              type="file"
              name="file"
              accept="image/jpeg,image/png,image/webp"
              required
            />
          </div>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading}
          >
            {uploading ? "Uploading & Hashing..." : "Register Image"}
          </button>
        </form>

        {uploadResult && (
          <div
            className="result-verified"
            style={{ marginTop: "1rem" }}
          >
            <h4 style={{ margin: "0 0 0.5rem" }}>Image Registered</h4>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <tbody>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>Verification ID</td>
                  <td style={{ fontFamily: "monospace" }}>{uploadResult.verification_id}</td>
                </tr>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>Verification URL</td>
                  <td>
                    <a href={uploadResult.verification_url}>{uploadResult.verification_url}</a>
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>SHA-256</td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.75rem", wordBreak: "break-all" }}>
                    {uploadResult.sha256_hash}
                  </td>
                </tr>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>PDQ Hash</td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.75rem", wordBreak: "break-all" }}>
                    {uploadResult.pdq_hash}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Asset List */}
      <div className="card">
        <h3 style={{ marginTop: 0 }}>
          Registered Assets ({assets.length})
        </h3>
        {assets.length === 0 ? (
          <p style={{ color: "#555" }}>No images registered yet.</p>
        ) : (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              fontSize: "0.875rem",
            }}
          >
            <thead>
              <tr style={{ borderBottom: "2px solid #e2e8f0" }}>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>
                  Verification ID
                </th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Type</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Size</th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>
                  Status
                </th>
                <th style={{ textAlign: "left", padding: "0.5rem" }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr
                  key={asset.id}
                  style={{ borderBottom: "1px solid #e2e8f0" }}
                >
                  <td
                    style={{
                      padding: "0.5rem",
                      fontFamily: "monospace",
                    }}
                  >
                    {asset.verification_id}
                  </td>
                  <td style={{ padding: "0.5rem" }}>{asset.mime_type}</td>
                  <td style={{ padding: "0.5rem" }}>
                    {(asset.file_size / 1024).toFixed(1)} KB
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    <span
                      style={{
                        background:
                          asset.status === "active" ? "#dcfce7" : "#fecaca",
                        color:
                          asset.status === "active" ? "#166534" : "#991b1b",
                        padding: "0.125rem 0.5rem",
                        borderRadius: "4px",
                        fontSize: "0.75rem",
                        fontWeight: 500,
                      }}
                    >
                      {asset.status}
                    </span>
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    {new Date(asset.created_at).toLocaleDateString("en-NZ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
