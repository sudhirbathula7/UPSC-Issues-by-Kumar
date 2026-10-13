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
    "CONCEPT UNFOLD",
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

    value = _clean(value)

    paper = ""
    subject = ""
    syllabus = ""

    # Format:
    # GS Paper II | Social Justice | Health and Education
    #
    # or:
    # GS Paper II • Social Justice • Health and Education
    if "|" in value or "•" in value:
        parts = [
            part.strip()
            for part in re.split(
                r"\s*[•|]\s*",
                value,
            )
            if part.strip()
        ]

        paper = (
            parts[0]
            if len(parts) > 0
            else ""
        )

        subject = (
            parts[1]
            if len(parts) > 1
            else ""
        )

        syllabus = (
            " • ".join(parts[2:])
            if len(parts) > 2
            else ""
        )

    # Format:
    # GS Paper II — Health, Education, Government Policies
    elif re.search(
        r"\s+[—–-]\s+",
        value,
    ):
        split_parts = re.split(
            r"\s+[—–-]\s+",
            value,
            maxsplit=1,
        )

        paper = split_parts[0].strip()

        remainder = (
            split_parts[1].strip()
            if len(split_parts) > 1
            else ""
        )

        remainder_parts = [
            part.strip()
            for part in remainder.split(",")
            if part.strip()
        ]

        subject = (
            remainder_parts[0]
            if remainder_parts
            else ""
        )

        syllabus = (
            ", ".join(
                remainder_parts[1:]
            )
            if len(remainder_parts) > 1
            else subject
        )

    # Labelled format:
    #
    # Paper: GS Paper II
    # Subject: Social Justice
    # Syllabus: Health and Education
    else:
        labelled: dict[str, str] = {}

        for line in _nonempty_lines(value):
            match = re.match(
                r"(?i)^\s*"
                r"(paper|subject|syllabus)"
                r"\s*:\s*(.+?)\s*$",
                line,
            )

            if match:
                labelled[
                    match.group(1).casefold()
                ] = match.group(2).strip()

        if labelled:
            paper = labelled.get(
                "paper",
                "",
            )

            subject = labelled.get(
                "subject",
                "",
            )

            syllabus = labelled.get(
                "syllabus",
                "",
            )

        else:
            parts = _nonempty_lines(
                value
            )

            paper = (
                parts[0]
                if len(parts) > 0
                else ""
            )

            subject = (
                parts[1]
                if len(parts) > 1
                else ""
            )

            syllabus = (
                " • ".join(parts[2:])
                if len(parts) > 2
                else ""
            )

    return {
        "display": " | ".join(
            item
            for item in (
                paper,
                subject,
                syllabus,
            )
            if item
        ),
        "paper": paper,
        "subject": subject,
        "syllabus": syllabus,
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
# CONCEPT UNFOLD
# ============================================================

def _parse_concept_unfold(
    value: str,
) -> dict[str, Any]:
    """
    Parse the selected Concept Unfold for one editorial.

    Expected input format:

        [Basic UPSC concept / condition] →

        [Consequence 1 heading]
        [Consequence 1 explanation]

        [Consequence 2 heading]
        [Consequence 2 explanation]

        [Consequence 3 heading]
        [Consequence 3 explanation]

    Example:

        Heavy dependence on a maritime chokepoint increases vulnerability →

        A local disruption can affect many countries
        When large amounts of oil and gas pass through one narrow route,
        war or blockage there can interrupt energy supplies far beyond
        the conflict area.

        Energy costs can rise across the economy
        Reduced supply can make oil and gas more expensive. Higher fuel
        costs then increase transport and production expenses, making
        many everyday goods costlier.

        Countries may seek alternative supply routes
        Repeated disruption risks can encourage governments and companies
        to diversify energy suppliers, transport routes and strategic
        reserves to reduce dependence on a single chokepoint.

    Stored JSON structure:

        {
            "concept": "...",
            "consequences": [
                {
                    "title": "...",
                    "explanation": "..."
                },
                {
                    "title": "...",
                    "explanation": "..."
                },
                {
                    "title": "...",
                    "explanation": "..."
                }
            ]
        }

    Important:
    - Only ONE selected concept is stored.
    - Exactly THREE consequences are required.
    - The three candidate options used during content generation
      are not part of the production input format.
    """

    lines = _nonempty_lines(value)

    # --------------------------------------------------------
    # STRUCTURE VALIDATION
    # --------------------------------------------------------

    # 1 concept
    # + 3 consequence headings
    # + 3 consequence explanations
    # = 7 non-empty lines
    expected_lines = 7

    if len(lines) != expected_lines:
        raise ConversionError(
            "CONCEPT UNFOLD must contain exactly "
            "7 non-empty lines:\n"
            "1. Basic concept / condition\n"
            "2. Consequence 1 heading\n"
            "3. Consequence 1 explanation\n"
            "4. Consequence 2 heading\n"
            "5. Consequence 2 explanation\n"
            "6. Consequence 3 heading\n"
            "7. Consequence 3 explanation\n\n"
            f"Found {len(lines)} non-empty line(s)."
        )

    # --------------------------------------------------------
    # CONCEPT
    # --------------------------------------------------------

    concept = lines[0].strip()

    if not concept:
        raise ConversionError(
            "CONCEPT UNFOLD concept cannot be empty."
        )

    # The arrow belongs to presentation.
    # Accept common arrow styles in INPUT_DATA.txt,
    # but remove them before storing the concept.

    concept = re.sub(
        r"\s*(?:→|->|=>)\s*$",
        "",
        concept,
    ).strip()

    if not concept:
        raise ConversionError(
            "CONCEPT UNFOLD concept cannot contain only an arrow."
        )

    # --------------------------------------------------------
    # CONSEQUENCES
    # --------------------------------------------------------

    consequences: list[dict[str, str]] = []

    line_index = 1

    for consequence_number in range(1, 4):

        title = lines[line_index].strip()
        explanation = lines[line_index + 1].strip()

        line_index += 2

        if not title:
            raise ConversionError(
                "CONCEPT UNFOLD "
                f"Consequence {consequence_number} "
                "heading cannot be empty."
            )

        if not explanation:
            raise ConversionError(
                "CONCEPT UNFOLD "
                f"Consequence {consequence_number} "
                "explanation cannot be empty."
            )

        consequences.append(
            {
                "title": title,
                "explanation": explanation,
            }
        )

    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    consequence_titles = [
        consequence["title"].casefold()
        for consequence in consequences
    ]

    if len(set(consequence_titles)) != len(consequence_titles):
        raise ConversionError(
            "CONCEPT UNFOLD consequence headings "
            "must all be different."
        )

    # --------------------------------------------------------
    # FINAL STRUCTURE
    # --------------------------------------------------------

    return {
        "concept": concept,
        "consequences": consequences,
    }

# ============================================================
# DAILY MCQ
# ============================================================

def _parse_mcq(
    value: str,
    number: int,
) -> dict[str, Any]:
    """Parse one DAILY MCQ section."""

    lines = _nonempty_lines(value)

    if not lines:
        raise ConversionError(
            f"DAILY MCQ {number} cannot be empty."
        )

    option_pattern = re.compile(
        r"^([A-D])\.\s*(.+)$",
        re.IGNORECASE,
    )
    correct_pattern = re.compile(
        r"^Correct\s+Answer\s*:\s*([A-D])\s*$",
        re.IGNORECASE,
    )
    explanation_pattern = re.compile(
        r"^Explanation\s*:\s*(.*)$",
        re.IGNORECASE,
    )

    question_lines: list[str] = []
    options: dict[str, str] = {}
    correct_answer = ""
    explanation_lines: list[str] = []
    reading_explanation = False

    for line in lines:
        if reading_explanation:
            explanation_lines.append(line)
            continue

        option_match = option_pattern.match(line)
        if option_match:
            letter = option_match.group(1).upper()
            option_text = option_match.group(2).strip()
            if letter in options:
                raise ConversionError(
                    f"DAILY MCQ {number}: duplicate option {letter}."
                )
            options[letter] = option_text
            continue

        correct_match = correct_pattern.match(line)
        if correct_match:
            correct_answer = correct_match.group(1).upper()
            continue

        explanation_match = explanation_pattern.match(line)
        if explanation_match:
            first_part = explanation_match.group(1).strip()
            if first_part:
                explanation_lines.append(first_part)
            reading_explanation = True
            continue

        question_lines.append(line)

    question = "\n".join(question_lines).strip()
    if not question:
        raise ConversionError(
            f"DAILY MCQ {number}: question cannot be empty."
        )

    expected_options = {"A", "B", "C", "D"}
    if set(options) != expected_options:
        missing_options = sorted(expected_options - set(options))
        raise ConversionError(
            f"DAILY MCQ {number}: must contain options A, B, C and D. "
            f"Missing: {', '.join(missing_options)}"
        )

    if not correct_answer:
        raise ConversionError(
            f"DAILY MCQ {number}: missing 'Correct Answer: X'."
        )

    if correct_answer not in options:
        raise ConversionError(
            f"DAILY MCQ {number}: correct answer {correct_answer} "
            "does not match an option."
        )

    explanation = " ".join(explanation_lines).strip()
    if not explanation:
        raise ConversionError(
            f"DAILY MCQ {number}: explanation cannot be empty."
        )

    return {
        "number": number,
        "question": question,
        "options": {
            "A": options["A"],
            "B": options["B"],
            "C": options["C"],
            "D": options["D"],
        },
        "correct_answer": correct_answer,
        "explanation": explanation,
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

    rating_raw = sections[
        "RATING"
    ].strip()

    rating_map = {
        "low": 2.0,
        "medium": 3.0,
        "moderate": 3.0,
        "high": 4.5,
        "very high": 5.0,
    }

    try:
        rating = float(
            rating_raw
        )

    except ValueError as exc:
        rating_key = rating_raw.casefold()

        if rating_key not in rating_map:
            raise ConversionError(
                f"Topic {topic_number}: "
                "RATING must be numeric or one of: "
                "Low, Medium, Moderate, High, Very High."
            ) from exc

        rating = rating_map[
            rating_key
        ]

    anchors = _nonempty_lines(
        sections[
            "RECALL ANCHORS"
        ]
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
        _clean(
            paragraph
        )
        for paragraph in re.split(
            r"\n\s*\n",
            sections[
                "MAINS ANSWER"
            ],
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

    concept_unfold = (
        _parse_concept_unfold(
            sections[
                "CONCEPT UNFOLD"
            ]
        )
    )

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
            sections[
                "ISSUE TITLE"
            ]
        ),
        "rating": rating,
        "editorial_sources": sources,
        "gs_mapping": (
            _parse_gs_mapping(
                sections[
                    "GS MAPPING"
                ]
            )
        ),
        "todays_question": (
            sections[
                "TODAY'S QUESTION"
            ]
        ),
        "recall_anchors": anchors,
        "knowledge_points": (
            knowledge_points
        ),
        "concept_unfold": (
            concept_unfold
        ),
        "key_takeaway": (
            sections[
                "KEY TAKEAWAY"
            ]
        ),
        "mains_question": (
            sections[
                "MAINS QUESTION"
            ]
            .rstrip()
            .rstrip(".")
            .rstrip("?")
            + "?"
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