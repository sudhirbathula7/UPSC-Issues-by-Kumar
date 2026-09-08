from __future__ import annotations

import re
from collections.abc import Iterable


def _normalise_anchors(
    anchors: Iterable[str] | str | None,
) -> tuple[str, ...]:
    """Convert Recall Anchors into a clean tuple."""
    if anchors is None:
        return ()

    if isinstance(anchors, str):
        values = re.split(
            r"\s*(?:•|\||;|\n)\s*",
            anchors,
        )
    else:
        values = [
            str(anchor)
            for anchor in anchors
        ]

    cleaned: list[str] = []
    seen: set[str] = set()

    for value in values:
        anchor = value.strip()

        if not anchor:
            continue

        key = anchor.casefold()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(anchor)

    cleaned.sort(
        key=len,
        reverse=True,
    )

    return tuple(cleaned)


def bold_recall_anchors(
    text: str,
    anchors: Iterable[str] | str | None,
) -> str:
    """
    Make exact Recall Anchor phrases bold-italic.

    Matching is case-insensitive while preserving the original
    capitalisation found in the content.
    """
    if not text:
        return text

    clean_anchors = _normalise_anchors(
        anchors
    )

    if not clean_anchors:
        return text

    pattern = re.compile(
        "|".join(
            re.escape(anchor)
            for anchor in clean_anchors
        ),
        flags=re.IGNORECASE,
    )

    return pattern.sub(
        lambda match: (
            f"<b><i>{match.group(0)}</i></b>"
        ),
        text,
    )


def bold_knowledge_heading(
    heading: str,
) -> str:
    """
    Add italic emphasis to a Knowledge Point heading.

    knowledge_points.py already wraps every Knowledge Point
    heading in <b>...</b>. Returning italic markup here makes
    Pro headings bold-italic while Normal headings remain bold.
    """
    if not heading:
        return heading

    return f"<i>{heading}</i>"


def bold_italic_text(
    text: str,
) -> str:
    """Make an entire Pro-only text block bold-italic."""
    if not text:
        return text

    return f"<b><i>{text}</i></b>"
