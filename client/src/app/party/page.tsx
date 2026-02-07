"use client";

import "../globals.css";
import { useState, useEffect, FormEvent } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Asset {
  id: string;
  verification_id: string;
  mime_type: string;
  file_size: number;
  status: string;
  created_at: string;
  sha256_hash: string;
  pdq_hash: string;
  phash: string;
  verification_url: string;
  qr_code_url: string;
  promoter_image_url: string | null;
  promoter_check: PromoterCheck | null;
}

interface PromoterCheck {
  found: boolean;
  confidence: number;
  extracted_text: string;
  best_match: string | null;
  match_ratio: number;
}

const POSITIONS = [
  { value: "bottom-left", label: "Bottom Left" },
  { value: "bottom-right", label: "Bottom Right" },
  { value: "top-left", label: "Top Left" },
  { value: "top-right", label: "Top Right" },
];

export default function PartyPortal() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<Asset | null>(null);

  // Promoter statement state
  const [promoterStatement, setPromoterStatement] = useState("");
  const [promoterUpdatedAt, setPromoterUpdatedAt] = useState<string | null>(null);
  const [editingStatement, setEditingStatement] = useState(false);
  const [statementDraft, setStatementDraft] = useState("");
  const [savingStatement, setSavingStatement] = useState(false);
  const [partyId, setPartyId] = useState<string | null>(null);

  // Upload options
  const [addPromoter, setAddPromoter] = useState(false);
  const [checkPromoter, setCheckPromoter] = useState(false);
  const [uploadPosition, setUploadPosition] = useState("bottom-left");

  // Batch mode state
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [batchPosition, setBatchPosition] = useState("bottom-left");
  const [batchProcessing, setBatchProcessing] = useState(false);

  // Default position
  const [defaultPosition, setDefaultPosition] = useState("bottom-left");
  const [savingPosition, setSavingPosition] = useState(false);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setLoginError(null);

    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
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
      if (data.party_id) setPartyId(data.party_id);
      if (data.default_statement_position) {
        setDefaultPosition(data.default_statement_position);
        setUploadPosition(data.default_statement_position);
        setBatchPosition(data.default_statement_position);
      }
      await Promise.all([
        loadAssets(data.access_token),
        loadPromoterStatement(data.access_token, data.party_id),
      ]);
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    }
  }

  async function loadAssets(accessToken: string) {
    const res = await fetch(`${API_BASE}/api/v1/assets`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (res.ok) {
      const data = await res.json();
      setAssets(data);
    }
  }

  async function loadPromoterStatement(accessToken: string, pid: string) {
    if (!pid) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/parties/${pid}/promoter-statement`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        const data = await res.json();
        setPromoterStatement(data.statement || "");
        setPromoterUpdatedAt(data.updated_at);
      }
    } catch {
      // Statement not set yet
    }
  }

  async function handleSaveStatement() {
    if (!token || !partyId) return;
    setSavingStatement(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/parties/${partyId}/promoter-statement`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ statement: statementDraft }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to save");
      }
      const data = await res.json();
      setPromoterStatement(data.statement);
      setPromoterUpdatedAt(data.updated_at);
      setEditingStatement(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save statement");
    } finally {
      setSavingStatement(false);
    }
  }

  async function handleSaveDefaultPosition() {
    if (!token) return;
    setSavingPosition(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/parties/me/default-position`, {
        method: "PATCH",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ position: defaultPosition }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to save");
      }
      setUploadPosition(defaultPosition);
      setBatchPosition(defaultPosition);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save position");
    } finally {
      setSavingPosition(false);
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
      if (addPromoter) {
        formData.append("add_promoter_statement", "true");
        formData.append("promoter_position", uploadPosition);
      }
      if (checkPromoter) {
        formData.append("check_promoter_statement", "true");
      }

      const res = await fetch(`${API_BASE}/api/v1/assets`, {
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

  async function handleBatchDownload() {
    if (!token || !batchFile) return;
    setBatchProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", batchFile);
      formData.append("position", batchPosition);

      const res = await fetch(`${API_BASE}/api/v1/assets/add-promoter`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Processing failed");
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "promoter_stamped.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setBatchFile(null);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Processing failed");
    } finally {
      setBatchProcessing(false);
    }
  }

  // Not logged in - show login form
  if (!token) {
    return (
      <div className="container">
        <h2 style={{ textAlign: "center" }}>Party Portal</h2>
        <p style={{ textAlign: "center", color: "#666666" }}>
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
              <p style={{ color: "#DC3545", margin: "0 0 1rem" }}>
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
    <div className="container" style={{ maxWidth: "900px" }}>
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
          style={{ background: "#D8D8D8" }}
          onClick={() => {
            setToken(null);
            setAssets([]);
            setPromoterStatement("");
            setPartyId(null);
          }}
        >
          Log Out
        </button>
      </div>

      {/* Promoter Statement Management */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0 }}>Promoter Statement</h3>
        <p style={{ color: "#666666", fontSize: "0.875rem", marginTop: 0 }}>
          Under the Electoral Act (section 204F), all political advertisements must include a
          promoter statement identifying who authorised the content. Set your party&apos;s
          promoter statement here to use across all campaign materials.
        </p>

        {!editingStatement ? (
          <>
            {promoterStatement ? (
              <div
                style={{
                  background: "#F5F5F5",
                  border: "1px solid #D8D8D8",
                  borderRadius: "8px",
                  padding: "1rem",
                  marginBottom: "0.75rem",
                }}
              >
                <p style={{ margin: 0, fontStyle: "italic" }}>
                  &ldquo;{promoterStatement}&rdquo;
                </p>
                {promoterUpdatedAt && (
                  <p style={{ margin: "0.5rem 0 0", fontSize: "0.75rem", color: "#999999" }}>
                    Last updated: {new Date(promoterUpdatedAt).toLocaleString("en-NZ")}
                  </p>
                )}
              </div>
            ) : (
              <div
                style={{
                  background: "#FFF3EC",
                  border: "1px solid #F26522",
                  borderRadius: "8px",
                  padding: "1rem",
                  marginBottom: "0.75rem",
                }}
              >
                <p style={{ margin: 0, color: "#D4551A" }}>
                  No promoter statement set. You must set one before using promoter features.
                </p>
              </div>
            )}
            <button
              className="btn btn-primary"
              onClick={() => {
                setStatementDraft(promoterStatement);
                setEditingStatement(true);
              }}
            >
              {promoterStatement ? "Edit Statement" : "Set Statement"}
            </button>
          </>
        ) : (
          <>
            <div className="form-group">
              <label className="label">Promoter Statement Text</label>
              <textarea
                className="input"
                rows={3}
                value={statementDraft}
                onChange={(e) => setStatementDraft(e.target.value)}
                placeholder="e.g. Authorised by J. Smith, 123 Main Street, Wellington"
                maxLength={500}
                style={{ resize: "vertical" }}
              />
              <p style={{ fontSize: "0.75rem", color: "#999999", margin: "0.25rem 0 0" }}>
                {statementDraft.length}/500 characters
              </p>
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                className="btn btn-primary"
                onClick={handleSaveStatement}
                disabled={savingStatement || statementDraft.length < 5}
              >
                {savingStatement ? "Saving..." : "Save"}
              </button>
              <button
                className="btn"
                style={{ background: "#D8D8D8" }}
                onClick={() => setEditingStatement(false)}
              >
                Cancel
              </button>
            </div>
          </>
        )}

        {/* Default Position */}
        <div style={{ marginTop: "1.25rem", paddingTop: "1.25rem", borderTop: "1px solid #D8D8D8" }}>
          <label className="label">Default Statement Position</label>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
            <select
              className="input"
              style={{ width: "auto", minWidth: "160px" }}
              value={defaultPosition}
              onChange={(e) => setDefaultPosition(e.target.value)}
            >
              {POSITIONS.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
            <button
              className="btn btn-primary"
              style={{ padding: "0.75rem 1rem" }}
              onClick={handleSaveDefaultPosition}
              disabled={savingPosition}
            >
              {savingPosition ? "Saving..." : "Save Default"}
            </button>
          </div>
        </div>
      </div>

      {/* Upload Form - Enhanced with promoter options */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0 }}>Register a Campaign Image</h3>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label className="label">Image File</label>
            <input
              className="input"
              type="file"
              name="file"
              accept="image/jpeg,image/png,image/webp,image/svg+xml,application/pdf"
              required
            />
          </div>

          {/* Promoter options */}
          <div
            style={{
              background: "#F5F5F5",
              borderRadius: "8px",
              padding: "1rem",
              marginBottom: "1.25rem",
            }}
          >
            <p style={{ margin: "0 0 0.75rem", fontWeight: 500, fontSize: "0.875rem" }}>
              Promoter Statement Options
            </p>

            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={checkPromoter}
                onChange={(e) => setCheckPromoter(e.target.checked)}
              />
              <span style={{ fontSize: "0.875rem" }}>
                Check image for existing promoter statement (OCR)
              </span>
            </label>

            <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={addPromoter}
                onChange={(e) => setAddPromoter(e.target.checked)}
                disabled={!promoterStatement}
              />
              <span style={{ fontSize: "0.875rem", color: promoterStatement ? "#333333" : "#999999" }}>
                Add promoter statement to image
                {!promoterStatement && " (set statement first)"}
              </span>
            </label>

            {addPromoter && (
              <div style={{ marginLeft: "1.5rem", marginTop: "0.5rem" }}>
                <label className="label" style={{ fontSize: "0.875rem" }}>Position</label>
                <select
                  className="input"
                  style={{ width: "auto", minWidth: "160px" }}
                  value={uploadPosition}
                  onChange={(e) => setUploadPosition(e.target.value)}
                >
                  {POSITIONS.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={uploading}
          >
            {uploading ? "Uploading & Processing..." : "Register Image"}
          </button>
        </form>

        {/* Upload result */}
        {uploadResult && (
          <div className="result-verified" style={{ marginTop: "1rem" }}>
            <h4 style={{ margin: "0 0 0.5rem" }}>Image Registered</h4>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <tbody>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500, width: "140px" }}>Verification ID</td>
                  <td style={{ fontFamily: "monospace" }}>{uploadResult.verification_id}</td>
                </tr>
                <tr>
                  <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>Verification URL</td>
                  <td>
                    <a href={uploadResult.verification_url} style={{ color: "#F26522" }}>
                      {uploadResult.verification_url}
                    </a>
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
                {uploadResult.promoter_image_url && (
                  <tr>
                    <td style={{ padding: "0.25rem 0", fontWeight: 500 }}>Promoter Image</td>
                    <td>
                      <a href={uploadResult.promoter_image_url} style={{ color: "#F26522" }}>
                        Download stamped version
                      </a>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* OCR check result */}
            {uploadResult.promoter_check && (
              <div
                style={{
                  marginTop: "0.75rem",
                  padding: "0.75rem",
                  borderRadius: "8px",
                  background: uploadResult.promoter_check.found ? "#E8F5E9" : "#FFF3E0",
                  border: `1px solid ${uploadResult.promoter_check.found ? "#28A745" : "#F26522"}`,
                }}
              >
                <p style={{ margin: 0, fontWeight: 500, fontSize: "0.875rem" }}>
                  Promoter Statement OCR Check
                </p>
                <p style={{ margin: "0.25rem 0 0", fontSize: "0.875rem" }}>
                  {uploadResult.promoter_check.found ? (
                    <>Statement found with {(uploadResult.promoter_check.match_ratio * 100).toFixed(0)}% match</>
                  ) : (
                    <>Statement not detected in image (best match: {(uploadResult.promoter_check.match_ratio * 100).toFixed(0)}%)</>
                  )}
                </p>
                {uploadResult.promoter_check.best_match && (
                  <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem", color: "#666666" }}>
                    Closest match: &ldquo;{uploadResult.promoter_check.best_match}&rdquo;
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Batch Mode */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <h3 style={{ marginTop: 0 }}>Batch: Add Promoter Statement</h3>
        <p style={{ color: "#666666", fontSize: "0.875rem", marginTop: 0 }}>
          Upload an image to add your promoter statement and download the result directly.
          This does not register the image as a verified asset.
        </p>

        {!promoterStatement ? (
          <p style={{ color: "#D4551A", fontSize: "0.875rem" }}>
            Set your promoter statement above before using batch mode.
          </p>
        ) : (
          <>
            <div className="form-group">
              <label className="label">Image File</label>
              <input
                className="input"
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(e) => setBatchFile(e.target.files?.[0] || null)}
              />
            </div>
            <div className="form-group">
              <label className="label">Position</label>
              <select
                className="input"
                style={{ width: "auto", minWidth: "160px" }}
                value={batchPosition}
                onChange={(e) => setBatchPosition(e.target.value)}
              >
                {POSITIONS.map((p) => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </div>
            <button
              className="btn btn-primary"
              disabled={!batchFile || batchProcessing}
              onClick={handleBatchDownload}
            >
              {batchProcessing ? "Processing..." : "Add Statement & Download"}
            </button>
          </>
        )}
      </div>

      {/* Asset List */}
      <div className="card">
        <h3 style={{ marginTop: 0 }}>
          Registered Assets ({assets.length})
        </h3>
        {assets.length === 0 ? (
          <p style={{ color: "#666666" }}>No images registered yet.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                fontSize: "0.875rem",
              }}
            >
              <thead>
                <tr style={{ borderBottom: "2px solid #D8D8D8" }}>
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
                    style={{ borderBottom: "1px solid #D8D8D8" }}
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
                            asset.status === "active" ? "#E8F5E9" : "#FFEBEE",
                          color:
                            asset.status === "active" ? "#1B5E20" : "#B71C1C",
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
          </div>
        )}
      </div>
    </div>
  );
}
