"use client";

import "../globals.css";
import { useState, FormEvent, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_BASE_PATH || "";

export default function ResetPasswordPage() {
  const [token, setToken] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setToken(params.get("token"));
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("No reset token found. Please use the link from your email.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/auth/reset-password/confirm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: newPassword }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Reset failed");
      }

      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <h2>Reset Password</h2>
        <div className="card" style={{ maxWidth: "400px", margin: "0 auto" }}>
          <p style={{ color: "#DC3545" }}>
            No reset token found. Please use the link from your password reset email.
          </p>
        </div>
      </div>
    );
  }

  if (success) {
    return (
      <div className="container" style={{ textAlign: "center" }}>
        <h2>Password Reset</h2>
        <div className="card" style={{ maxWidth: "400px", margin: "0 auto" }}>
          <div
            style={{
              background: "#E8F5E9",
              border: "1px solid #28A745",
              borderRadius: "8px",
              padding: "1rem",
              marginBottom: "1rem",
            }}
          >
            <p style={{ margin: 0, color: "#1B5E20", fontWeight: 500 }}>
              Your password has been reset successfully.
            </p>
          </div>
          <a href="/party" className="btn btn-primary" style={{ display: "inline-block" }}>
            Go to Party Portal Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h2 style={{ textAlign: "center" }}>Reset Password</h2>
      <p style={{ textAlign: "center", color: "#666666" }}>
        Enter your new password below.
      </p>

      <div className="card" style={{ maxWidth: "400px", margin: "0 auto" }}>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="label">New Password</label>
            <input
              className="input"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              required
            />
            <p style={{ fontSize: "0.75rem", color: "#999", margin: "0.25rem 0 0" }}>
              Minimum 8 characters
            </p>
          </div>
          <div className="form-group">
            <label className="label">Confirm New Password</label>
            <input
              className="input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              minLength={8}
              required
            />
          </div>
          {error && (
            <p style={{ color: "#DC3545", margin: "0 0 1rem" }}>{error}</p>
          )}
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%" }}
            disabled={submitting}
          >
            {submitting ? "Resetting..." : "Reset Password"}
          </button>
        </form>
      </div>
    </div>
  );
}
