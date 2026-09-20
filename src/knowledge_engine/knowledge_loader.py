from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_JSON = PROJECT_ROOT / "input_processing" / "INPUT.json"


class KnowledgeLoadError(ValueError):
    """Raised when validated knowledge data cannot be loaded safely."""


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class GSMapping:
    paper: str
    subject: str
    syllabus: str


@dataclass(frozen=True)
class KnowledgePointRecord:
    heading: str
    explanation: str


@dataclass(frozen=True)
class ConceptUnfoldConsequence:
    title: str
    explanation: str


@dataclass(frozen=True)
class ConceptUnfoldRecord:
    concept: str
    consequences: tuple[
        ConceptUnfoldConsequence,
        ConceptUnfoldConsequence,
    ]


@dataclass(frozen=True)
class MCQRecord:
    question: str
    options: tuple[str, str, str, str]
    correct_answer: str
    explanation: str


@dataclass(frozen=True)
class TopicRecord:
    topic_number: int
    issue_title: str
    rating: float
    editorial_sources: tuple[str, ...]
    gs_mapping: GSMapping
    todays_question: str
    recall_anchors: tuple[
        str,
        str,
        str,
        str,
        str,
    ]
    knowledge_points: tuple[
        KnowledgePointRecord,
        ...
    ]
    concept_unfold: ConceptUnfoldRecord
    key_takeaway: str
    mains_question: str
    mains_answer: str
    daily_mcqs: tuple[
        MCQRecord,
        ...
    ]

# ============================================================
# HELPERS
# ============================================================

def _required(
    mapping: dict[str, Any],
    key: str,
    context: str,
) -> Any:
    if key not in mapping:
        raise KnowledgeLoadError(
            f"{context}: missing required field '{key}'."
        )

    return mapping[key]


def _require_count(
    values: list[Any],
    expected: int,
    context: str,
) -> list[Any]:
    if len(values) != expected:
        raise KnowledgeLoadError(
            f"{context}: expected {expected} items, found {len(values)}."
        )

    return values


# ============================================================
# CONCEPT UNFOLD
# ============================================================

def _load_concept_unfold(
    raw_concept_unfold: Any,
    context: str,
) -> ConceptUnfoldRecord:
    """
    Load one selected Concept Unfold.

    Expected JSON structure:

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

    Exactly one concept and three consequences are required.
    """

    # --------------------------------------------------------
    # ROOT STRUCTURE
    # --------------------------------------------------------

    if not isinstance(
        raw_concept_unfold,
        dict,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "concept_unfold must be an object."
        )

    # --------------------------------------------------------
    # CONCEPT
    # --------------------------------------------------------

    concept = str(
        _required(
            raw_concept_unfold,
            "concept",
            f"{context} concept unfold",
        )
    ).strip()

    if not concept:
        raise KnowledgeLoadError(
            f"{context}: "
            "concept unfold concept cannot be empty."
        )

    # --------------------------------------------------------
    # CONSEQUENCES
    # --------------------------------------------------------

    consequences_raw = _required(
        raw_concept_unfold,
        "consequences",
        f"{context} concept unfold",
    )

    if not isinstance(
        consequences_raw,
        list,
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "concept unfold consequences must be a list."
        )

    consequences_raw = _require_count(
        consequences_raw,
        3,
        f"{context} concept unfold consequences",
    )

    consequences: list[
        ConceptUnfoldConsequence
    ] = []

    # --------------------------------------------------------
    # INDIVIDUAL CONSEQUENCES
    # --------------------------------------------------------

    for consequence_index, consequence in enumerate(
        consequences_raw,
        start=1,
    ):
        consequence_context = (
            f"{context} concept unfold "
            f"consequence {consequence_index}"
        )

        if not isinstance(
            consequence,
            dict,
        ):
            raise KnowledgeLoadError(
                f"{consequence_context}: "
                "must be an object."
            )

        title = str(
            _required(
                consequence,
                "title",
                consequence_context,
            )
        ).strip()

        explanation = str(
            _required(
                consequence,
                "explanation",
                consequence_context,
            )
        ).strip()

        if not title:
            raise KnowledgeLoadError(
                f"{consequence_context}: "
                "title cannot be empty."
            )

        if not explanation:
            raise KnowledgeLoadError(
                f"{consequence_context}: "
                "explanation cannot be empty."
            )

        consequences.append(
            ConceptUnfoldConsequence(
                title=title,
                explanation=explanation,
            )
        )

    # --------------------------------------------------------
    # DUPLICATE CONSEQUENCE CHECK
    # --------------------------------------------------------

    consequence_titles = [
        consequence.title.casefold()
        for consequence in consequences
    ]

    if (
        len(consequence_titles)
        != len(set(consequence_titles))
    ):
        raise KnowledgeLoadError(
            f"{context}: "
            "concept unfold consequence titles "
            "must all be different."
        )

    # --------------------------------------------------------
    # FINAL RECORD
    # --------------------------------------------------------

    return ConceptUnfoldRecord(
        concept=concept,
        consequences=(
            consequences[0],
            consequences[1],
            consequences[2],
        ),
    )

# ============================================================
# TOPIC LOADER
# ============================================================

