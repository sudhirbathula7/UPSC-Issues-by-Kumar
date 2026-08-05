import Link from "next/link";

import { BRAND } from "@/lib/branding";

import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={`${styles.container} siteContainer`}>
        <div className={styles.brand}>
          <h2>{BRAND.name}</h2>

          <p>{BRAND.description}</p>
        </div>

        <nav className={styles.links}>
          <Link href="/">Home</Link>

          <Link href="/issues">
            Archive
          </Link>

          <Link href="/about">
            About
          </Link>

          <Link href="/privacy">
            Privacy
          </Link>

          <Link href="/contact">
            Contact
          </Link>
        </nav>

        <div className={styles.bottom}>
          <span>{BRAND.copyright}</span>

          <span>
            {BRAND.taglineLineOne} • {BRAND.taglineLineTwo}
          </span>
        </div>
      </div>
    </footer>
  );
}