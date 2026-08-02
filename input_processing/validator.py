from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


INPUT_JSON = Path(__file__).resolve().parent / "INPUT.json"


# ============================================================
# MAXIMUM CONTENT LIMITS
# ============================================================

ISSUE_TITLE_MAX_WORDS = 10
TODAYS_QUESTION_MAX_WORDS = 18

RECALL_ANCHOR_COUNT = 5
RECALL_ANCHOR_MAX_WORDS = 3

KNOWLEDGE_POINT_COUNT = 5
KNOWLEDGE_HEADING_MAX_WORDS = 4
KNOWLEDGE_EXPLANATION_MAX_WORDS = 35

QUICK_FACT_COUNT = 4
QUICK_FACT_MAX_WORDS = 30

KEY_TAKEAWAY_MAX_WORDS = 25

MAINS_PARAGRAPH_COUNT = 3
MAINS_INTRO_MAX_WORDS = 45
MAINS_CONCLUSION_MAX_WORDS = 40
MAINS_ANSWER_MAX_WORDS = 230

MCQ_COUNT = 3
MCQ_OPTION_KEYS = {"A", "B", "C", "D"}

RATING_MIN = 0.0
RATING_MAX = 5.0

SUSPICIOUS_ARTIFACTS = (
    "next",
    "continue",
    "generate next",
)


# ============================================================
# TEXT HELPERS
# ============================================================

def word_count(value: str) -> int:
    return len(
        re.findall(
            r"\b[\w’'-]+\b",
            str(value),
            flags=re.UNICODE,
        )
    )


def normalize_text(value: str) -> str:
    value = str(value).casefold()
    value = value.replace("–", "-").replace("—", "-")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def is_nonempty_string(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
    )


def add_maximum_word_error(
    errors: list[str],
    *,
    prefix: str,
    label: str,
    text: str,
    maximum: int,
) -> None:
    count = word_count(text)

    if count > maximum:
        errors.append(
            f"{prefix}: {label} contains {count} words; "
            f"maximum permitted is {maximum}."
        )


def detect_suspicious_artifact(
    errors: list[str],
    *,
    prefix: str,
    label: str,
    text: str,
) -> None:
    normalized = normalize_text(text)

    for artifact in SUSPICIOUS_ARTIFACTS:
        artifact_normalized = normalize_text(
            artifact
        )

        if (
            normalized == artifact_normalized
            or normalized.endswith(
                f" {artifact_normalized}"
            )
            or normalized.startswith(
                f"{artifact_normalized} "
            )
        ):
            errors.append(
                f"{prefix}: {label} may contain "
                f"unwanted workflow text: "
                f"'{artifact}'."
            )


def validate_unique_texts(
    errors: list[str],
    *,
    prefix: str,
    label: str,
    values: list[str],
) -> None:
    normalized_values = [
        normalize_text(value)
        for value in values
        if normalize_text(value)
    ]

    if (
        len(normalized_values)
        != len(set(normalized_values))
    ):
        errors.append(
            f"{prefix}: {label} contain "
            "duplicate content."
        )


# ============================================================
# PUBLICATION DATE
# ============================================================

