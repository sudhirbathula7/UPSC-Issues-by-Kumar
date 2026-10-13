import json
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_JSON_PATH = PROJECT_ROOT / "input_processing" / "INPUT.json"


class ValidationError:
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message


# ============================================================
# HELPERS
# ============================================================

def _is_nonempty(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
    )


def _normalise_text(value: str) -> str:
    value = value.lower()

    value = re.sub(
        r"[^a-z0-9\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def _meaningfully_reused(
    anchor: str,
    topic: dict[str, Any],
) -> bool:
    """
    Check whether a Recall Anchor is meaningfully reused
    somewhere in the topic's learning content.

    Recall Anchors are currently retained as internal
    highlighting terms. Their visible PDF display will
    be removed separately.

    Searchable content includes:
    - Knowledge Points
    - Concept Unfold
    - Mains Answer
    - Daily MCQs
    """

    anchor_words = {
        word
        for word in _normalise_text(anchor).split()
        if len(word) > 2
    }

    if not anchor_words:
        return True

    searchable_parts: list[str] = []

    # --------------------------------------------------------
    # KNOWLEDGE POINTS
    # --------------------------------------------------------

    for point in topic.get(
        "knowledge_points",
        [],
    ):
        if not isinstance(
            point,
            dict,
        ):
            continue

        searchable_parts.extend(
            [
                str(
                    point.get(
                        "heading",
                        "",
                    )
                ),
                str(
                    point.get(
                        "explanation",
                        "",
                    )
                ),
            ]
        )

    # --------------------------------------------------------
    # CONCEPT UNFOLD
    # --------------------------------------------------------

    concept_unfold = topic.get(
        "concept_unfold",
        {},
    )

    if isinstance(
        concept_unfold,
        dict,
    ):
        searchable_parts.append(
            str(
                concept_unfold.get(
                    "concept",
                    "",
                )
            )
        )

        consequences = concept_unfold.get(
            "consequences",
            [],
        )

        if isinstance(
            consequences,
            list,
        ):
            for consequence in consequences:

                if not isinstance(
                    consequence,
                    dict,
                ):
                    continue

                searchable_parts.extend(
                    [
                        str(
                            consequence.get(
                                "title",
                                "",
                            )
                        ),
                        str(
                            consequence.get(
                                "explanation",
                                "",
                            )
                        ),
                    ]
                )

    # --------------------------------------------------------
    # MAINS ANSWER
    # --------------------------------------------------------

    mains_answer = topic.get(
        "mains_answer",
        {},
    )

    if isinstance(
        mains_answer,
        dict,
    ):
        searchable_parts.append(
            str(
                mains_answer.get(
                    "full_text",
                    "",
                )
            )
        )

        paragraphs = mains_answer.get(
            "paragraphs",
            [],
        )

        if isinstance(
            paragraphs,
            list,
        ):
            searchable_parts.extend(
                str(item)
                for item in paragraphs
            )

    elif isinstance(
        mains_answer,
        str,
    ):
        searchable_parts.append(
            mains_answer
        )

    # --------------------------------------------------------
    # DAILY MCQs
    # --------------------------------------------------------

    for mcq in topic.get(
        "daily_mcqs",
        [],
    ):
        if not isinstance(
            mcq,
            dict,
        ):
            continue

        searchable_parts.append(
            str(
                mcq.get(
                    "question",
                    "",
                )
            )
        )

        searchable_parts.append(
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

        if isinstance(
            options,
            dict,
        ):
            searchable_parts.extend(
                str(value)
                for value in options.values()
            )

    # --------------------------------------------------------
    # COMBINE SEARCHABLE CONTENT
    # --------------------------------------------------------

    searchable_text = _normalise_text(
        " ".join(searchable_parts)
    )

    searchable_words = set(
        searchable_text.split()
    )

    # An anchor is considered meaningfully reused when
    # at least one substantive word from the anchor appears
    # somewhere in the learning content.
    return any(
        word in searchable_words
        for word in anchor_words
    )

# ============================================================
# BASIC FIELD VALIDATION
# ============================================================

def _validate_required_string(
    topic_number: int,
    topic: dict[str, Any],
    field: str,
    errors: list[str],
) -> None:

    value = topic.get(field)

    if not _is_nonempty(value):
        errors.append(
            f"Topic {topic_number}: "
            f"{field.replace('_', ' ').title()} is empty."
        )


# ============================================================
# KNOWLEDGE POINT VALIDATION
# ============================================================

def _validate_knowledge_points(
    topic_number: int,
    topic: dict[str, Any],
    errors: list[str],
) -> None:

    knowledge_points = topic.get(
        "knowledge_points"
    )

    if not isinstance(
        knowledge_points,
        list,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Knowledge Points must be a list."
        )
        return

    if len(knowledge_points) != 5:
        errors.append(
            f"Topic {topic_number}: expected "
            f"5 Knowledge Points, found "
            f"{len(knowledge_points)}."
        )

    for index, point in enumerate(
        knowledge_points,
        start=1,
    ):

        if not isinstance(
            point,
            dict,
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Knowledge Point {index}: "
                "must be an object."
            )
            continue

        heading = point.get(
            "heading"
        )

        explanation = point.get(
            "explanation"
        )

        if not _is_nonempty(
            heading
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Knowledge Point {index}: "
                "heading is empty."
            )

        if not _is_nonempty(
            explanation
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Knowledge Point {index}: "
                "explanation is empty."
            )


# ============================================================
# CONCEPT UNFOLD VALIDATION
# ============================================================

def _validate_concept_unfold(
    topic_number: int,
    topic: dict[str, Any],
    errors: list[str],
) -> None:
    """
    Validate the selected Concept Unfold.

    Expected structure:

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

    Concept Unfold contains:

        1 basic UPSC concept
                ↓
        Consequence 1
                ↓
        Consequence 2
                ↓
        Consequence 3

    Exactly three consequences are required.
    """

    concept_unfold = topic.get(
        "concept_unfold"
    )

    # --------------------------------------------------------
    # ROOT STRUCTURE
    # --------------------------------------------------------

    if not isinstance(
        concept_unfold,
        dict,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Concept Unfold must be an object."
        )
        return

    # --------------------------------------------------------
    # CONCEPT
    # --------------------------------------------------------

    concept = concept_unfold.get(
        "concept"
    )

    if not _is_nonempty(
        concept
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Concept Unfold concept is empty."
        )

    # --------------------------------------------------------
    # CONSEQUENCES
    # --------------------------------------------------------

    consequences = concept_unfold.get(
        "consequences"
    )

    if not isinstance(
        consequences,
        list,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Concept Unfold consequences "
            "must be a list."
        )
        return

    if len(consequences) != 3:
        errors.append(
            f"Topic {topic_number}: "
            "Concept Unfold must contain exactly "
            f"3 consequences, found "
            f"{len(consequences)}."
        )

    # --------------------------------------------------------
    # INDIVIDUAL CONSEQUENCE VALIDATION
    # --------------------------------------------------------

    consequence_titles: list[str] = []

    for index, consequence in enumerate(
        consequences,
        start=1,
    ):

        if not isinstance(
            consequence,
            dict,
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Concept Unfold Consequence {index}: "
                "must be an object."
            )
            continue

        title = consequence.get(
            "title"
        )

        explanation = consequence.get(
            "explanation"
        )

        if not _is_nonempty(
            title
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Concept Unfold Consequence {index}: "
                "title is empty."
            )

        else:
            consequence_titles.append(
                title.strip().casefold()
            )

        if not _is_nonempty(
            explanation
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Concept Unfold Consequence {index}: "
                "explanation is empty."
            )

    # --------------------------------------------------------
    # DUPLICATE CONSEQUENCE CHECK
    # --------------------------------------------------------

    if (
        len(consequence_titles)
        != len(set(consequence_titles))
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Concept Unfold consequence titles "
            "must all be different."
        )

# ============================================================
# MCQ VALIDATION
# ============================================================

def _validate_mcqs(
    topic_number: int,
    topic: dict[str, Any],
    errors: list[str],
) -> None:

    mcqs = topic.get(
        "daily_mcqs"
    )

    if not isinstance(
        mcqs,
        list,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Daily MCQs must be a list."
        )
        return

    if len(mcqs) != 3:
        errors.append(
            f"Topic {topic_number}: expected "
            f"3 Daily MCQs, found "
            f"{len(mcqs)}."
        )

    for index, mcq in enumerate(
        mcqs,
        start=1,
    ):

        if not isinstance(
            mcq,
            dict,
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Daily MCQ {index}: "
                "must be an object."
            )
            continue

        question = mcq.get(
            "question"
        )

        options = mcq.get(
            "options"
        )

        answer = mcq.get(
            "correct_answer"
        )

        explanation = mcq.get(
            "explanation"
        )

        if not _is_nonempty(
            question
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Daily MCQ {index}: "
                "question is empty."
            )

        if not isinstance(
            options,
            dict,
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Daily MCQ {index}: "
                "options must be an object."
            )
        else:
            expected_options = {
                "A",
                "B",
                "C",
                "D",
            }

            actual_options = set(
                options.keys()
            )

            if actual_options != expected_options:
                errors.append(
                    f"Topic {topic_number}, "
                    f"Daily MCQ {index}: "
                    "must contain exactly "
                    "A, B, C and D options."
                )

            for letter in (
                "A",
                "B",
                "C",
                "D",
            ):
                if letter in options and not _is_nonempty(
                    options[letter]
                ):
                    errors.append(
                        f"Topic {topic_number}, "
                        f"Daily MCQ {index}, "
                        f"Option {letter}: "
                        "is empty."
                    )

        if answer not in {
            "A",
            "B",
            "C",
            "D",
        }:
            errors.append(
                f"Topic {topic_number}, "
                f"Daily MCQ {index}: "
                "Correct Answer must be A, B, C or D."
            )

        if not _is_nonempty(
            explanation
        ):
            errors.append(
                f"Topic {topic_number}, "
                f"Daily MCQ {index}: "
                "explanation is empty."
            )


# ============================================================
# TOPIC VALIDATION
# ============================================================

def _validate_topic(
    topic_number: int,
    topic: dict[str, Any],
) -> list[str]:

    errors: list[str] = []

    required_fields = [
        "issue_title",
        "rating",
        "editorial_sources",
        "gs_mapping",
        "todays_question",
        "recall_anchors",
        "knowledge_points",
        "concept_unfold",
        "key_takeaway",
        "mains_question",
        "mains_answer",
        "daily_mcqs",
    ]

    for field in required_fields:

        if field not in topic:
            errors.append(
                f"Topic {topic_number}: "
                f"missing field '{field}'."
            )

    _validate_required_string(
        topic_number,
        topic,
        "issue_title",
        errors,
    )

    _validate_required_string(
        topic_number,
        topic,
        "todays_question",
        errors,
    )

    _validate_required_string(
        topic_number,
        topic,
        "key_takeaway",
        errors,
    )

    _validate_required_string(
        topic_number,
        topic,
        "mains_question",
        errors,
    )

    # --------------------------------------------------------
    # Rating
    # --------------------------------------------------------

    rating = topic.get(
        "rating"
    )

    if not isinstance(
        rating,
        (int, float),
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Rating must be numeric."
        )

    elif not (
        1 <= float(rating) <= 5
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Rating must be between 1 and 5."
        )

    # --------------------------------------------------------
    # GS Mapping
    # --------------------------------------------------------

    gs_mapping = topic.get(
        "gs_mapping"
    )

    if not isinstance(
        gs_mapping,
        dict,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "GS Mapping must be an object."
        )
    else:
        for field in (
            "display",
            "paper",
            "subject",
            "syllabus",
        ):
            if not _is_nonempty(
                gs_mapping.get(field)
            ):
                errors.append(
                    f"Topic {topic_number}: "
                    f"GS Mapping {field} is empty."
                )

    # --------------------------------------------------------
    # Recall Anchors
    # --------------------------------------------------------

    anchors = topic.get(
        "recall_anchors"
    )

    if not isinstance(
        anchors,
        list,
    ):
        errors.append(
            f"Topic {topic_number}: "
            "Recall Anchors must be a list."
        )

    else:

        if len(anchors) == 0:
            errors.append(
                f"Topic {topic_number}: "
                "Recall Anchors cannot be empty."
            )

        for index, anchor in enumerate(
            anchors,
            start=1,
        ):

            if not _is_nonempty(
                anchor
            ):
                errors.append(
                    f"Topic {topic_number}: "
                    f"Recall Anchor {index} "
                    "is empty."
                )
                continue

            if not _meaningfully_reused(
                anchor,
                topic,
            ):
                errors.append(
                    f"Topic {topic_number}: "
                    f"Recall Anchor {index} "
                    f"('{anchor}') is not meaningfully "
                    "reused in the Knowledge Points, "
                    "Concept Unfold, Mains Answer "
                    "or MCQs."
                )

    # --------------------------------------------------------
    # Knowledge Points
    # --------------------------------------------------------

    _validate_knowledge_points(
        topic_number,
        topic,
        errors,
    )

    # --------------------------------------------------------
    # Concept Unfold
    # --------------------------------------------------------

    _validate_concept_unfold(
        topic_number,
        topic,
        errors,
    )

    # --------------------------------------------------------
    # MCQs
    # --------------------------------------------------------

    _validate_mcqs(
        topic_number,
        topic,
        errors,
    )

    return errors


# ============================================================
# COMPLETE VALIDATION
# ============================================================

def validate_data(
    data: dict[str, Any],
) -> list[str]:

    errors: list[str] = []

    if not isinstance(
        data,
        dict,
    ):
        return [
            "Root JSON must be an object."
        ]

    topics = data.get(
        "topics"
    )

    if not isinstance(
        topics,
        list,
    ):
        return [
            "Root field 'topics' must be a list."
        ]

    if len(topics) == 0:
        errors.append(
            "No topics found."
        )
        return errors

    topic_numbers: set[int] = set()

    for position, topic in enumerate(
        topics,
        start=1,
    ):

        if not isinstance(
            topic,
            dict,
        ):
            errors.append(
                f"Topic position {position}: "
                "must be an object."
            )
            continue

        topic_number = topic.get(
            "topic_number"
        )

        if not isinstance(
            topic_number,
            int,
        ):
            errors.append(
                f"Topic position {position}: "
                "topic_number must be an integer."
            )
            continue

        if topic_number in topic_numbers:
            errors.append(
                f"Duplicate topic number: "
                f"{topic_number}."
            )

        topic_numbers.add(
            topic_number
        )

        errors.extend(
            _validate_topic(
                topic_number,
                topic,
            )
        )

    return errors


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_file(
    input_path: Path = INPUT_JSON_PATH,
) -> bool:

    print()
    print(
        "=" * 72
    )
    print(
        "VALIDATING INPUT.json"
    )
    print(
        "=" * 72
    )

    if not input_path.exists():
        print(
            f"ERROR: File not found: "
            f"{input_path}"
        )
        return False

    try:
        with input_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(
                file
            )

    except json.JSONDecodeError as exc:
        print(
            "ERROR: INPUT.json contains invalid JSON."
        )

        print(
            f"Line {exc.lineno}, "
            f"column {exc.colno}: "
            f"{exc.msg}"
        )

        return False

    except OSError as exc:
        print(
            f"ERROR: Could not read INPUT.json: "
            f"{exc}"
        )

        return False

    errors = validate_data(
        data
    )

    if errors:

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

        return False

    topic_count = len(
        data.get(
            "topics",
            [],
        )
    )

    print(
        "INPUT.json validation PASSED."
    )

    print(
        f"Topics validated: {topic_count}"
    )

    print(
        "Concept Unfold: 1 per topic"
    )

    print(
        "Quick Facts validation: REMOVED"
    )

    print()

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    success = validate_file()

    if success:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )