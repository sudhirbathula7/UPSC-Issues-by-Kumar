from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT
from src.publication import PublicationMetadata


# ============================================================
# PATHS
# ============================================================

REPOSITORY_ROOT = PROJECT_ROOT / "repository"
ISSUES_DIRECTORY = REPOSITORY_ROOT / "issues"

REPOSITORY_INDEX_PATH = (
    REPOSITORY_ROOT
    / "index.json"
)

REPOSITORY_STATISTICS_PATH = (
    REPOSITORY_ROOT
    / "statistics.json"
)

REPOSITORY_SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "schema_version.json"
)

DAILY_OUTPUT_ROOT = (
    PROJECT_ROOT
    / "output"
    / "daily"
)

INPUT_DATA_PATH = (
    PROJECT_ROOT
    / "INPUT_DATA.txt"
)

INPUT_JSON_PATH = (
    PROJECT_ROOT
    / "input_processing"
    / "INPUT.json"
)


# ============================================================
# CONSTANTS
# ============================================================

REPOSITORY_SCHEMA_VERSION = "1.0"
ISSUE_SCHEMA_VERSION = "1.0"


# ============================================================
# GENERAL HELPERS
# ============================================================

def ensure_repository_structure() -> None:
    REPOSITORY_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    ISSUES_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    DAILY_OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not REPOSITORY_INDEX_PATH.exists():
        _write_json(
            REPOSITORY_INDEX_PATH,
            [],
        )

    if not REPOSITORY_STATISTICS_PATH.exists():
        _write_json(
            REPOSITORY_STATISTICS_PATH,
            {
                "schema_version": (
                    REPOSITORY_SCHEMA_VERSION
                ),
                "total_issues": 0,
                "total_days": 0,
                "average_rating": 0.0,
                "latest_issue_id": None,
                "last_updated": None,
            },
        )

    if not REPOSITORY_SCHEMA_PATH.exists():
        _write_json(
            REPOSITORY_SCHEMA_PATH,
            {
                "repository_schema_version": (
                    REPOSITORY_SCHEMA_VERSION
                ),
                "issue_schema_version": (
                    ISSUE_SCHEMA_VERSION
                ),
            },
        )


def _write_json(
    path: Path,
    data: Any,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    temporary_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_path.replace(
        path
    )


def _read_json(
    path: Path,
    default: Any,
) -> Any:
    if not path.exists():
        return default

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )
    except (
        OSError,
        json.JSONDecodeError,
    ):
        return default


def _copy_required_file(
    source: Path,
    destination: Path,
) -> None:
    if not source.exists():
        raise FileNotFoundError(
            f"Required archive source was not found: "
            f"{source}"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        source,
        destination,
    )


def _normalize_for_hash(
    value: Any,
) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_for_hash(value[key])
            for key in sorted(value)
            if key not in {
                "issue_id",
                "content_hash",
                "repository_saved_at",
            }
        }

    if isinstance(value, list):
        return [
            _normalize_for_hash(item)
            for item in value
        ]

    if isinstance(value, str):
        return " ".join(
            value.split()
        )

    return value


def calculate_content_hash(
    issue_data: dict[str, Any],
) -> str:
    normalized = _normalize_for_hash(
        issue_data
    )

    payload = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(
        payload
    ).hexdigest()


# ============================================================
# DAILY ARCHIVE
# ============================================================

def build_daily_archive_directory(
    metadata: PublicationMetadata,
) -> Path:
    parsed_date = datetime.strptime(
        metadata.publication_date,
        "%d %B %Y",
    )

    folder_name = parsed_date.strftime(
        "%d-%m-%Y"
    )

    archive_directory = (
        DAILY_OUTPUT_ROOT
        / folder_name
    )

    archive_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return archive_directory


def archive_source_files(
    archive_directory: Path,
) -> None:
    _copy_required_file(
        INPUT_DATA_PATH,
        archive_directory
        / "INPUT_DATA.txt",
    )

    _copy_required_file(
        INPUT_JSON_PATH,
        archive_directory
        / "INPUT.json",
    )


