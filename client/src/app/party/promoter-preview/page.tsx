"use client";

import "../../globals.css";
import { useState, useRef, useEffect, FormEvent } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const POSITIONS = [
  { value: "bottom-left", label: "Bottom Left" },
  { value: "bottom-right", label: "Bottom Right" },
  { value: "top-left", label: "Top Left" },
  { value: "top-right", label: "Top Right" },
];

export default function PromoterPreview() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);

  const [promoterStatement, setPromoterStatement] = useState("");
  const [partyId, setPartyId] = useState<string | null>(null);

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageDimensions, setImageDimensions] = useState<{ w: number; h: number } | null>(null);
  const [position, setPosition] = useState("bottom-left");
  const [processing, setProcessing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);

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
      if (data.party_id) setPartyId(data.party_id);
      if (data.default_statement_position) setPosition(data.default_statement_position);
      // Load promoter statement
      if (data.party_id) {
        const stRes = await fetch(`${API_BASE}/api/v1/parties/${data.party_id}/promoter-statement`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
        });
        if (stRes.ok) {
          const stData = await stRes.json();
          setPromoterStatement(stData.statement || "");
        }
      }
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed");
    }
  }

  function handleImageSelect(file: File | null) {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (!file) {
      setImageFile(null);
      setImageUrl(null);
      setImageDimensions(null);
      return;
    }
    setImageFile(file);
    const url = URL.createObjectURL(file);
    setImageUrl(url);

    const img = new Image();
    img.onload = () => {
      setImageDimensions({ w: img.naturalWidth, h: img.naturalHeight });
    };
    img.src = url;
  }

  // Client-side preview rendering on canvas
  useEffect(() => {
    if (!imageUrl || !imageDimensions || !promoterStatement || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      // Scale to fit canvas (max 700px wide)
      const maxW = 700;
      const scale = Math.min(1, maxW / img.naturalWidth);
      canvas.width = img.naturalWidth * scale;
      canvas.height = img.naturalHeight * scale;

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Draw promoter statement preview
      const fontSize = Math.max(12, Math.floor(canvas.height * 0.025));
      const padding = Math.max(6, Math.floor(fontSize / 2));
      const margin = Math.max(8, fontSize);

      ctx.font = `${fontSize}px system-ui, sans-serif`;

      // Wrap text
      const maxTextW = canvas.width < canvas.height
        ? canvas.width * 0.9 - padding * 2
        : canvas.width * 0.45 - padding * 2;

      const lines: string[] = [];
      const words = promoterStatement.split(" ");
      let currentLine = "";
      for (const word of words) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        if (ctx.measureText(testLine).width <= maxTextW) {
          currentLine = testLine;
        } else {
          if (currentLine) lines.push(currentLine);
          currentLine = word;
        }
      }
      if (currentLine) lines.push(currentLine);

      const lineHeight = fontSize + 4;
      const textBlockH = lines.length * lineHeight;
      let textBlockW = 0;
      for (const line of lines) {
        textBlockW = Math.max(textBlockW, ctx.measureText(line).width);
      }

      const boxW = textBlockW + padding * 2;
      const boxH = textBlockH + padding * 2;

      let boxX: number, boxY: number;
      if (position === "bottom-left") {
        boxX = margin;
        boxY = canvas.height - boxH - margin;
      } else if (position === "bottom-right") {
        boxX = canvas.width - boxW - margin;
        boxY = canvas.height - boxH - margin;
      } else if (position === "top-left") {
        boxX = margin;
        boxY = margin;
      } else {
        boxX = canvas.width - boxW - margin;
        boxY = margin;
      }

      // Clamp
      boxX = Math.max(0, Math.min(boxX, canvas.width - boxW));
      boxY = Math.max(0, Math.min(boxY, canvas.height - boxH));

      // Sample background colour
      const imgData = ctx.getImageData(boxX, boxY, Math.max(1, boxW), Math.max(1, boxH));
      let rSum = 0, gSum = 0, bSum = 0;
      const pixelCount = imgData.data.length / 4;
      for (let i = 0; i < imgData.data.length; i += 4) {
        rSum += imgData.data[i];
        gSum += imgData.data[i + 1];
        bSum += imgData.data[i + 2];
      }
      const avgR = rSum / pixelCount;
      const avgG = gSum / pixelCount;
      const avgB = bSum / pixelCount;

      // WCAG luminance
      function srgbToLinear(c: number) {
        const s = c / 255;
        return s <= 0.04045 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      }
      const lum = 0.2126 * srgbToLinear(avgR) + 0.7152 * srgbToLinear(avgG) + 0.0722 * srgbToLinear(avgB);

      const useWhite = lum < 0.5;
      const textColor = useWhite ? "rgba(255,255,255,1)" : "rgba(0,0,0,1)";
      const backingColor = useWhite ? "rgba(0,0,0,0.7)" : "rgba(255,255,255,0.7)";

      // Draw backing
      ctx.fillStyle = backingColor;
      ctx.fillRect(boxX, boxY, boxW, boxH);

      // Draw text
      ctx.fillStyle = textColor;
      ctx.font = `${fontSize}px system-ui, sans-serif`;
      ctx.textBaseline = "top";
      let yCursor = boxY + padding;
      for (const line of lines) {
        let textX: number;
        if (position.includes("right")) {
          textX = boxX + boxW - padding - ctx.measureText(line).width;
        } else {
          textX = boxX + padding;
        }
        ctx.fillText(line, textX, yCursor);
        yCursor += lineHeight;
      }
    };
    img.src = imageUrl;
  }, [imageUrl, imageDimensions, promoterStatement, position]);

  async function handleApplyAndDownload() {
    if (!token || !imageFile) return;
    setProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", imageFile);
      formData.append("position", position);

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
      setPreviewUrl(url);

      // Trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = "promoter_stamped.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Processing failed");
    } finally {
      setProcessing(false);
    }
  }

  if (!token) {
    return (
      <div className="container">
        <h2 style={{ textAlign: "center" }}>Promoter Statement Preview</h2>
        <p style={{ textAlign: "center", color: "#666666" }}>
          Log in to preview how your promoter statement will appear on images.
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

  const orientation = imageDimensions
    ? imageDimensions.h > imageDimensions.w ? "Portrait" : "Landscape"
    : null;

  return (
    <div className="container" style={{ maxWidth: "900px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h2 style={{ margin: 0 }}>Promoter Statement Preview</h2>
        <a href="/party" style={{ color: "#F26522", textDecoration: "none", fontSize: "0.875rem" }}>
          Back to Party Portal
        </a>
      </div>

      {!promoterStatement ? (
        <div className="card">
          <div style={{ background: "#FFF3EC", border: "1px solid #F26522", borderRadius: "8px", padding: "1rem" }}>
            <p style={{ margin: 0, color: "#D4551A" }}>
              No promoter statement set. Go to the <a href="/party" style={{ color: "#F26522" }}>Party Portal</a> to set one first.
            </p>
          </div>
        </div>
      ) : (
        <>
          {/* Controls */}
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ marginTop: 0 }}>Preview Settings</h3>
            <p style={{ color: "#666666", fontSize: "0.875rem", marginTop: 0 }}>
              Current statement: <em>&ldquo;{promoterStatement}&rdquo;</em>
            </p>

            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", alignItems: "flex-end" }}>
              <div className="form-group" style={{ marginBottom: 0, flex: "1 1 300px" }}>
                <label className="label">Upload Image</label>
                <input
                  className="input"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => handleImageSelect(e.target.files?.[0] || null)}
                />
              </div>
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label className="label">Position</label>
                <select
                  className="input"
                  style={{ width: "auto", minWidth: "160px" }}
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                >
                  {POSITIONS.map((p) => (
                    <option key={p.value} value={p.value}>{p.label}</option>
                  ))}
                </select>
              </div>
            </div>

            {imageDimensions && (
              <p style={{ fontSize: "0.75rem", color: "#999999", margin: "0.75rem 0 0" }}>
                {imageDimensions.w} x {imageDimensions.h}px &middot; {orientation}
              </p>
            )}
          </div>

          {/* Canvas Preview */}
          {imageUrl && (
            <div className="card" style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ marginTop: 0 }}>Preview</h3>
              <p style={{ color: "#666666", fontSize: "0.75rem", marginTop: 0 }}>
                This is a client-side approximation. The server-rendered version may differ slightly in font and sizing.
              </p>
              <div style={{ overflow: "auto", border: "1px solid #D8D8D8", borderRadius: "8px" }}>
                <canvas
                  ref={canvasRef}
                  style={{ display: "block", maxWidth: "100%", height: "auto" }}
                />
              </div>
              <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
                <button
                  className="btn btn-primary"
                  disabled={processing}
                  onClick={handleApplyAndDownload}
                >
                  {processing ? "Processing..." : "Apply & Download (server-rendered)"}
                </button>
              </div>
              {previewUrl && (
                <p style={{ fontSize: "0.875rem", color: "#28A745", marginTop: "0.5rem" }}>
                  Download started. The server-rendered image uses the exact same contrast
                  and positioning algorithm used during asset registration.
                </p>
              )}
            </div>
          )}

          {!imageUrl && (
            <div className="card">
              <div
                style={{
                  border: "2px dashed #D8D8D8",
                  borderRadius: "12px",
                  padding: "3rem 2rem",
                  textAlign: "center",
                  color: "#999999",
                }}
              >
                Upload an image above to see how your promoter statement will appear.
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
