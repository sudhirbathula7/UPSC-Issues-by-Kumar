from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = Path(__file__).resolve().parent / "INPUT.json"

INPUT_CANDIDATES = (
    PROJECT_ROOT / "input.txt",
    PROJECT_ROOT / "INPUT.txt",
    PROJECT_ROOT / "INPUT_DATA.txt",
)

PUBLICATION_DATE_HEADING = "PUBLICATION DATE"

SUPPORTED_PUBLICATION_DATE_FORMATS = (
    "%d.%m.%y",
    "%d-%m-%y",
    "%d/%m/%y",
    "%d.%m.%Y",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d %B %Y",
)


class ConversionError(ValueError):
    """Raised when input text cannot be converted safely."""


# ============================================================
# GENERAL HELPERS
# ============================================================

def _clean(value: str) -> str:
    value = value.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )

    value = re.sub(
        r"\n[ \t]+",
        "\n",
        value,
    )

    return value.strip()


def _nonempty_lines(
    value: str,
) -> list[str]:
    return [
        line.strip()
        for line in value.splitlines()
        if line.strip()
    ]


def _find_input_file() -> Path:
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path

    names = ", ".join(
        path.name
        for path in INPUT_CANDIDATES
    )

    raise FileNotFoundError(
        "No input text file found in project root. "
        f"Expected one of: {names}"
    )


# ============================================================
# PUBLICATION DATE
# ============================================================

def _parse_publication_date(
    raw_date: str,
) -> datetime:
    cleaned_date = _clean(
        raw_date
    )

    for date_format in (
        SUPPORTED_PUBLICATION_DATE_FORMATS
    ):
        try:
            return datetime.strptime(
                cleaned_date,
                date_format,
            )

        except ValueError:
            continue

    raise ConversionError(
        "Unsupported PUBLICATION DATE format.\n\n"
        "Supported examples:\n"
        "03.08.26\n"
        "03-08-26\n"
        "03/08/26\n"
        "03.08.2026\n"
        "03-08-2026\n"
        "03/08/2026\n"
        "03 August 2026"
    )


def _extract_publication_date(
    text: str,
) -> tuple[str, str]:
    """
    Read PUBLICATION DATE from the content before TOPIC 1.

    Accepted formats:

        03.08.26
        03-08-26
        03/08/26
        03.08.2026
        03-08-2026
        03/08/2026
        03 August 2026

    Returns:

        display_date -> 03 August 2026
        iso_date     -> 2026-08-03
    """

    normalized_text = (
        text
        .replace(
            "\r\n",
            "\n",
        )
        .replace(
            "\r",
            "\n",
        )
    )

    first_topic_match = re.search(
        r"(?m)^\s*TOPIC\s+\d+\s*$",
        normalized_text,
    )

    if not first_topic_match:
        raise ConversionError(
            "No 'TOPIC X' heading was found."
        )

    metadata_block = normalized_text[
        :first_topic_match.start()
    ]

    date_match = re.search(
        rf"(?im)^\s*"
        rf"{re.escape(PUBLICATION_DATE_HEADING)}"
        rf"\s*$"
        rf"\s*^\s*(.+?)\s*$",
        metadata_block,
    )

    if not date_match:
        raise ConversionError(
            "Missing PUBLICATION DATE block at "
            "the top of the input.\n\n"
            "Expected example:\n\n"
            "PUBLICATION DATE\n\n"
            "03.08.26"
        )

    parsed_date = _parse_publication_date(
        date_match.group(1)
    )

    display_date = parsed_date.strftime(
        "%d %B %Y"
    )

    iso_date = parsed_date.strftime(
        "%Y-%m-%d"
    )

    return (
        display_date,
        iso_date,
    )
# ============================================================
# TOPIC SPLITTING
# ============================================================

