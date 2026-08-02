from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_JSON = PROJECT_ROOT / "input_processing" / "INPUT.json"


class KnowledgeLoadError(ValueError):
    """Raised when validated knowledge data cannot be loaded safely."""


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
    recall_anchors: tuple[str, str, str, str, str]
    knowledge_points: tuple[KnowledgePointRecord, ...]
    quick_facts: tuple[str, str, str, str]
    key_takeaway: str
    mains_question: str
    mains_answer: str
    daily_mcqs: tuple[MCQRecord, ...]


def _required(mapping: dict[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        raise KnowledgeLoadError(f"{context}: missing required field '{key}'.")
    return mapping[key]


def _require_count(values: list[Any], expected: int, context: str) -> list[Any]:
    if len(values) != expected:
        raise KnowledgeLoadError(
            f"{context}: expected {expected} items, found {len(values)}."
        )
    return values


def _load_topic(raw: dict[str, Any], position: int) -> TopicRecord:
    context = f"Topic {position}"

    gs_raw = _required(raw, "gs_mapping", context)
    if not isinstance(gs_raw, dict):
        raise KnowledgeLoadError(f"{context}: gs_mapping must be an object.")

    anchors_raw = _require_count(
        list(_required(raw, "recall_anchors", context)),
        5,
        f"{context} recall anchors",
    )

    points_raw = _require_count(
        list(_required(raw, "knowledge_points", context)),
        5,
        f"{context} knowledge points",
    )
    points = tuple(
        KnowledgePointRecord(
            heading=str(_required(point, "heading", f"{context} knowledge point")),
            explanation=str(
                _required(point, "explanation", f"{context} knowledge point")
            ),
        )
        for point in points_raw
    )

    facts_raw = _require_count(
        list(_required(raw, "quick_facts", context)),
        4,
        f"{context} quick facts",
    )

    mains_raw = _required(raw, "mains_answer", context)
    if isinstance(mains_raw, dict):
        mains_answer = str(
            mains_raw.get("full_text")
            or "\n\n".join(mains_raw.get("paragraphs", []))
        ).strip()
    else:
        mains_answer = str(mains_raw).strip()

    mcqs_raw = _require_count(
        list(_required(raw, "daily_mcqs", context)),
        3,
        f"{context} MCQs",
    )
    mcqs: list[MCQRecord] = []
    for mcq_index, mcq in enumerate(mcqs_raw, start=1):
        options_raw = _required(mcq, "options", f"{context} MCQ {mcq_index}")
        if not isinstance(options_raw, dict):
            raise KnowledgeLoadError(
                f"{context} MCQ {mcq_index}: options must be an object."
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
                f"{context} MCQ {mcq_index}: options A, B, C and D are required."
            ) from exc

        mcqs.append(
            MCQRecord(
                question=str(_required(mcq, "question", f"{context} MCQ {mcq_index}")),
                options=options,
                correct_answer=str(
                    _required(mcq, "correct_answer", f"{context} MCQ {mcq_index}")
                ).upper(),
                explanation=str(
                    _required(mcq, "explanation", f"{context} MCQ {mcq_index}")
                ),
            )
        )

    sources = tuple(str(item) for item in _required(raw, "editorial_sources", context))

    return TopicRecord(
        topic_number=int(_required(raw, "topic_number", context)),
        issue_title=str(_required(raw, "issue_title", context)),
        rating=float(_required(raw, "rating", context)),
        editorial_sources=sources,
        gs_mapping=GSMapping(
            paper=str(_required(gs_raw, "paper", f"{context} GS mapping")),
            subject=str(_required(gs_raw, "subject", f"{context} GS mapping")),
            syllabus=str(_required(gs_raw, "syllabus", f"{context} GS mapping")),
        ),
        todays_question=str(_required(raw, "todays_question", context)),
        recall_anchors=tuple(str(item) for item in anchors_raw),
        knowledge_points=points,
        quick_facts=tuple(str(item) for item in facts_raw),
        key_takeaway=str(_required(raw, "key_takeaway", context)),
        mains_question=str(_required(raw, "mains_question", context)),
        mains_answer=mains_answer,
        daily_mcqs=tuple(mcqs),
    )


def load_topics(input_path: Path = INPUT_JSON) -> tuple[TopicRecord, ...]:
    try:
        raw_data = json.loads(input_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise KnowledgeLoadError(f"Input JSON not found: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise KnowledgeLoadError(
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    topics_raw = raw_data.get("topics")
    if not isinstance(topics_raw, list) or not topics_raw:
        raise KnowledgeLoadError("INPUT.json must contain a non-empty topics list.")

    return tuple(
        _load_topic(topic, position)
        for position, topic in enumerate(topics_raw, start=1)
    )