def archive_generated_pdfs(
    archive_directory: Path,
    standard_pdf: Path,
    pro_pdf: Path,
) -> tuple[Path, Path]:
    standard_destination = (
        archive_directory
        / standard_pdf.name
    )

    pro_destination = (
        archive_directory
        / pro_pdf.name
    )

    _copy_required_file(
        standard_pdf,
        standard_destination,
    )

    _copy_required_file(
        pro_pdf,
        pro_destination,
    )

    return (
        standard_destination,
        pro_destination,
    )


# ============================================================
# ISSUE REPOSITORY
# ============================================================

def load_validated_input() -> dict[str, Any]:
    data = _read_json(
        INPUT_JSON_PATH,
        {},
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Validated INPUT.json must contain "
            "a JSON object."
        )

    topics = data.get("topics")

    if not isinstance(topics, list):
        raise ValueError(
            "Validated INPUT.json does not contain "
            "a valid topics list."
        )

    return data


def build_issue_id(
    metadata: PublicationMetadata,
    topic_number: int,
) -> str:
    return (
        f"{metadata.edition_code}-"
        f"{topic_number:02d}"
    )


def build_issue_record(
    topic: dict[str, Any],
    metadata: PublicationMetadata,
) -> dict[str, Any]:
    topic_number = int(
        topic["topic_number"]
    )

    issue_id = build_issue_id(
        metadata,
        topic_number,
    )

    issue_record: dict[str, Any] = {
        "schema_version": (
            ISSUE_SCHEMA_VERSION
        ),
        "issue_id": issue_id,
        "publication_date": (
            metadata.publication_date
        ),
        "edition_code": (
            metadata.edition_code
        ),
        "status": "published",
        "topic_number": topic_number,
        "issue_title": (
            topic.get("issue_title", "")
        ),
        "rating": topic.get(
            "rating"
        ),
        "editorial_sources": topic.get(
            "editorial_sources",
            [],
        ),
        "gs_mapping": topic.get(
            "gs_mapping",
            {},
        ),
        "todays_question": topic.get(
            "todays_question",
            "",
        ),
        "recall_anchors": topic.get(
            "recall_anchors",
            [],
        ),
        "knowledge_points": topic.get(
            "knowledge_points",
            [],
        ),
        "quick_facts": topic.get(
            "quick_facts",
            [],
        ),
        "key_takeaway": topic.get(
            "key_takeaway",
            "",
        ),
        "mains_question": topic.get(
            "mains_question",
            "",
        ),
        "mains_answer": topic.get(
            "mains_answer",
            {},
        ),
        "daily_mcqs": topic.get(
            "daily_mcqs",
            [],
        ),
        "repository_saved_at": (
            datetime.now()
            .isoformat(
                timespec="seconds"
            )
        ),
    }

    issue_record["content_hash"] = (
        calculate_content_hash(
            issue_record
        )
    )

    return issue_record


def save_issue_records(
    metadata: PublicationMetadata,
) -> list[dict[str, Any]]:
    input_data = load_validated_input()

    topics = input_data.get(
        "topics",
        [],
    )

    saved_records: list[
        dict[str, Any]
    ] = []

    for topic in topics:
        if not isinstance(topic, dict):
            continue

        issue_record = build_issue_record(
            topic=topic,
            metadata=metadata,
        )

        issue_path = (
            ISSUES_DIRECTORY
            / (
                f"{issue_record['issue_id']}"
                ".json"
            )
        )

        if issue_path.exists():
            existing_record = _read_json(
                issue_path,
                {},
            )

            existing_hash = (
                existing_record.get(
                    "content_hash"
                )
                if isinstance(
                    existing_record,
                    dict,
                )
                else None
            )

            if existing_hash == issue_record[
                "content_hash"
            ]:
                saved_records.append(
                    existing_record
                )
                continue

            raise FileExistsError(
                "Repository issue already exists "
                "with different content:\n"
                f"{issue_path}"
            )

        _write_json(
            issue_path,
            issue_record,
        )

        saved_records.append(
            issue_record
        )

    return saved_records


# ============================================================
# INDEX
# ============================================================

def update_repository_index(
    issue_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    index_data = _read_json(
        REPOSITORY_INDEX_PATH,
        [],
    )

    if not isinstance(index_data, list):
        index_data = []

    indexed_ids = {
        str(item.get("issue_id"))
        for item in index_data
        if isinstance(item, dict)
    }

    for issue in issue_records:
        issue_id = str(
            issue["issue_id"]
        )

        if issue_id in indexed_ids:
            continue

        mapping = issue.get(
            "gs_mapping",
            {},
        )

        index_entry = {
            "issue_id": issue_id,
            "publication_date": (
                issue.get(
                    "publication_date"
                )
            ),
            "edition_code": (
                issue.get(
                    "edition_code"
                )
            ),
            "topic_number": (
                issue.get(
                    "topic_number"
                )
            ),
            "issue_title": (
                issue.get(
                    "issue_title"
                )
            ),
            "rating": issue.get(
                "rating"
            ),
            "gs_paper": (
                mapping.get("paper")
                if isinstance(
                    mapping,
                    dict,
                )
                else None
            ),
            "gs_subject": (
                mapping.get("subject")
                if isinstance(
                    mapping,
                    dict,
                )
                else None
            ),
            "content_hash": (
                issue.get(
                    "content_hash"
                )
            ),
        }

        index_data.append(
            index_entry
        )

        indexed_ids.add(
            issue_id
        )

    index_data.sort(
        key=lambda item: (
            str(
                item.get(
                    "publication_date",
                    "",
                )
            ),
            int(
                item.get(
                    "topic_number",
                    0,
                )
                or 0
            ),
        )
    )

    _write_json(
        REPOSITORY_INDEX_PATH,
        index_data,
    )

    return index_data


# ============================================================
# STATISTICS
# ============================================================

def update_repository_statistics(
    index_data: list[dict[str, Any]],
) -> dict[str, Any]:
    total_issues = len(
        index_data
    )

    unique_dates = {
        str(
            item.get(
                "publication_date"
            )
        )
        for item in index_data
        if item.get(
            "publication_date"
        )
    }

    ratings = [
        float(item["rating"])
        for item in index_data
        if isinstance(
            item.get("rating"),
            (int, float),
        )
    ]

    average_rating = (
        round(
            sum(ratings) / len(ratings),
            2,
        )
        if ratings
        else 0.0
    )

    latest_issue_id = (
        index_data[-1].get(
            "issue_id"
        )
        if index_data
        else None
    )

    statistics = {
        "schema_version": (
            REPOSITORY_SCHEMA_VERSION
        ),
        "total_issues": (
            total_issues
        ),
        "total_days": len(
            unique_dates
        ),
        "average_rating": (
            average_rating
        ),
        "latest_issue_id": (
            latest_issue_id
        ),
        "last_updated": (
            datetime.now()
            .isoformat(
                timespec="seconds"
            )
        ),
    }

    _write_json(
        REPOSITORY_STATISTICS_PATH,
        statistics,
    )

    return statistics


# ============================================================
# MANIFEST AND SUMMARY
# ============================================================

def write_production_manifest(
    archive_directory: Path,
    metadata: PublicationMetadata,
    issue_records: list[dict[str, Any]],
    standard_pdf: Path,
    pro_pdf: Path,
) -> Path:
    manifest_path = (
        archive_directory
        / "output_manifest.json"
    )

    manifest = {
        "schema_version": "1.0",
        "publication_date": (
            metadata.publication_date
        ),
        "edition_code": (
            metadata.edition_code
        ),
        "issue_count": len(
            issue_records
        ),
        "issue_ids": [
            issue["issue_id"]
            for issue in issue_records
        ],
        "standard_pdf": {
            "generated": (
                standard_pdf.exists()
            ),
            "filename": (
                standard_pdf.name
            ),
        },
        "pro_pdf": {
            "generated": (
                pro_pdf.exists()
            ),
            "filename": (
                pro_pdf.name
            ),
        },
        "repository_updated": True,
        "daily_archive_created": True,
        "created_at": (
            datetime.now()
            .isoformat(
                timespec="seconds"
            )
        ),
    }

    _write_json(
        manifest_path,
        manifest,
    )

    return manifest_path


def write_production_summary(
    archive_directory: Path,
    metadata: PublicationMetadata,
    issue_records: list[dict[str, Any]],
    standard_pdf: Path,
    pro_pdf: Path,
    elapsed_seconds: float | None = None,
) -> Path:
    summary_path = (
        archive_directory
        / "production_summary.txt"
    )

    lines = [
        "=" * 72,
        "UPSC ISSUES BY KUMAR — PRODUCTION SUMMARY",
        "=" * 72,
        "",
        (
            f"Publication Date : "
            f"{metadata.publication_date}"
        ),
        (
            f"Edition Code     : "
            f"{metadata.edition_code}"
        ),
        (
            f"Issues Published : "
            f"{len(issue_records)}"
        ),
        "",
        "Issue IDs",
        "-" * 72,
    ]

    lines.extend(
        issue["issue_id"]
        for issue in issue_records
    )

    lines.extend(
        [
            "",
            (
                f"Standard PDF    : "
                f"{standard_pdf.name}"
            ),
            (
                f"Pro PDF         : "
                f"{pro_pdf.name}"
            ),
            "Repository       : Updated",
            "Daily Archive    : Created",
        ]
    )

    if elapsed_seconds is not None:
        lines.append(
            f"Duration         : "
            f"{elapsed_seconds:.1f} seconds"
        )

    lines.extend(
        [
            "",
            "=" * 72,
        ]
    )

    summary_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return summary_path


# ============================================================
# COMPLETE REPOSITORY UPDATE
# ============================================================

def complete_repository_and_archive(
    *,
    metadata: PublicationMetadata,
    standard_pdf: Path,
    pro_pdf: Path,
    elapsed_seconds: float | None = None,
) -> dict[str, Any]:
    ensure_repository_structure()

    archive_directory = (
        build_daily_archive_directory(
            metadata
        )
    )

    archive_source_files(
        archive_directory
    )

    (
        archived_standard_pdf,
        archived_pro_pdf,
    ) = archive_generated_pdfs(
        archive_directory=archive_directory,
        standard_pdf=standard_pdf,
        pro_pdf=pro_pdf,
    )

    issue_records = save_issue_records(
        metadata
    )

    index_data = update_repository_index(
        issue_records
    )

    statistics = (
        update_repository_statistics(
            index_data
        )
    )

    manifest_path = (
        write_production_manifest(
            archive_directory=archive_directory,
            metadata=metadata,
            issue_records=issue_records,
            standard_pdf=(
                archived_standard_pdf
            ),
            pro_pdf=(
                archived_pro_pdf
            ),
        )
    )

    summary_path = (
        write_production_summary(
            archive_directory=archive_directory,
            metadata=metadata,
            issue_records=issue_records,
            standard_pdf=(
                archived_standard_pdf
            ),
            pro_pdf=(
                archived_pro_pdf
            ),
            elapsed_seconds=(
                elapsed_seconds
            ),
        )
    )

    return {
        "archive_directory": (
            archive_directory
        ),
        "issue_records": (
            issue_records
        ),
        "index_path": (
            REPOSITORY_INDEX_PATH
        ),
        "statistics_path": (
            REPOSITORY_STATISTICS_PATH
        ),
        "manifest_path": (
            manifest_path
        ),
        "summary_path": (
            summary_path
        ),
        "statistics": (
            statistics
        ),
    }