import Image from "next/image";

import { BRAND } from "@/lib/branding";

import styles from "./Hero.module.css";

export default function Hero() {
  return (
    <section className={styles.hero}>
      <div className={`${styles.container} siteContainer`}>
        <div className={styles.left}>
          <span className={styles.badge}>
            DAILY EDITORIAL • ACTIVE RECALL • UPSC
          </span>

          <h1 className={styles.title}>
            {BRAND.taglineLineOne}
            <br />
            <span>{BRAND.taglineLineTwo}</span>
          </h1>

          <p className={styles.description}>
            Daily editorial analysis designed for serious UPSC aspirants.
            Build concepts, connect current affairs with the syllabus,
            and retain them through an active recall framework.
          </p>

          <div className={styles.buttons}>
            <button
              type="button"
              className={styles.primary}
            >
              Download Today's PDF
            </button>

            <button
              type="button"
              className={styles.secondary}
            >
              Download Pro PDF
            </button>
          </div>

          <div className={styles.stats}>
            <div>
              <strong>4</strong>
              <span>Issues Daily</span>
            </div>

            <div>
              <strong>365</strong>
              <span>Days Archive</span>
            </div>

            <div>
              <strong>100%</strong>
              <span>Editorial Based</span>
            </div>
          </div>
        </div>

        <div className={styles.right}>
          <Image
            src="/hero.png"
            alt="UPSC Anchor Hero"
            width={900}
            height={900}
            priority
            className={styles.heroImage}
          />
        </div>
      </div>
    </section>
  );
}