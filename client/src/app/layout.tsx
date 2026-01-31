import type { Metadata } from "next";

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
            background: "#1a1a2e",
            color: "white",
            padding: "1rem 2rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <a href="/" style={{ color: "white", textDecoration: "none" }}>
            <h1 style={{ margin: 0, fontSize: "1.25rem" }}>
              NZ Political Image Verification
            </h1>
          </a>
          <nav style={{ display: "flex", gap: "1.5rem" }}>
            <a href="/" style={{ color: "#88c0d0", textDecoration: "none" }}>
              Verify
            </a>
            <a
              href="/party"
              style={{ color: "#88c0d0", textDecoration: "none" }}
            >
              Party Portal
            </a>
          </nav>
        </header>
        <main>{children}</main>
        <footer
          style={{
            background: "#16213e",
            color: "#8892b0",
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
        </footer>
      </body>
    </html>
  );
}
