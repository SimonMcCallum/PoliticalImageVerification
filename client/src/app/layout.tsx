import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Political Image Verification (PIVS)",
  description:
    "Check political campaign images for the New Zealand 2026 General Election against parties' own register.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">Skip to main content</a>

        <header className="site-header" role="banner">
          <div className="site-header__inner">
            <Link href="/" className="site-header__brand" aria-label="PIVS home">
              <span className="site-header__logo" aria-hidden>
                PIVS
              </span>
              <span className="site-header__brand-text">
                <span className="site-header__brand-en">
                  Political Image Verification
                </span>
                <span className="site-header__brand-mi">
                  Whakamana whakaahua tōrangapū
                </span>
              </span>
            </Link>

            <nav className="site-nav" aria-label="Primary">
              <Link href="/" className="site-nav__link">
                Verify
              </Link>
              <Link href="/party/promoter-preview" className="site-nav__link">
                Promoter preview
              </Link>
              <Link href="/ec" className="site-nav__link">
                Commission
              </Link>
              <Link href="/party" className="site-nav__cta">
                Party portal login
              </Link>
            </nav>
          </div>
        </header>

        <main id="main">{children}</main>

        <footer className="site-footer" role="contentinfo">
          <div className="site-footer__inner">
            <div className="site-footer__col">
              <h4>About</h4>
              <ul>
                <li><Link href="/">Verify an image</Link></li>
                <li><Link href="/party/promoter-preview">Promoter statement preview</Link></li>
                <li><Link href="/ec">Electoral Commission dashboard</Link></li>
              </ul>
            </div>
            <div className="site-footer__col">
              <h4>Resources</h4>
              <ul>
                <li>
                  <a href="https://elections.nz" rel="noopener noreferrer" target="_blank">
                    elections.nz
                  </a>
                </li>
                <li>
                  <a href="https://vote.nz" rel="noopener noreferrer" target="_blank">
                    vote.nz
                  </a>
                </li>
                <li>
                  <a
                    href="https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM307519.html"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    Electoral Act 1993
                  </a>
                </li>
              </ul>
            </div>
            <div className="site-footer__col">
              <h4>Privacy</h4>
              <ul>
                <li>Image bytes never stored. Hashes only.</li>
                <li>No personal information required to verify.</li>
                <li>Open source. Independent inspection welcome.</li>
              </ul>
            </div>
            <div className="site-footer__col">
              <h4>Contact</h4>
              <ul>
                <li>Electoral Commission</li>
                <li className="site-footer__contact">0800 36 76 56</li>
                <li>
                  <a href="mailto:enquiries@elections.govt.nz">
                    enquiries@elections.govt.nz
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <div className="site-footer__bottom">
            <span>
              PIVS &middot; New Zealand 2026 General Election &middot; open
              source
            </span>
            <span>v0.2.0 &middot; Build 2026-04-30</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