def validate_publication_date(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    publication_date = str(
        data.get(
            "publication_date",
            "",
        )
    ).strip()

    publication_date_iso = str(
        data.get(
            "publication_date_iso",
            "",
        )
    ).strip()

    if not publication_date:
        errors.append(
            "publication_date is missing."
        )

    if not publication_date_iso:
        errors.append(
            "publication_date_iso is missing."
        )

    if errors:
        return errors

    try:
        display_date = datetime.strptime(
            publication_date,
            "%d %B %Y",
        )

    except ValueError:
        errors.append(
            "publication_date must use "
            "'DD Month YYYY', for example "
            "'30 July 2026'."
        )

        return errors

    try:
        iso_date = datetime.strptime(
            publication_date_iso,
            "%Y-%m-%d",
        )

    except ValueError:
        errors.append(
            "publication_date_iso must use "
            "'YYYY-MM-DD', for example "
            "'2026-07-30'."
        )

        return errors

    if (
        display_date.date()
        != iso_date.date()
    ):
        errors.append(
            "publication_date and "
            "publication_date_iso do not match."
        )

    normalized_display_date = (
        display_date.strftime(
            "%d %B %Y"
        )
    )

    if publication_date != normalized_display_date:
        errors.append(
            "publication_date must use the "
            f"normalized format "
            f"'{normalized_display_date}'."
        )

    normalized_iso_date = (
        iso_date.strftime(
            "%Y-%m-%d"
        )
    )

    if publication_date_iso != normalized_iso_date:
        errors.append(
            "publication_date_iso must use the "
            f"normalized format "
            f"'{normalized_iso_date}'."
        )

    return errors


# ============================================================
# ANCHOR REUSE
# ============================================================

def anchor_is_used(
    anchor: str,
    searchable_text: str,
) -> bool:
    normalized_anchor = normalize_text(
        anchor
    )

    normalized_content = normalize_text(
        searchable_text
    )

    if not normalized_anchor:
        return False

    if normalized_anchor in normalized_content:
        return True

    tokens = [
        token
        for token in normalized_anchor.split()
        if len(token) >= 2
    ]

    if not tokens:
        return False

    return all(
        re.search(
            rf"\b{re.escape(token)}\b",
            normalized_content,
        )
        for token in tokens
    )


def build_anchor_search_text(
    topic: dict[str, Any],
) -> str:
    sections: list[str] = []

    for point in topic.get(
        "knowledge_points",
        [],
    ):
        if isinstance(point, dict):
            sections.append(
                str(
                    point.get(
                        "heading",
                        "",
                    )
                )
            )

            sections.append(
                str(
                    point.get(
                        "explanation",
                        "",
                    )
                )
            )

    for fact in topic.get(
        "quick_facts",
        [],
    ):
        sections.append(
            str(fact)
        )

    mains_answer = topic.get(
        "mains_answer",
        {},
    )

    if isinstance(
        mains_answer,
        dict,
    ):
        sections.append(
            str(
                mains_answer.get(
                    "full_text",
                    "",
                )
            )
        )

    for mcq in topic.get(
        "daily_mcqs",
        [],
    ):
        if not isinstance(mcq, dict):
            continue

        sections.append(
            str(
                mcq.get(
                    "question",
                    "",
                )
            )
        )

        sections.append(
            str(
                mcq.get(
                    "explanation",
                    "",
                )
            )
        )

        options = mcq.get(
            "options",
            {},
        )

        if isinstance(options, dict):
            sections.extend(
                str(value)
                for value
                in options.values()
            )

    return "\n".join(
        sections
    )


# ============================================================
# GS MAPPING
# ============================================================

def validate_gs_mapping(
    mapping: Any,
    *,
    prefix: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(mapping, dict):
        return [
            f"{prefix}: gs_mapping must be "
            "a JSON object."
        ]

    required_fields = (
        "display",
        "paper",
        "subject",
        "syllabus",
    )

    for field in required_fields:
        if field not in mapping:
            errors.append(
                f"{prefix}: gs_mapping is "
                f"missing '{field}'."
            )

        elif not is_nonempty_string(
            mapping[field]
        ):
            errors.append(
                f"{prefix}: gs_mapping "
                f"'{field}' is empty."
            )

    return errors


# ============================================================
# KNOWLEDGE POINTS
# ============================================================

def validate_knowledge_points(
    points: Any,
    *,
    prefix: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(points, list):
        return [
            f"{prefix}: knowledge_points "
            "must be a list."
        ]

    if len(points) != KNOWLEDGE_POINT_COUNT:
        errors.append(
            f"{prefix}: expected "
            f"{KNOWLEDGE_POINT_COUNT} "
            f"Knowledge Points, found "
            f"{len(points)}."
        )

    headings: list[str] = []
    explanations: list[str] = []

    for index, point in enumerate(
        points,
        start=1,
    ):
        point_prefix = (
            f"{prefix}, "
            f"Knowledge Point {index}"
        )

        if not isinstance(point, dict):
            errors.append(
                f"{point_prefix}: must be "
                "a JSON object."
            )

            continue

        heading = str(
            point.get(
                "heading",
                "",
            )
        ).strip()

        explanation = str(
            point.get(
                "explanation",
                "",
            )
        ).strip()

        if not heading:
            errors.append(
                f"{point_prefix}: "
                "heading is empty."
            )

        else:
            headings.append(
                heading
            )

            add_maximum_word_error(
                errors,
                prefix=point_prefix,
                label="heading",
                text=heading,
                maximum=(
                    KNOWLEDGE_HEADING_MAX_WORDS
                ),
            )

        if not explanation:
            errors.append(
                f"{point_prefix}: "
                "explanation is empty."
            )

        else:
            explanations.append(
                explanation
            )

            add_maximum_word_error(
                errors,
                prefix=point_prefix,
                label="explanation",
                text=explanation,
                maximum=(
                    KNOWLEDGE_EXPLANATION_MAX_WORDS
                ),
            )

            detect_suspicious_artifact(
                errors,
                prefix=point_prefix,
                label="explanation",
                text=explanation,
            )

    validate_unique_texts(
        errors,
        prefix=prefix,
        label="Knowledge Point headings",
        values=headings,
    )

    validate_unique_texts(
        errors,
        prefix=prefix,
        label=(
            "Knowledge Point explanations"
        ),
        values=explanations,
    )

    return errors


# ============================================================
# QUICK FACTS
# ============================================================

def validate_quick_facts(
    facts: Any,
    *,
    prefix: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(facts, list):
        return [
            f"{prefix}: quick_facts "
            "must be a list."
        ]

    if len(facts) != QUICK_FACT_COUNT:
        errors.append(
            f"{prefix}: expected "
            f"{QUICK_FACT_COUNT} "
            f"Quick Facts, found "
            f"{len(facts)}."
        )

    valid_facts: list[str] = []

    for index, fact in enumerate(
        facts,
        start=1,
    ):
        fact_prefix = (
            f"{prefix}, "
            f"Quick Fact {index}"
        )

        if not is_nonempty_string(
            fact
        ):
            errors.append(
                f"{fact_prefix}: is empty."
            )

            continue

        fact_text = str(
            fact
        ).strip()

        valid_facts.append(
            fact_text
        )

        add_maximum_word_error(
            errors,
            prefix=fact_prefix,
            label="fact",
            text=fact_text,
            maximum=QUICK_FACT_MAX_WORDS,
        )

        detect_suspicious_artifact(
            errors,
            prefix=fact_prefix,
            label="fact",
            text=fact_text,
        )

    validate_unique_texts(
        errors,
        prefix=prefix,
        label="Quick Facts",
        values=valid_facts,
    )

    return errors


# ============================================================
# MAINS ANSWER
# ============================================================

def validate_mains_answer(
    mains_answer: Any,
    *,
    prefix: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(
        mains_answer,
        dict,
    ):
        return [
            f"{prefix}: mains_answer "
            "must be a JSON object."
        ]

    paragraphs = mains_answer.get(
        "paragraphs",
        [],
    )

    full_text = str(
        mains_answer.get(
            "full_text",
            "",
        )
    ).strip()

    if not isinstance(
        paragraphs,
        list,
    ):
        errors.append(
            f"{prefix}: Mains Answer "
            "paragraphs must be a list."
        )

        paragraphs = []

    if (
        len(paragraphs)
        != MAINS_PARAGRAPH_COUNT
    ):
        errors.append(
            f"{prefix}: Mains Answer must "
            f"contain exactly "
            f"{MAINS_PARAGRAPH_COUNT} "
            f"paragraphs; found "
            f"{len(paragraphs)}."
        )

    if not full_text:
        errors.append(
            f"{prefix}: "
            "Mains Answer is empty."
        )

        return errors

    add_maximum_word_error(
        errors,
        prefix=prefix,
        label="Mains Answer",
        text=full_text,
        maximum=MAINS_ANSWER_MAX_WORDS,
    )

    if len(paragraphs) >= 1:
        introduction = str(
            paragraphs[0]
        ).strip()

        add_maximum_word_error(
            errors,
            prefix=prefix,
            label="Mains Introduction",
            text=introduction,
            maximum=(
                MAINS_INTRO_MAX_WORDS
            ),
        )

    if len(paragraphs) >= 3:
        conclusion = str(
            paragraphs[-1]
        ).strip()

        add_maximum_word_error(
            errors,
            prefix=prefix,
            label="Mains Conclusion",
            text=conclusion,
            maximum=(
                MAINS_CONCLUSION_MAX_WORDS
            ),
        )

    detect_suspicious_artifact(
        errors,
        prefix=prefix,
        label="Mains Answer",
        text=full_text,
    )

    return errors


# ============================================================
# MCQS
# ============================================================

def validate_mcqs(
    mcqs: Any,
    *,
    prefix: str,
) -> list[str]:
    errors: list[str] = []

    if not isinstance(mcqs, list):
        return [
            f"{prefix}: daily_mcqs "
            "must be a list."
        ]

    if len(mcqs) != MCQ_COUNT:
        errors.append(
            f"{prefix}: expected "
            f"{MCQ_COUNT} MCQs, "
            f"found {len(mcqs)}."
        )

    questions: list[str] = []

    for index, mcq in enumerate(
        mcqs,
        start=1,
    ):
        mcq_prefix = (
            f"{prefix}, MCQ {index}"
        )

        if not isinstance(mcq, dict):
            errors.append(
                f"{mcq_prefix}: must be "
                "a JSON object."
            )

            continue

        question = str(
            mcq.get(
                "question",
                "",
            )
        ).strip()

        explanation = str(
            mcq.get(
                "explanation",
                "",
            )
        ).strip()

        correct_answer = str(
            mcq.get(
                "correct_answer",
                "",
            )
        ).strip().upper()

        options = mcq.get(
            "options",
            {},
        )

        if not question:
            errors.append(
                f"{mcq_prefix}: "
                "question is empty."
            )

        else:
            questions.append(
                question
            )

        if not isinstance(
            options,
            dict,
        ):
            errors.append(
                f"{mcq_prefix}: options "
                "must be a JSON object."
            )

            options = {}

        if (
            set(options.keys())
            != MCQ_OPTION_KEYS
        ):
            errors.append(
                f"{mcq_prefix}: options "
                "must contain exactly "
                "A, B, C and D."
            )

        option_values: list[str] = []

        for option_key in sorted(
            MCQ_OPTION_KEYS
        ):
            option_value = str(
                options.get(
                    option_key,
                    "",
                )
            ).strip()

            if not option_value:
                errors.append(
                    f"{mcq_prefix}: option "
                    f"{option_key} is empty."
                )

            else:
                option_values.append(
                    option_value
                )

        normalized_options = {
            normalize_text(option)
            for option in option_values
        }

        if (
            len(normalized_options)
            != len(option_values)
        ):
            errors.append(
                f"{mcq_prefix}: contains "
                "duplicate answer options."
            )

        if (
            correct_answer
            not in MCQ_OPTION_KEYS
        ):
            errors.append(
                f"{mcq_prefix}: "
                "correct_answer must be "
                "A, B, C or D."
            )

        if not explanation:
            errors.append(
                f"{mcq_prefix}: "
                "explanation is empty."
            )

    validate_unique_texts(
        errors,
        prefix=prefix,
        label="MCQ questions",
        values=questions,
    )

    return errors


# ============================================================
# COMPLETE TOPIC
# ============================================================

def validate_topic(
    topic: dict[str, Any],
    position: int,
) -> list[str]:
    errors: list[str] = []

    prefix = (
        f"Topic {position}"
    )

    required_fields = (
        "topic_number",
        "issue_title",
        "rating",
        "editorial_sources",
        "gs_mapping",
        "todays_question",
        "recall_anchors",
        "knowledge_points",
        "quick_facts",
        "key_takeaway",
        "mains_question",
        "mains_answer",
        "daily_mcqs",
    )

    missing_fields = [
        field
        for field in required_fields
        if field not in topic
    ]

    for field in missing_fields:
        errors.append(
            f"{prefix}: missing required "
            f"field '{field}'."
        )

    if missing_fields:
        return errors

    # --------------------------------------------------------
    # TOPIC NUMBER
    # --------------------------------------------------------

    if topic["topic_number"] != position:
        errors.append(
            f"{prefix}: topic_number is "
            f"{topic['topic_number']}; "
            f"expected {position}."
        )

    # --------------------------------------------------------
    # ISSUE TITLE
    # --------------------------------------------------------

    issue_title = str(
        topic["issue_title"]
    ).strip()

    if not issue_title:
        errors.append(
            f"{prefix}: "
            "Issue Title is empty."
        )

    else:
        add_maximum_word_error(
            errors,
            prefix=prefix,
            label="Issue Title",
            text=issue_title,
            maximum=ISSUE_TITLE_MAX_WORDS,
        )

    # --------------------------------------------------------
    # RATING
    # --------------------------------------------------------

    rating = topic["rating"]

    if not isinstance(
        rating,
        (int, float),
    ):
        errors.append(
            f"{prefix}: rating "
            "must be numeric."
        )

    elif not (
        RATING_MIN
        <= float(rating)
        <= RATING_MAX
    ):
        errors.append(
            f"{prefix}: rating must be "
            f"between {RATING_MIN:.1f} "
            f"and {RATING_MAX:.1f}."
        )

    elif (
        round(
            float(rating),
            1,
        )
        != float(rating)
    ):
        errors.append(
            f"{prefix}: rating must use "
            "no more than one decimal place."
        )

    # --------------------------------------------------------
    # EDITORIAL SOURCES
    # --------------------------------------------------------

    editorial_sources = topic[
        "editorial_sources"
    ]

    if not isinstance(
        editorial_sources,
        list,
    ):
        errors.append(
            f"{prefix}: editorial_sources "
            "must be a list."
        )

    elif not editorial_sources:
        errors.append(
            f"{prefix}: editorial_sources "
            "is empty."
        )

    # --------------------------------------------------------
    # GS MAPPING
    # --------------------------------------------------------

    errors.extend(
        validate_gs_mapping(
            topic["gs_mapping"],
            prefix=prefix,
        )
    )

    # --------------------------------------------------------
    # TODAY'S QUESTION
    # --------------------------------------------------------

    todays_question = str(
        topic["todays_question"]
    ).strip()

    if not todays_question:
        errors.append(
            f"{prefix}: Today's Question "
            "is empty."
        )

    else:
        add_maximum_word_error(
            errors,
            prefix=prefix,
            label="Today's Question",
            text=todays_question,
            maximum=(
                TODAYS_QUESTION_MAX_WORDS
            ),
        )

        if not todays_question.endswith(
            "?"
        ):
            errors.append(
                f"{prefix}: Today's Question "
                "must end with a question mark."
            )

    # --------------------------------------------------------
    # RECALL ANCHORS
    # --------------------------------------------------------

    anchors = topic[
        "recall_anchors"
    ]

    if not isinstance(
        anchors,
        list,
    ):
        errors.append(
            f"{prefix}: recall_anchors "
            "must be a list."
        )

        anchors = []

    if len(anchors) != RECALL_ANCHOR_COUNT:
        errors.append(
            f"{prefix}: expected "
            f"{RECALL_ANCHOR_COUNT} "
            f"Recall Anchors, found "
            f"{len(anchors)}."
        )

    valid_anchors: list[str] = []

    for index, anchor in enumerate(
        anchors,
        start=1,
    ):
        anchor_prefix = (
            f"{prefix}, "
            f"Recall Anchor {index}"
        )

        anchor_text = str(
            anchor
        ).strip()

        if not anchor_text:
            errors.append(
                f"{anchor_prefix}: is empty."
            )

            continue

        valid_anchors.append(
            anchor_text
        )

        add_maximum_word_error(
            errors,
            prefix=anchor_prefix,
            label="anchor",
            text=anchor_text,
            maximum=(
                RECALL_ANCHOR_MAX_WORDS
            ),
        )

    validate_unique_texts(
        errors,
        prefix=prefix,
        label="Recall Anchors",
        values=valid_anchors,
    )

    # --------------------------------------------------------
    # KNOWLEDGE POINTS
    # --------------------------------------------------------

    errors.extend(
        validate_knowledge_points(
            topic["knowledge_points"],
            prefix=prefix,
        )
    )

    # --------------------------------------------------------
    # QUICK FACTS
    # --------------------------------------------------------

    errors.extend(
        validate_quick_facts(
            topic["quick_facts"],
            prefix=prefix,
        )
    )

    # --------------------------------------------------------
    # KEY TAKEAWAY
    # --------------------------------------------------------

    key_takeaway = str(
        topic["key_takeaway"]
    ).strip()

    if not key_takeaway:
        errors.append(
            f"{prefix}: "
            "Key Takeaway is empty."
        )

    else:
        add_maximum_word_error(
            errors,
            prefix=prefix,
            label="Key Takeaway",
            text=key_takeaway,
            maximum=(
                KEY_TAKEAWAY_MAX_WORDS
            ),
        )

    # --------------------------------------------------------
    # MAINS QUESTION
    # --------------------------------------------------------

    mains_question = str(
        topic["mains_question"]
    ).strip()

    if not mains_question:
        errors.append(
            f"{prefix}: "
            "Mains Question is empty."
        )

    elif not mains_question.endswith(
        "?"
    ):
        errors.append(
            f"{prefix}: Mains Question "
            "must end with a question mark."
        )

    # --------------------------------------------------------
    # MAINS ANSWER
    # --------------------------------------------------------

    errors.extend(
        validate_mains_answer(
            topic["mains_answer"],
            prefix=prefix,
        )
    )

    # --------------------------------------------------------
    # MCQS
    # --------------------------------------------------------

    errors.extend(
        validate_mcqs(
            topic["daily_mcqs"],
            prefix=prefix,
        )
    )

    # --------------------------------------------------------
    # ANCHOR REUSE
    # --------------------------------------------------------

    anchor_search_text = (
        build_anchor_search_text(
            topic
        )
    )

    for index, anchor in enumerate(
        valid_anchors,
        start=1,
    ):
        if not anchor_is_used(
            anchor,
            anchor_search_text,
        ):
            errors.append(
                f"{prefix}: Recall Anchor "
                f"{index} ('{anchor}') is not "
                "meaningfully reused in the "
                "Knowledge Points, Quick Facts, "
                "Mains Answer or MCQs."
            )

    return errors


# ============================================================
# COMPLETE JSON
# ============================================================

def validate_data(
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return [
            "INPUT.json root must be "
            "a JSON object."
        ]

    if (
        data.get("schema_version")
        != "2.0"
    ):
        errors.append(
            "schema_version must be '2.0'."
        )

    errors.extend(
        validate_publication_date(
            data
        )
    )

    topics = data.get(
        "topics"
    )

    if (
        not isinstance(topics, list)
        or not topics
    ):
        return [
            "INPUT.json must contain "
            "a non-empty 'topics' list."
        ]

    if (
        data.get("topic_count")
        != len(topics)
    ):
        errors.append(
            f"topic_count is "
            f"{data.get('topic_count')}, "
            f"but {len(topics)} topics exist."
        )

    topic_numbers: list[int] = []
    issue_titles: list[str] = []

    for position, topic in enumerate(
        topics,
        start=1,
    ):
        if not isinstance(
            topic,
            dict,
        ):
            errors.append(
                f"Topic {position}: must be "
                "a JSON object."
            )

            continue

        topic_number = topic.get(
            "topic_number"
        )

        if isinstance(
            topic_number,
            int,
        ):
            topic_numbers.append(
                topic_number
            )

        issue_titles.append(
            str(
                topic.get(
                    "issue_title",
                    "",
                )
            ).strip()
        )

        errors.extend(
            validate_topic(
                topic,
                position,
            )
        )

    if (
        len(topic_numbers)
        != len(set(topic_numbers))
    ):
        errors.append(
            "Topic numbers contain duplicates."
        )

    validate_unique_texts(
        errors,
        prefix="INPUT.json",
        label="Issue Titles",
        values=issue_titles,
    )

    return errors


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_file(
    path: Path = INPUT_JSON,
) -> list[str]:
    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8-sig",
            )
        )

    except FileNotFoundError:
        return [
            f"File not found: {path}"
        ]

    except json.JSONDecodeError as exc:
        return [
            f"Invalid JSON at line "
            f"{exc.lineno}, column "
            f"{exc.colno}: {exc.msg}"
        ]

    except OSError as exc:
        return [
            f"Unable to read {path}: {exc}"
        ]

    return validate_data(
        data
    )


# ============================================================
# COMMAND LINE
# ============================================================

def main() -> int:
    errors = validate_file()

    if errors:
        print("=" * 72)
        print(
            "INPUT VALIDATION FAILED"
        )
        print("=" * 72)
        print(
            f"Total errors: {len(errors)}"
        )
        print()

        for index, error in enumerate(
            errors,
            start=1,
        ):
            print(
                f"{index}. {error}"
            )

        print()
        print("=" * 72)

        return 1

    print("=" * 72)
    print(
        "INPUT VALIDATION PASSED"
    )
    print("=" * 72)
    print(
        f"Validated: {INPUT_JSON}"
    )
    print("=" * 72)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )