import styles from "./Download.module.css";

export default function Download() {
  return (
    <section className={styles.section}>
      <div className={`${styles.container} siteContainer`}>
        <div className={styles.heading}>
          <span className={styles.eyebrow}>
            CHOOSE YOUR EDITION
          </span>

          <h2>What&apos;s included in each PDF?</h2>

          <p>
            Start with the daily edition or choose Pro for
            complete prelims and mains support.
          </p>
        </div>

        <div className={styles.comparison}>
          <article className={styles.editionCard}>
            <span className={styles.cardLabel}>
              TODAY&apos;S PDF
            </span>

            <h3>Daily Editorial Learning</h3>

            <ul>
              <li>Daily Editorial Summary</li>
              <li>Knowledge Points</li>
              <li>Today&apos;s Question</li>
            </ul>
          </article>

          <article
            className={`${styles.editionCard} ${styles.proCard}`}
          >
            <span className={styles.recommended}>
              RECOMMENDED
            </span>

            <span className={styles.cardLabel}>
              PRO PDF
            </span>

            <h3>Complete UPSC Preparation</h3>

            <ul>
              <li>Everything in Today&apos;s PDF</li>
              <li>Mains Perspective</li>
              <li>Prelims MCQs</li>
              <li>Deeper Analysis</li>
            </ul>
          </article>
        </div>
      </div>
    </section>
  );
}