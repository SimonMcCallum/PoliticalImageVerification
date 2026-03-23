"use client";

import "../globals.css";
import { useState, FormEvent } from "react";

const API_BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";

interface PartyInfo {
  id: string;
  name: string;
  short_name: string;
  status: string;
  has_promoter_statement: boolean;
  asset_count: number;
  active_count: number;
  revoked_count: number;
}

interface VerificationStats {
  period_days: number;
  total_verifications: number;
  verified_count: number;
  unverified_count: number;
  verification_rate: number;
  daily_trend: { date: string; total: number }[];
}

interface GeoStat {
  region: string;
  country: string;
  count: number;
}

interface ECImage {
  id: string;
  party_name: string;
  party_short_name: string;
  verification_id: string;
  mime_type: string;
  file_size: number;
  status: string;
  created_at: string;
  thumbnail_url: string | null;
}

interface ECUser {
  id: string;
  username: string;
  email: string;
  role: string;
  party_name: string;
  is_active: boolean;
  mfa_enabled: boolean;
  email_verified: boolean;
  last_login: string | null;
  created_at: string;
}

export default function ECDashboard() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);

  const [parties, setParties] = useState<PartyInfo[]>([]);
  const [stats, setStats] = useState<VerificationStats | null>(null);
  const [geoData, setGeoData] = useState<GeoStat[]>([]);
  const [images, setImages] = useState<ECImage[]>([]);
  const [users, setUsers] = useState<ECUser[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "stats" | "geo" | "images" | "users">("overview");
  const [loading, setLoading] = useState(false);

  // User management state
  const [editingEmail, setEditingEmail] = useState<string | null>(null);
  const [emailDraft, setEmailDraft] = useState("");
  const [resetConfirm, setResetConfirm] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Independent candidate creation
  const [showCreateIndependent, setShowCreateIndependent] = useState(false);
  const [indForm, setIndForm] = useState({ username: "", email: "", password: "", promoter_statement: "" });
  const [creatingIndependent, setCreatingIndependent] = useState(false);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setLoginError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, mfa_code: mfaCode || null }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }
      const data = await res.json();
      setToken(data.access_token);
      await loadAllData(data.access_token);
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    }
  }

  async function loadAllData(accessToken: string) {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${accessToken}` };
      const [partiesRes, statsRes, geoRes, imagesRes, usersRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/ec/parties`, { headers }),
        fetch(`${API_BASE}/api/v1/ec/stats?days=30`, { headers }),
        fetch(`${API_BASE}/api/v1/ec/geo?days=30`, { headers }),
        fetch(`${API_BASE}/api/v1/ec/images?per_page=50`, { headers }),
        fetch(`${API_BASE}/api/v1/ec/users`, { headers }),
      ]);

      if (partiesRes.ok) setParties(await partiesRes.json());
      if (statsRes.ok) setStats(await statsRes.json());
      if (geoRes.ok) setGeoData(await geoRes.json());
      if (imagesRes.ok) setImages(await imagesRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
    } catch {
      // Non-fatal
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="container">
        <h2 style={{ textAlign: "center" }}>Electoral Commission Dashboard</h2>
        <p style={{ textAlign: "center", color: "#666666" }}>
          Log in with your Electoral Commission account to view party usage and verification data.
        </p>
        <div className="card" style={{ maxWidth: "400px", margin: "0 auto" }}>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label className="label">Username</label>
              <input className="input" type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="label">Password</label>
              <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <div className="form-group">
              <label className="label">MFA Code (if enabled)</label>
              <input className="input" type="text" value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} placeholder="Optional" />
            </div>
            {loginError && <p style={{ color: "#DC3545", margin: "0 0 1rem" }}>{loginError}</p>}
            <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>Log In</button>
          </form>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <h2>Loading dashboard data...</h2>
      </div>
    );
  }

  const totalImages = parties.reduce((sum, p) => sum + p.asset_count, 0);

  return (
    <div className="container" style={{ maxWidth: "1000px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>Electoral Commission Dashboard</h2>
        <button className="btn" style={{ background: "#D8D8D8" }} onClick={() => { setToken(null); }}>Log Out</button>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", borderBottom: "2px solid #D8D8D8", paddingBottom: "0.5rem" }}>
        {(["overview", "users", "stats", "geo", "images"] as const).map((tab) => (
          <button
            key={tab}
            className="btn"
            style={{
              background: activeTab === tab ? "#F26522" : "#F5F5F5",
              color: activeTab === tab ? "white" : "#333",
              border: "none",
              padding: "0.5rem 1rem",
              borderRadius: "4px",
              cursor: "pointer",
              textTransform: "capitalize",
            }}
            onClick={() => { setActiveTab(tab); setActionMessage(null); }}
          >
            {tab === "geo" ? "Geographic Data" : tab === "stats" ? "Verification Stats" : tab === "images" ? "Image Browser" : tab === "users" ? "Users" : "Party Overview"}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <>
          {/* Summary Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
            <div className="card" style={{ textAlign: "center" }}>
              <p style={{ margin: 0, fontSize: "2rem", fontWeight: 700, color: "#F26522" }}>{parties.length}</p>
              <p style={{ margin: 0, color: "#666" }}>Registered Parties</p>
            </div>
            <div className="card" style={{ textAlign: "center" }}>
              <p style={{ margin: 0, fontSize: "2rem", fontWeight: 700, color: "#F26522" }}>{totalImages}</p>
              <p style={{ margin: 0, color: "#666" }}>Total Images</p>
            </div>
            <div className="card" style={{ textAlign: "center" }}>
              <p style={{ margin: 0, fontSize: "2rem", fontWeight: 700, color: "#F26522" }}>{stats?.total_verifications || 0}</p>
              <p style={{ margin: 0, color: "#666" }}>Verifications (30d)</p>
            </div>
          </div>

          {/* Parties Table */}
          <div className="card">
            <h3 style={{ marginTop: 0 }}>Parties</h3>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #D8D8D8" }}>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Party</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Status</th>
                    <th style={{ textAlign: "center", padding: "0.5rem" }}>Promoter</th>
                    <th style={{ textAlign: "right", padding: "0.5rem" }}>Active</th>
                    <th style={{ textAlign: "right", padding: "0.5rem" }}>Revoked</th>
                    <th style={{ textAlign: "right", padding: "0.5rem" }}>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {parties.map((p) => (
                    <tr key={p.id} style={{ borderBottom: "1px solid #D8D8D8" }}>
                      <td style={{ padding: "0.5rem" }}>
                        <strong>{p.short_name}</strong>
                        <br />
                        <span style={{ fontSize: "0.75rem", color: "#666" }}>{p.name}</span>
                      </td>
                      <td style={{ padding: "0.5rem" }}>
                        <span style={{
                          background: p.status === "active" ? "#E8F5E9" : "#FFEBEE",
                          color: p.status === "active" ? "#1B5E20" : "#B71C1C",
                          padding: "0.125rem 0.5rem", borderRadius: "4px", fontSize: "0.75rem",
                        }}>{p.status}</span>
                      </td>
                      <td style={{ textAlign: "center", padding: "0.5rem" }}>
                        {p.has_promoter_statement ? (
                          <span style={{ color: "#28A745" }}>&#x2713;</span>
                        ) : (
                          <span style={{ color: "#DC3545" }}>&#x2717;</span>
                        )}
                      </td>
                      <td style={{ textAlign: "right", padding: "0.5rem" }}>{p.active_count}</td>
                      <td style={{ textAlign: "right", padding: "0.5rem" }}>{p.revoked_count}</td>
                      <td style={{ textAlign: "right", padding: "0.5rem", fontWeight: 600 }}>{p.asset_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Users Tab */}
      {activeTab === "users" && (
        <div className="card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h3 style={{ marginTop: 0 }}>User Management</h3>
            <button
              className="btn btn-primary"
              style={{ fontSize: "0.875rem" }}
              onClick={() => { setShowCreateIndependent(!showCreateIndependent); setActionMessage(null); }}
            >
              {showCreateIndependent ? "Cancel" : "Create Independent Candidate"}
            </button>
          </div>

          {showCreateIndependent && (
            <div style={{
              background: "#E3F2FD",
              borderRadius: "8px",
              padding: "1rem",
              marginBottom: "1rem",
              border: "1px solid #1565C0",
            }}>
              <p style={{ margin: "0 0 0.75rem", fontWeight: 500, fontSize: "0.875rem", color: "#1565C0" }}>
                Create Independent Candidate
              </p>
              <p style={{ margin: "0 0 0.75rem", fontSize: "0.75rem", color: "#666" }}>
                This creates a candidate account in the &quot;Independent Candidates&quot; party.
                They must have their own promoter statement.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="label" style={{ fontSize: "0.75rem" }}>Username</label>
                  <input
                    className="input"
                    type="text"
                    value={indForm.username}
                    onChange={(e) => setIndForm({ ...indForm, username: e.target.value })}
                    placeholder="username"
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="label" style={{ fontSize: "0.75rem" }}>Email</label>
                  <input
                    className="input"
                    type="email"
                    value={indForm.email}
                    onChange={(e) => setIndForm({ ...indForm, email: e.target.value })}
                    placeholder="email@example.com"
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="label" style={{ fontSize: "0.75rem" }}>Password</label>
                  <input
                    className="input"
                    type="password"
                    value={indForm.password}
                    onChange={(e) => setIndForm({ ...indForm, password: e.target.value })}
                    placeholder="Min 8 characters"
                  />
                </div>
                <div className="form-group" style={{ margin: 0 }}>
                  <label className="label" style={{ fontSize: "0.75rem" }}>Promoter Statement (required)</label>
                  <input
                    className="input"
                    type="text"
                    value={indForm.promoter_statement}
                    onChange={(e) => setIndForm({ ...indForm, promoter_statement: e.target.value })}
                    placeholder="Authorised by..."
                  />
                </div>
              </div>
              <button
                className="btn btn-primary"
                style={{ marginTop: "0.75rem" }}
                disabled={
                  creatingIndependent ||
                  !indForm.username ||
                  !indForm.email ||
                  indForm.password.length < 8 ||
                  indForm.promoter_statement.length < 5
                }
                onClick={async () => {
                  setCreatingIndependent(true);
                  setActionMessage(null);
                  try {
                    const res = await fetch(`${API_BASE}/api/v1/ec/candidates`, {
                      method: "POST",
                      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
                      body: JSON.stringify(indForm),
                    });
                    if (!res.ok) {
                      const data = await res.json();
                      throw new Error(data.detail || "Failed");
                    }
                    setIndForm({ username: "", email: "", password: "", promoter_statement: "" });
                    setShowCreateIndependent(false);
                    setActionMessage({ type: "success", text: "Independent candidate created" });
                    // Reload users
                    const usersRes = await fetch(`${API_BASE}/api/v1/ec/users`, {
                      headers: { Authorization: `Bearer ${token}` },
                    });
                    if (usersRes.ok) setUsers(await usersRes.json());
                  } catch (err) {
                    setActionMessage({ type: "error", text: err instanceof Error ? err.message : "Failed" });
                  } finally {
                    setCreatingIndependent(false);
                  }
                }}
              >
                {creatingIndependent ? "Creating..." : "Create Independent Candidate"}
              </button>
            </div>
          )}
          {actionMessage && (
            <div
              style={{
                padding: "0.75rem",
                borderRadius: "8px",
                marginBottom: "1rem",
                background: actionMessage.type === "success" ? "#E8F5E9" : "#FFEBEE",
                border: `1px solid ${actionMessage.type === "success" ? "#28A745" : "#DC3545"}`,
                color: actionMessage.type === "success" ? "#1B5E20" : "#B71C1C",
              }}
            >
              {actionMessage.text}
            </div>
          )}
          {users.length === 0 ? (
            <p style={{ color: "#999" }}>No users found.</p>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid #D8D8D8" }}>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Username</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Email</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Party</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Role</th>
                    <th style={{ textAlign: "center", padding: "0.5rem" }}>Active</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Last Login</th>
                    <th style={{ textAlign: "left", padding: "0.5rem" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} style={{ borderBottom: "1px solid #D8D8D8" }}>
                      <td style={{ padding: "0.5rem", fontWeight: 500 }}>{u.username}</td>
                      <td style={{ padding: "0.5rem" }}>
                        {editingEmail === u.id ? (
                          <div style={{ display: "flex", gap: "0.25rem", alignItems: "center" }}>
                            <input
                              className="input"
                              type="email"
                              value={emailDraft}
                              onChange={(e) => setEmailDraft(e.target.value)}
                              style={{ padding: "0.25rem 0.5rem", fontSize: "0.875rem", width: "200px" }}
                            />
                            <button
                              className="btn btn-primary"
                              style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem" }}
                              onClick={async () => {
                                try {
                                  const res = await fetch(`${API_BASE}/api/v1/ec/users/${u.id}/email`, {
                                    method: "PATCH",
                                    headers: {
                                      Authorization: `Bearer ${token}`,
                                      "Content-Type": "application/json",
                                    },
                                    body: JSON.stringify({ email: emailDraft }),
                                  });
                                  if (!res.ok) {
                                    const data = await res.json();
                                    throw new Error(data.detail || "Failed");
                                  }
                                  setUsers(users.map((x) =>
                                    x.id === u.id ? { ...x, email: emailDraft, email_verified: false } : x
                                  ));
                                  setEditingEmail(null);
                                  setActionMessage({ type: "success", text: `Email updated for ${u.username}` });
                                } catch (err) {
                                  setActionMessage({ type: "error", text: err instanceof Error ? err.message : "Failed" });
                                }
                              }}
                            >
                              Save
                            </button>
                            <button
                              className="btn"
                              style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "#D8D8D8" }}
                              onClick={() => setEditingEmail(null)}
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <span style={{ fontSize: "0.875rem" }}>{u.email}</span>
                        )}
                      </td>
                      <td style={{ padding: "0.5rem", fontSize: "0.75rem" }}>{u.party_name}</td>
                      <td style={{ padding: "0.5rem" }}>
                        <span style={{
                          fontSize: "0.75rem",
                          background: u.role === "electoral_commission" ? "#E3F2FD" : "#F5F5F5",
                          color: u.role === "electoral_commission" ? "#1565C0" : "#333",
                          padding: "0.125rem 0.5rem",
                          borderRadius: "4px",
                        }}>
                          {u.role.replace(/_/g, " ")}
                        </span>
                      </td>
                      <td style={{ textAlign: "center", padding: "0.5rem" }}>
                        {u.is_active ? (
                          <span style={{ color: "#28A745" }}>&#x2713;</span>
                        ) : (
                          <span style={{ color: "#DC3545" }}>&#x2717;</span>
                        )}
                      </td>
                      <td style={{ padding: "0.5rem", fontSize: "0.75rem", color: "#666" }}>
                        {u.last_login ? new Date(u.last_login).toLocaleString("en-NZ") : "Never"}
                      </td>
                      <td style={{ padding: "0.5rem" }}>
                        {u.role !== "electoral_commission" && (
                          <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                            <button
                              className="btn"
                              style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "#F5F5F5" }}
                              onClick={() => {
                                setEditingEmail(u.id);
                                setEmailDraft(u.email);
                                setActionMessage(null);
                              }}
                            >
                              Edit Email
                            </button>
                            {resetConfirm === u.id ? (
                              <div style={{ display: "flex", gap: "0.25rem" }}>
                                <button
                                  className="btn"
                                  style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "#DC3545", color: "white" }}
                                  onClick={async () => {
                                    try {
                                      const res = await fetch(`${API_BASE}/api/v1/ec/users/${u.id}/reset-password`, {
                                        method: "POST",
                                        headers: { Authorization: `Bearer ${token}` },
                                      });
                                      if (!res.ok) {
                                        const data = await res.json();
                                        throw new Error(data.detail || "Failed");
                                      }
                                      const data = await res.json();
                                      setActionMessage({ type: "success", text: data.detail || `Password reset triggered for ${u.username}` });
                                    } catch (err) {
                                      setActionMessage({ type: "error", text: err instanceof Error ? err.message : "Failed" });
                                    }
                                    setResetConfirm(null);
                                  }}
                                >
                                  Confirm Reset
                                </button>
                                <button
                                  className="btn"
                                  style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "#D8D8D8" }}
                                  onClick={() => setResetConfirm(null)}
                                >
                                  Cancel
                                </button>
                              </div>
                            ) : (
                              <button
                                className="btn"
                                style={{ padding: "0.25rem 0.5rem", fontSize: "0.75rem", background: "#FFF3EC", color: "#D4551A" }}
                                onClick={() => { setResetConfirm(u.id); setActionMessage(null); }}
                              >
                                Reset Password
                              </button>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Stats Tab */}
      {activeTab === "stats" && stats && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Verification Statistics (Last {stats.period_days} days)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "1.5rem" }}>
            <div style={{ textAlign: "center", padding: "1rem", background: "#F5F5F5", borderRadius: "8px" }}>
              <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700 }}>{stats.total_verifications}</p>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#666" }}>Total</p>
            </div>
            <div style={{ textAlign: "center", padding: "1rem", background: "#E8F5E9", borderRadius: "8px" }}>
              <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#28A745" }}>{stats.verified_count}</p>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#666" }}>Verified</p>
            </div>
            <div style={{ textAlign: "center", padding: "1rem", background: "#FFEBEE", borderRadius: "8px" }}>
              <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#DC3545" }}>{stats.unverified_count}</p>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#666" }}>Unverified</p>
            </div>
            <div style={{ textAlign: "center", padding: "1rem", background: "#FFF3EC", borderRadius: "8px" }}>
              <p style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, color: "#F26522" }}>{stats.verification_rate}%</p>
              <p style={{ margin: 0, fontSize: "0.75rem", color: "#666" }}>Success Rate</p>
            </div>
          </div>

          {stats.daily_trend.length > 0 && (
            <>
              <h4>Daily Trend</h4>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #D8D8D8" }}>
                      <th style={{ textAlign: "left", padding: "0.5rem" }}>Date</th>
                      <th style={{ textAlign: "right", padding: "0.5rem" }}>Verifications</th>
                      <th style={{ textAlign: "left", padding: "0.5rem", width: "50%" }}>Bar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.daily_trend.map((d) => {
                      const maxCount = Math.max(...stats.daily_trend.map((x) => x.total));
                      const pct = maxCount > 0 ? (d.total / maxCount) * 100 : 0;
                      return (
                        <tr key={d.date} style={{ borderBottom: "1px solid #D8D8D8" }}>
                          <td style={{ padding: "0.5rem" }}>{d.date}</td>
                          <td style={{ textAlign: "right", padding: "0.5rem" }}>{d.total}</td>
                          <td style={{ padding: "0.5rem" }}>
                            <div style={{
                              width: `${pct}%`, minWidth: d.total > 0 ? "4px" : "0",
                              height: "16px", background: "#F26522", borderRadius: "2px",
                            }} />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* Geo Tab */}
      {activeTab === "geo" && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Geographic Verification Data</h3>
          <p style={{ color: "#666", fontSize: "0.875rem", marginTop: 0 }}>
            Aggregate verification counts by region. Individual IP addresses are never stored.
          </p>
          {geoData.length === 0 ? (
            <p style={{ color: "#999" }}>No geographic data available yet.</p>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <thead>
                <tr style={{ borderBottom: "2px solid #D8D8D8" }}>
                  <th style={{ textAlign: "left", padding: "0.5rem" }}>Region</th>
                  <th style={{ textAlign: "left", padding: "0.5rem" }}>Country</th>
                  <th style={{ textAlign: "right", padding: "0.5rem" }}>Verifications</th>
                </tr>
              </thead>
              <tbody>
                {geoData.map((g, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid #D8D8D8" }}>
                    <td style={{ padding: "0.5rem" }}>{g.region}</td>
                    <td style={{ padding: "0.5rem" }}>{g.country}</td>
                    <td style={{ textAlign: "right", padding: "0.5rem", fontWeight: 600 }}>{g.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* Images Tab */}
      {activeTab === "images" && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Registered Images (All Parties)</h3>
          {images.length === 0 ? (
            <p style={{ color: "#999" }}>No images registered yet.</p>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "1rem" }}>
              {images.map((img) => (
                <div key={img.id} style={{
                  border: "1px solid #D8D8D8", borderRadius: "8px", overflow: "hidden",
                  background: "white",
                }}>
                  <div style={{
                    width: "100%", height: "120px", background: "#F5F5F5",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    {img.thumbnail_url ? (
                      <img
                        src={`${API_BASE}${img.thumbnail_url}`}
                        alt={img.verification_id}
                        style={{ maxWidth: "100%", maxHeight: "120px", objectFit: "cover" }}
                      />
                    ) : (
                      <span style={{ color: "#999", fontSize: "0.75rem" }}>No thumbnail</span>
                    )}
                  </div>
                  <div style={{ padding: "0.5rem" }}>
                    <p style={{ margin: 0, fontSize: "0.75rem", fontWeight: 600 }}>{img.party_short_name}</p>
                    <p style={{ margin: 0, fontSize: "0.625rem", fontFamily: "monospace", color: "#666" }}>
                      {img.verification_id}
                    </p>
                    <p style={{ margin: 0, fontSize: "0.625rem", color: "#999" }}>
                      {new Date(img.created_at).toLocaleDateString("en-NZ")}
                    </p>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.25rem", marginTop: "0.25rem" }}>
                      <span style={{
                        fontSize: "0.625rem",
                        background: img.status === "active" ? "#E8F5E9" : "#FFEBEE",
                        color: img.status === "active" ? "#1B5E20" : "#B71C1C",
                        padding: "0.0625rem 0.25rem", borderRadius: "2px",
                      }}>{img.status}</span>
                    </div>
                    <div style={{ display: "flex", gap: "0.25rem", marginTop: "0.375rem", flexWrap: "wrap" }}>
                      <button
                        className="btn"
                        style={{ padding: "0.125rem 0.375rem", fontSize: "0.5625rem", background: "#F5F5F5" }}
                        onClick={async () => {
                          const res = await fetch(`${API_BASE}/api/v1/ec/images/${img.id}/download/original`, {
                            headers: { Authorization: `Bearer ${token}` },
                          });
                          if (res.ok) {
                            const blob = await res.blob();
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url; a.download = `original_${img.verification_id}.png`;
                            document.body.appendChild(a); a.click(); document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          }
                        }}
                      >
                        Original
                      </button>
                      <button
                        className="btn"
                        style={{ padding: "0.125rem 0.375rem", fontSize: "0.5625rem", background: "#FFF3EC", color: "#D4551A" }}
                        onClick={async () => {
                          const res = await fetch(`${API_BASE}/api/v1/ec/images/${img.id}/download/promoter`, {
                            headers: { Authorization: `Bearer ${token}` },
                          });
                          if (res.ok) {
                            const blob = await res.blob();
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url; a.download = `promoter_${img.verification_id}.png`;
                            document.body.appendChild(a); a.click(); document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          } else {
                            alert("No promoter version available");
                          }
                        }}
                      >
                        Promoter
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
