import Image from "next/image";

import {
  getLatestEdition,
} from "@/lib/issues";

import ThemeToggle from "./theme-toggle";


export const dynamic = "force-dynamic";


function RatingBadge({
  rating,
}: {
  rating: number | null;
}) {
  if (rating === null) {
    return null;
  }

  return (
    <span className="rating-badge">
      {rating.toFixed(1)}
    </span>
  );
}


export default function Home() {
  const latestEdition = getLatestEdition();

  return (
    <main className="site-shell">
      <div className="site-frame">
        <header className="site-header">
          <a
            href="/"
            className="brand-row"
            aria-label="UPSC Issues by Kumar homepage"
          >
            <Image
              src="/logo.png"
              alt="UPSC Issues by Kumar logo"
              width={72}
              height={72}
              className="brand-logo"
              priority
            />

            <div className="brand-name">
              <strong>UPSC ISSUES</strong>
              <span>by KUMAR</span>
            </div>
          </a>

          <ThemeToggle />
        </header>

        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">
              DAILY EDITORIAL LEARNING
            </p>

            <h1>
              Understand the issue.
              <span>
                Recall the argument.
              </span>
            </h1>

            <p className="hero-description">
              Curated editorials. Curiosity questions.
              Recall anchors. Mains perspective.
            </p>
          </div>

          <aside className="latest-card">
            <div className="latest-icon">
              <span aria-hidden="true">
                ▦
              </span>
            </div>

            <div className="latest-content">
              <p className="latest-label">
                LATEST EDITION
              </p>

              {latestEdition ? (
                <>
                  <h2>
                    {latestEdition.publicationDate}
                  </h2>

                  <p className="latest-meta">
                    <span>
                      {latestEdition.editionCode}
                    </span>

                    <i aria-hidden="true">
                      •
                    </i>

                    <span>
                      {latestEdition.issues.length}
                      {" "}
                      {latestEdition.issues.length === 1
                        ? "Issue"
                        : "Issues"}
                    </span>
                  </p>
                </>
              ) : (
                <p className="empty-message">
                  No edition found.
                </p>
              )}
            </div>
          </aside>
        </section>

        <section className="issues-section">
          <div className="section-heading">
            <div className="section-title-group">
              <span className="section-rule" />

              <h2>
                TODAY&apos;S ISSUES
              </h2>
            </div>

            {latestEdition && (
              <p className="section-date">
                {latestEdition.publicationDate}
              </p>
            )}
          </div>

          {latestEdition &&
          latestEdition.issues.length > 0 ? (
            <div className="issue-grid">
              {latestEdition.issues.map(
                (issue) => (
                  <article
                    className="issue-card"
                    key={issue.issue_id}
                  >
                    <div className="issue-top">
                      <span className="issue-label">
                        ISSUE{" "}
                        {String(
                          issue.topic_number,
                        ).padStart(2, "0")}
                      </span>

                      <RatingBadge
                        rating={issue.rating}
                      />
                    </div>

                    <h3>
                      {issue.issue_title}
                    </h3>

                    <div className="gs-tags">
                      {issue.gs_mapping.paper && (
                        <span>
                          {issue.gs_mapping.paper}
                        </span>
                      )}

                      {issue.gs_mapping.subject && (
                        <span>
                          {issue.gs_mapping.subject}
                        </span>
                      )}
                    </div>

                    <div className="issue-divider" />

                    <p className="issue-question">
                      {issue.todays_question}
                    </p>

                    <div className="anchor-list">
                      {issue.recall_anchors.map(
                        (anchor) => (
                          <span key={anchor}>
                            {anchor}
                          </span>
                        ),
                      )}
                    </div>

                    <div className="issue-footer">
                      <small>
                        {issue.issue_id}
                      </small>

                      <button
                        type="button"
                        className="read-button"
                        title="Individual issue page will be connected next."
                      >
                        Read →
                      </button>
                    </div>
                  </article>
                ),
              )}
            </div>
          ) : (
            <div className="empty-state">
              No published issues were found.
            </div>
          )}
        </section>

        <section className="download-panel">
          <div className="download-icon">
            <span aria-hidden="true">
              ↓
            </span>
          </div>

          <div className="download-copy">
            <p className="download-label">
              TODAY&apos;S EDITION
            </p>

            <h2>
              Download Today&apos;s Edition
            </h2>

            <p>
              Choose the edition that suits your
              preparation.
            </p>
          </div>

          <div className="download-actions">
            <button
              type="button"
              className="download-button primary-download"
              title="PDF connection will be added next."
            >
              Today&apos;s PDF
            </button>

            <button
              type="button"
              className="download-button secondary-download"
              title="PDF Pro connection will be added next."
            >
              Today&apos;s PDF Pro
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}