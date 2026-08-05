import Image from "next/image";
import Link from "next/link";

import ThemeToggle from "@/app/theme-toggle";
import { BRAND } from "@/lib/branding";

import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={`${styles.container} siteContainer`}>
        <Link
          href="/"
          className={styles.brand}
          aria-label={`${BRAND.name} homepage`}
        >
          <Image
            src="/upsc-anchor-logo.png"
            alt={`${BRAND.name} logo`}
            width={120}
            height={120}
            priority
            className={styles.logo}
          />

          <div className={styles.brandText}>
            <strong>{BRAND.shortName}</strong>
            <span>by {BRAND.author}</span>
          </div>
        </Link>

        <nav
          className={styles.navigation}
          aria-label="Main navigation"
        >
          <Link
            href="/"
            className={styles.active}
          >
            Home
          </Link>

          <Link href="/#todays-issues">
            Today&apos;s Issues
          </Link>

          <Link href="/issues">
            All Issues
          </Link>

          <Link href="/resources">
            Resources
          </Link>

          <Link href="/about">
            About
          </Link>
        </nav>

        <div className={styles.actions}>
          <ThemeToggle />

          <button
            type="button"
            className={styles.subscribe}
          >
            Subscribe
          </button>

          <button
            type="button"
            className={styles.login}
          >
            Login
          </button>
        </div>
      </div>
    </header>
  );
}