import "./globals.css";
import ImageVerifier from "@/components/ImageVerifier";

export default function Home() {
  return (
    <div className="container">
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <h2 style={{ marginBottom: "0.5rem" }}>
          Verify a Political Campaign Image
        </h2>
        <p style={{ color: "#666666", maxWidth: "600px", margin: "0 auto" }}>
          Upload an image you&apos;ve seen in a political advertisement to check
          if it has been officially registered by a New Zealand political party
          for the 2026 General Election.
        </p>
      </div>

      <div className="card">
        <ImageVerifier />
      </div>

      <div
        className="card"
        style={{ marginTop: "1.5rem" }}
      >
        <h3 style={{ marginTop: 0 }}>How it works</h3>
        <ol style={{ color: "#666666", lineHeight: 1.8 }}>
          <li>
            Political parties register their official campaign images through
            the Party Portal.
          </li>
          <li>
            The system creates cryptographic and perceptual hashes of each
            image.
          </li>
          <li>
            When you upload an image here, it is hashed and compared against all
            registered images.
          </li>
          <li>
            Even if the image has been resized, compressed, or has a
            verification badge added, the perceptual hash can still match the
            original.
          </li>
        </ol>
        <p style={{ color: "#666666", fontSize: "0.875rem" }}>
          Images you upload for verification are not stored. Only their hashes
          are computed in memory and compared.
        </p>
      </div>
    </div>
  );
}
