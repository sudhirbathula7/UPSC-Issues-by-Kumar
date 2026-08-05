import Link from "next/link";

import { getLatestEdition } from "@/lib/issues";

import styles from "./TodaysIssues.module.css";

export default function TodaysIssues() {
  const edition = getLatestEdition();

  if (!edition) {
    return null;
  }

  return (
    <section
      id="todays-issues"
      className={styles.section}
    >
      <div className={`${styles.container} siteContainer`}>
        <div className={styles.header}>
          <div>
            <span className={styles.badge}>
              TODAY'S EDITION
            </span>

            <h2>Today's UPSC Issues</h2>
          </div>

          <span className={styles.date}>
            {edition.publicationDate}
          </span>
        </div>

        <div className={styles.grid}>
          {edition.issues.map((issue) => (
            <article
              key={issue.issue_id}
              className={styles.card}
            >
              <div className={styles.top}>
                <span>
                  ISSUE {issue.topic_number}
                </span>

                <strong>
                  ⭐ {issue.rating ?? "-"}
                </strong>
              </div>

              <h3>{issue.issue_title}</h3>

              <div className={styles.tags}>
                <span>
                  {issue.gs_mapping.paper}
                </span>

                <span>
                  {issue.gs_mapping.subject}
                </span>
              </div>

              <p>
                {issue.todays_question}
              </p>

              <div className={styles.footer}>
                <span>
                  {issue.editorial_sources.join(", ")}
                </span>

                <Link href="#">
                  Read →
                </Link>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}