import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "NZ Political Image Verification",
  description:
    "Verify the authenticity of political campaign images for the NZ 2026 General Election",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, -apple-system, sans-serif" }}>
        <header
          style={{
            background: "#1B1B1B",
            color: "white",
            padding: "1rem 2rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Link href="/" style={{ color: "white", textDecoration: "none" }}>
            <h1 style={{ margin: 0, fontSize: "1.25rem" }}>
              NZ Political Image Verification
            </h1>
          </Link>
          <nav style={{ display: "flex", gap: "1.5rem" }}>
            <Link href="/" style={{ color: "#F26522", textDecoration: "none" }}>
              Verify
            </Link>
            <Link
              href="/party"
              style={{ color: "#F26522", textDecoration: "none" }}
            >
              Party Portal
            </Link>
            <Link
              href="/party/promoter-preview"
              style={{ color: "#F26522", textDecoration: "none" }}
            >
              Promoter Preview
            </Link>
            <Link
              href="/ec"
              style={{ color: "#F26522", textDecoration: "none" }}
            >
              EC Dashboard
            </Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer
          style={{
            background: "#2D2D2D",
            color: "#999999",
            padding: "1.5rem 2rem",
            textAlign: "center",
            fontSize: "0.875rem",
            marginTop: "2rem",
          }}
        >
          <p style={{ margin: 0 }}>
            NZ Political Image Verification System &mdash; 2026 General
            Election
          </p>
          <p style={{ margin: "0.25rem 0 0" }}>
            An open-source tool for verifying the authenticity of political
            campaign images.
          </p>
          <p style={{ margin: "0.5rem 0 0", fontSize: "0.75rem", color: "#666" }}>
            v0.2.0 &mdash; Build 2025-02-16a
          </p>
        </footer>
      </body>
    </html>
  );
}
