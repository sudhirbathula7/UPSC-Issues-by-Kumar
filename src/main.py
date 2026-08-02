from __future__ import annotations

import os
import time
from pathlib import Path

from src.config import PREVIEW_PATH
from src.pdf.font_loader import register_fonts
from src.pdf.pdf_generator import generate_pdf
from src.pdf.pro_pdf_generator import generate_pro_pdf
from src.publication import (
    PRO_PDF_FILENAME,
    STANDARD_PDF_FILENAME,
    build_publication_metadata,
)
from src.repository.repository_manager import (
    complete_repository_and_archive,
)


# ============================================================
# DEVELOPMENT SETTINGS
# ============================================================

OPEN_PDF = True
OPEN_PRO_PDF = True


# ============================================================
# OPEN GENERATED FILE
# ============================================================

def open_generated_file(
    file_path: Path,
) -> None:
    if not file_path.exists():
        return

    if os.name == "nt":
        os.startfile(
            file_path.resolve()
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    production_started_at = (
        time.perf_counter()
    )

    # Register fonts once.
    register_fonts()

    PREVIEW_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    # One metadata object for the complete run.
    metadata = (
        build_publication_metadata()
    )

    # ========================================================
    # STANDARD PDF
    # ========================================================

    pdf_output_file = (
        PREVIEW_PATH
        / STANDARD_PDF_FILENAME
    )

    generated_pdf = generate_pdf(
        output_path=pdf_output_file,
        metadata=metadata,
    )

    print()
    print("=" * 60)
    print("STANDARD PDF GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(
        f"Date   : {metadata.publication_date}"
    )
    print(
        f"Edition: {metadata.edition_code}"
    )
    print(
        f"Output : {generated_pdf.resolve()}"
    )
    print("=" * 60)

    # ========================================================
    # PRO PDF
    # ========================================================

    pro_output_file = (
        PREVIEW_PATH
        / PRO_PDF_FILENAME
    )

    generated_pro_pdf = generate_pro_pdf(
        output_path=pro_output_file,
        metadata=metadata,
    )

    print()
    print("=" * 60)
    print("PRO PDF GENERATED SUCCESSFULLY")
    print("=" * 60)
    print(
        f"Date   : {metadata.publication_date}"
    )
    print(
        f"Edition: {metadata.edition_code}"
    )
    print(
        f"Output : {generated_pro_pdf.resolve()}"
    )
    print("=" * 60)

    # ========================================================
    # REPOSITORY + DAILY ARCHIVE
    # ========================================================

    elapsed_seconds = (
        time.perf_counter()
        - production_started_at
    )

    repository_result = (
        complete_repository_and_archive(
            metadata=metadata,
            standard_pdf=generated_pdf,
            pro_pdf=generated_pro_pdf,
            elapsed_seconds=elapsed_seconds,
        )
    )

    archive_directory = (
        repository_result[
            "archive_directory"
        ]
    )

    issue_records = (
        repository_result[
            "issue_records"
        ]
    )

    statistics = (
        repository_result[
            "statistics"
        ]
    )

    print()
    print("=" * 60)
    print("REPOSITORY AND ARCHIVE UPDATED")
    print("=" * 60)
    print(
        f"Archive     : "
        f"{archive_directory.resolve()}"
    )
    print(
        f"Issues saved: "
        f"{len(issue_records)}"
    )
    print(
        f"Total issues: "
        f"{statistics['total_issues']}"
    )
    print(
        f"Total days  : "
        f"{statistics['total_days']}"
    )
    print("=" * 60)

    # ========================================================
    # OPEN BOTH PDFS
    # ========================================================

    if OPEN_PDF:
        open_generated_file(
            generated_pdf
        )

    if OPEN_PRO_PDF:
        open_generated_file(
            generated_pro_pdf
        )


if __name__ == "__main__":
    main()