import ImageVerifier from "@/components/ImageVerifier";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero__inner">
          <p className="hero__eyebrow">2026 General Election</p>
          <h1 className="hero__title">
            Verify a political campaign image
            <span className="hero__title-mi">
              Whakamana he whakaahua tōrangapū
            </span>
          </h1>
          <p className="hero__lead">
            Upload an image you have seen in a political advertisement to
            check whether it has been registered by a New Zealand political
            party. Verification is anonymous and the image you upload is
            never stored.
          </p>
        </div>
      </section>

      <div className="container container--narrow stack">
        <section className="card card--feature" aria-labelledby="verify-h">
          <h2 id="verify-h" style={{ marginTop: 0 }}>
            Check an image
          </h2>
          <ImageVerifier />
        </section>

        <section className="card" aria-labelledby="how-h">
          <h2 id="how-h" style={{ marginTop: 0 }}>How it works</h2>
          <ol style={{ color: "var(--ec-text-muted)", lineHeight: 1.7, paddingLeft: "1.2rem" }}>
            <li>
              Political parties register their official campaign images
              through the Party Portal.
            </li>
            <li>
              The system computes cryptographic and perceptual hashes of
              each image. Image bytes are encrypted at rest.
            </li>
            <li>
              When you upload an image here, the same hashes are computed
              and compared against the register.
            </li>
            <li>
              Common modifications (resize, recompression, the verification
              badge being added) still match because the perceptual hash
              tolerates them.
            </li>
          </ol>
          <p style={{ color: "var(--ec-text-muted)", fontSize: "0.9rem", margin: 0 }}>
            "Registered by a party" is a statement about provenance, not
            about whether an image is accurate, fair, or appropriate. Those
            judgements remain with parties, voters, and the Advertising
            Standards Authority.
          </p>
        </section>

        <section className="card" aria-labelledby="ext-h">
          <h2 id="ext-h" style={{ marginTop: 0 }}>
            Browser extension (beta)
          </h2>
          <p style={{ color: "var(--ec-text-muted)" }}>
            A companion browser extension checks images automatically while
            you browse and shows a small badge on registered campaign
            images. A transparency mode lets you see exactly what the
            extension is doing on your device.
          </p>
          <p style={{ margin: 0 }}>
            <a href="https://github.com/" rel="noopener noreferrer">
              Read the install guide
            </a>
            .
          </p>
        </section>
      </div>
    </>
  );
}