def _load_topic(
    raw: dict[str, Any],
    position: int,
) -> TopicRecord:
    context = f"Topic {position}"

    # --------------------------------------------------------
    # GS MAPPING
    # --------------------------------------------------------

    gs_raw = _required(
        raw,
        "gs_mapping",
        context,
    )

    if not isinstance(gs_raw, dict):
        raise KnowledgeLoadError(
            f"{context}: gs_mapping must be an object."
        )

    # --------------------------------------------------------
    # RECALL ANCHORS
    # --------------------------------------------------------

    anchors_raw = _require_count(
        list(
            _required(
                raw,
                "recall_anchors",
                context,
            )
        ),
        5,
        f"{context} recall anchors",
    )

    # --------------------------------------------------------
    # KNOWLEDGE POINTS
    # --------------------------------------------------------

    points_raw = _require_count(
        list(
            _required(
                raw,
                "knowledge_points",
                context,
            )
        ),
        5,
        f"{context} knowledge points",
    )

    points = tuple(
        KnowledgePointRecord(
            heading=str(
                _required(
                    point,
                    "heading",
                    f"{context} knowledge point",
                )
            ),
            explanation=str(
                _required(
                    point,
                    "explanation",
                    f"{context} knowledge point",
                )
            ),
        )
        for point in points_raw
    )

    # --------------------------------------------------------
    # CONCEPT UNFOLD
    # --------------------------------------------------------

    concept_unfold = _load_concept_unfold(
        _required(
            raw,
            "concept_unfold",
            context,
        ),
        context,
    )

    # --------------------------------------------------------
    # MAINS ANSWER
    # --------------------------------------------------------

    mains_raw = _required(
        raw,
        "mains_answer",
        context,
    )

    if isinstance(mains_raw, dict):
        mains_answer = str(
            mains_raw.get("full_text")
            or "\n\n".join(
                mains_raw.get(
                    "paragraphs",
                    [],
                )
            )
        ).strip()
    else:
        mains_answer = str(
            mains_raw
        ).strip()

    # --------------------------------------------------------
    # MCQs
    # --------------------------------------------------------

    mcqs_raw = _require_count(
        list(
            _required(
                raw,
                "daily_mcqs",
                context,
            )
        ),
        3,
        f"{context} MCQs",
    )

    mcqs: list[MCQRecord] = []

    for mcq_index, mcq in enumerate(
        mcqs_raw,
        start=1,
    ):
        mcq_context = (
            f"{context} MCQ {mcq_index}"
        )

        options_raw = _required(
            mcq,
            "options",
            mcq_context,
        )

        if not isinstance(
            options_raw,
            dict,
        ):
            raise KnowledgeLoadError(
                f"{mcq_context}: options must be an object."
            )

        try:
            options = (
                str(options_raw["A"]),
                str(options_raw["B"]),
                str(options_raw["C"]),
                str(options_raw["D"]),
            )
        except KeyError as exc:
            raise KnowledgeLoadError(
                f"{mcq_context}: options A, B, C and D are required."
            ) from exc

        mcqs.append(
            MCQRecord(
                question=str(
                    _required(
                        mcq,
                        "question",
                        mcq_context,
                    )
                ),
                options=options,
                correct_answer=str(
                    _required(
                        mcq,
                        "correct_answer",
                        mcq_context,
                    )
                ).upper(),
                explanation=str(
                    _required(
                        mcq,
                        "explanation",
                        mcq_context,
                    )
                ),
            )
        )

    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    sources = tuple(
        str(item)
        for item in _required(
            raw,
            "editorial_sources",
            context,
        )
    )

    # --------------------------------------------------------
    # FINAL TOPIC RECORD
    # --------------------------------------------------------

    return TopicRecord(
        topic_number=int(
            _required(
                raw,
                "topic_number",
                context,
            )
        ),
        issue_title=str(
            _required(
                raw,
                "issue_title",
                context,
            )
        ),
        rating=float(
            _required(
                raw,
                "rating",
                context,
            )
        ),
        editorial_sources=sources,
        gs_mapping=GSMapping(
            paper=str(
                _required(
                    gs_raw,
                    "paper",
                    f"{context} GS mapping",
                )
            ),
            subject=str(
                _required(
                    gs_raw,
                    "subject",
                    f"{context} GS mapping",
                )
            ),
            syllabus=str(
                _required(
                    gs_raw,
                    "syllabus",
                    f"{context} GS mapping",
                )
            ),
        ),
        todays_question=str(
            _required(
                raw,
                "todays_question",
                context,
            )
        ),
        recall_anchors=tuple(
            str(item)
            for item in anchors_raw
        ),
        knowledge_points=points,
        concept_unfold=concept_unfold,
        key_takeaway=str(
            _required(
                raw,
                "key_takeaway",
                context,
            )
        ),
        mains_question=str(
            _required(
                raw,
                "mains_question",
                context,
            )
        ),
        mains_answer=mains_answer,
        daily_mcqs=tuple(mcqs),
    )


# ============================================================
# PUBLIC LOADER
# ============================================================

def load_topics(
    input_path: Path = INPUT_JSON,
) -> tuple[TopicRecord, ...]:

    try:
        raw_data = json.loads(
            input_path.read_text(
                encoding="utf-8-sig"
            )
        )

    except FileNotFoundError as exc:
        raise KnowledgeLoadError(
            f"Input JSON not found: {input_path}"
        ) from exc

    except json.JSONDecodeError as exc:
        raise KnowledgeLoadError(
            f"Invalid JSON at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}"
        ) from exc

    topics_raw = raw_data.get("topics")

    if (
        not isinstance(
            topics_raw,
            list,
        )
        or not topics_raw
    ):
        raise KnowledgeLoadError(
            "INPUT.json must contain a non-empty topics list."
        )

    return tuple(
        _load_topic(
            topic,
            position,
        )
        for position, topic in enumerate(
            topics_raw,
            start=1,
        )
    )