def _split_topics(
    text: str,
) -> list[tuple[int, str]]:
    text = (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # Remove long visual separators.
    text = re.sub(
        r"\s*-{20,}\s*",
        "\n\n",
        text,
    )

    matches = list(
        re.finditer(
            r"(?m)^\s*TOPIC\s+(\d+)\s*$",
            text,
        )
    )

    if not matches:
        raise ConversionError(
            "No 'TOPIC X' heading was found."
        )

    topics: list[
        tuple[int, str]
    ] = []

    for index, match in enumerate(
        matches
    ):
        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        topic_number = int(
            match.group(1)
        )

        block = text[
            start:end
        ].strip()

        block = re.sub(
            r"(?m)^\s*END TOPIC\s*$",
            "",
            block,
        ).strip()

        topics.append(
            (
                topic_number,
                block,
            )
        )

    return topics


# ============================================================
# SECTION HEADINGS
# ============================================================

SECTION_HEADINGS = [
    "ISSUE TITLE",
    "RATING",
    "EDITORIAL SOURCE(S)",
    "GS MAPPING",
    "TODAY'S QUESTION",
    "RECALL ANCHORS",
    "KNOWLEDGE POINT 1",
    "KNOWLEDGE POINT 2",
    "KNOWLEDGE POINT 3",
    "KNOWLEDGE POINT 4",
    "KNOWLEDGE POINT 5",
    "QUICK FACTS",
    "KEY TAKEAWAY",
    "MAINS QUESTION",
    "MAINS ANSWER",
    "DAILY MCQ 1",
    "DAILY MCQ 2",
    "DAILY MCQ 3",
]


# ============================================================
# SECTION EXTRACTION
# ============================================================

def _extract_sections(
    block: str,
) -> dict[str, str]:

    headings = "|".join(
        re.escape(item)
        for item in SECTION_HEADINGS
    )

    pattern = re.compile(
        rf"(?m)^\s*({headings})\s*$"
    )

    matches = list(
        pattern.finditer(
            block
        )
    )

    found = [
        match.group(1)
        for match in matches
    ]

    missing = [
        heading
        for heading in SECTION_HEADINGS
        if heading not in found
    ]

    duplicates = sorted(
        {
            heading
            for heading in found
            if found.count(heading) > 1
        }
    )

    if missing:
        raise ConversionError(
            "Missing section(s): "
            + ", ".join(missing)
        )

    if duplicates:
        raise ConversionError(
            "Duplicate section(s): "
            + ", ".join(duplicates)
        )

    sections: dict[
        str,
        str,
    ] = {}

    for index, match in enumerate(
        matches
    ):
        heading = match.group(1)

        start = match.end()

        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(block)
        )

        sections[
            heading
        ] = _clean(
            block[start:end]
        )

    return sections


# ============================================================
# GS MAPPING
# ============================================================

def _parse_gs_mapping(
    value: str,
) -> dict[str, str]:

    parts = [
        part.strip()
        for part in re.split(
            r"\s*[•|]\s*",
            value,
        )
        if part.strip()
    ]

    return {
        "display": value.strip(),
        "paper": (
            parts[0]
            if len(parts) > 0
            else ""
        ),
        "subject": (
            parts[1]
            if len(parts) > 1
            else ""
        ),
        "syllabus": (
            " • ".join(
                parts[2:]
            )
            if len(parts) > 2
            else ""
        ),
    }


# ============================================================
# KNOWLEDGE POINT
# ============================================================

def _parse_knowledge_point(
    value: str,
    number: int,
) -> dict[str, Any]:

    lines = _nonempty_lines(
        value
    )

    if len(lines) < 2:
        raise ConversionError(
            f"Knowledge Point {number} "
            "must contain a heading "
            "and explanation."
        )

    return {
        "number": number,
        "heading": lines[0],
        "explanation": " ".join(
            lines[1:]
        ),
    }


# ============================================================
# QUICK FACTS
# ============================================================

def _parse_quick_facts(
    value: str,
) -> list[str]:

    lines = _nonempty_lines(
        value
    )

    facts: list[str] = []

    current = ""

    for line in lines:

        if re.match(
            r"^[•*\-]\s+",
            line,
        ):
            if current:
                facts.append(
                    current.strip()
                )

            current = re.sub(
                r"^[•*\-]\s+",
                "",
                line,
            ).strip()

        else:
            current = (
                f"{current} {line}"
            ).strip()

    if current:
        facts.append(
            current.strip()
        )

    if len(facts) <= 1:

        chunks = [
            chunk.strip()
            for chunk in re.split(
                r"\n\s*\n",
                value,
            )
            if chunk.strip()
        ]

        if len(chunks) > 1:
            facts = [
                re.sub(
                    r"^[•*\-]\s*",
                    "",
                    _clean(chunk),
                )
                for chunk in chunks
            ]

    return facts
# ============================================================
# MCQ
# ============================================================

def _parse_mcq(
    value: str,
    number: int,
) -> dict[str, Any]:
    answer_match = re.search(
        r"(?im)^\s*(?:Correct\s+)?"
        r"Answer\s*:\s*([A-D])\s*$",
        value,
    )

    explanation_match = re.search(
        r"(?im)^\s*Explanation\s*:\s*(.+)$",
        value,
        re.S,
    )

    if not answer_match:
        raise ConversionError(
            f"Daily MCQ {number} has no valid "
            "Answer: A-D line."
        )

    if not explanation_match:
        raise ConversionError(
            f"Daily MCQ {number} has no Explanation line."
        )

    before_answer = value[
        :answer_match.start()
    ].strip()

    option_matches = list(
        re.finditer(
            r"(?m)^\s*([A-D])\.\s+(.+?)\s*$",
            before_answer,
        )
    )

    if len(option_matches) != 4:
        raise ConversionError(
            f"Daily MCQ {number} must contain "
            "exactly four options A-D."
        )

    question = before_answer[
        :option_matches[0].start()
    ].strip()

    question = re.sub(
        r"^\s*Q\.\s*",
        "",
        question,
        flags=re.I,
    ).strip()

    options = {
        match.group(1): (
            match.group(2).strip()
        )
        for match in option_matches
    }

    return {
        "number": number,
        "question": question,
        "options": options,
        "correct_answer": (
            answer_match
            .group(1)
            .upper()
        ),
        "explanation": _clean(
            explanation_match.group(1)
        ),
    }


# ============================================================
# TOPIC PARSER
# ============================================================

def _parse_topic(
    topic_number: int,
    block: str,
) -> dict[str, Any]:
    sections = _extract_sections(
        block
    )

    try:
        rating = float(
            sections["RATING"]
        )

    except ValueError as exc:
        raise ConversionError(
            f"Topic {topic_number}: "
            "RATING must be numeric."
        ) from exc

    anchors = _nonempty_lines(
        sections["RECALL ANCHORS"]
    )

    anchors = [
        re.sub(
            r"^\d+\.\s*",
            "",
            anchor,
        )
        for anchor in anchors
    ]

    source_text = sections[
        "EDITORIAL SOURCE(S)"
    ]

    sources = [
        source.strip()
        for source in re.split(
            r"\s*[,;]\s*",
            source_text,
        )
        if source.strip()
    ]

    paragraphs = [
        _clean(paragraph)
        for paragraph in re.split(
            r"\n\s*\n",
            sections["MAINS ANSWER"],
        )
        if paragraph.strip()
    ]

    knowledge_points = [
        _parse_knowledge_point(
            sections[
                f"KNOWLEDGE POINT {index}"
            ],
            index,
        )
        for index in range(
            1,
            6,
        )
    ]

    daily_mcqs = [
        _parse_mcq(
            sections[
                f"DAILY MCQ {index}"
            ],
            index,
        )
        for index in range(
            1,
            4,
        )
    ]

    return {
        "topic_number": topic_number,
        "issue_title": (
            sections["ISSUE TITLE"]
        ),
        "rating": rating,
        "editorial_sources": sources,
        "gs_mapping": (
            _parse_gs_mapping(
                sections["GS MAPPING"]
            )
        ),
        "todays_question": (
            sections["TODAY'S QUESTION"]
        ),
        "recall_anchors": anchors,
        "knowledge_points": (
            knowledge_points
        ),
        "quick_facts": (
            _parse_quick_facts(
                sections["QUICK FACTS"]
            )
        ),
        "key_takeaway": (
            sections["KEY TAKEAWAY"]
        ),
        "mains_question": (
            sections["MAINS QUESTION"]
        ),
        "mains_answer": {
            "paragraphs": paragraphs,
            "full_text": "\n\n".join(
                paragraphs
            ),
        },
        "daily_mcqs": daily_mcqs,
    }
# ============================================================
# COMPLETE CONVERSION
# ============================================================

def convert_text(
    text: str,
) -> dict[str, Any]:
    (
        publication_date,
        publication_date_iso,
    ) = _extract_publication_date(
        text
    )

    topics = [
        _parse_topic(
            topic_number,
            block,
        )
        for topic_number, block
        in _split_topics(text)
    ]

    return {
        "schema_version": "2.0",
        "publication_date": (
            publication_date
        ),
        "publication_date_iso": (
            publication_date_iso
        ),
        "topic_count": len(topics),
        "topics": topics,
    }


def convert_file(
    input_path: Path,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    text = input_path.read_text(
        encoding="utf-8-sig"
    )

    data = convert_text(
        text
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = output_path.with_suffix(
        ".json.tmp"
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
        output_path
    )

    return output_path


# ============================================================
# COMMAND LINE
# ============================================================

def main() -> int:
    try:
        input_path = _find_input_file()

        output_path = convert_file(
            input_path
        )

        data = json.loads(
            output_path.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"Converted: {input_path}"
        )

        print(
            f"Created:   {output_path}"
        )

        print(
            "Date:      "
            f"{data['publication_date']}"
        )

        print(
            "ISO Date:  "
            f"{data['publication_date_iso']}"
        )

        return 0

    except (
        OSError,
        ConversionError,
    ) as exc:
        print(
            f"CONVERSION FAILED: {exc}",
            file=sys.stderr,
        )

        return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )