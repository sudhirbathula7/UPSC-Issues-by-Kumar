from __future__ import annotations

import re
from dataclasses import dataclass

from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from src.pdf.helpers import (
    draw_paragraph,
    paragraph_style,
)
from src.pdf.logo_loader import draw_logo
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    HEADING_BLUE,
    MAINS_LEADING,
    MAINS_QUESTION_SIZE,
    MAINS_TEXT_SIZE,
    SECTION_TITLE_SIZE,
)


@dataclass(frozen=True)
class MainsAnswerData:
    title: str
    question: str
    answer: str


# ============================================================
# SECTION HEADING
# ============================================================

def _draw_section_title(
    canvas: Canvas,
    rect: Rect,
    title: str,
) -> Rect:
    heading_height = 7 * mm

    heading_rect = Rect(
        x=rect.x + 3 * mm,
        y=rect.top - heading_height,
        width=rect.width - 6 * mm,
        height=heading_height,
    )

    icon_size = 4.2 * mm
    icon_gap = 1.2 * mm

    title_width = stringWidth(
        title,
        FONT_BOLD,
        SECTION_TITLE_SIZE,
    )

    group_width = (
        icon_size
        + icon_gap
        + title_width
    )

    group_left = (
        heading_rect.centre_x
        - group_width / 2
    )

    icon_rect = Rect(
        x=group_left,
        y=(
            heading_rect.centre_y
            - icon_size / 2
        ),
        width=icon_size,
        height=icon_size,
    )

    draw_logo(
        canvas=canvas,
        filename="mains.svg",
        rect=icon_rect,
    )

    heading_baseline = (
        heading_rect.y
        + (
            heading_rect.height
            - SECTION_TITLE_SIZE
        )
        / 2
        + 1.4
    )

    canvas.saveState()

    canvas.setFillColor(
        HEADING_BLUE,
    )

    canvas.setFont(
        FONT_BOLD,
        SECTION_TITLE_SIZE,
    )

    canvas.drawString(
        icon_rect.right + icon_gap,
        heading_baseline,
        title,
    )

    canvas.restoreState()

    return heading_rect


# ============================================================
# ANSWER PARAGRAPH HELPERS
# ============================================================

def _split_answer_into_three_paragraphs(
    answer: str,
) -> tuple[str, ...]:
    """
    Keep the rendered Mains Answer in a clean 3-paragraph structure:

    1. Introduction
    2. Main Body
    3. Conclusion

    If the incoming answer contains more than three blank-line
    separated blocks, all middle blocks are merged into one body
    paragraph. This prevents short lead-in lines from becoming a
    separate fourth paragraph.
    """
    raw = str(answer).strip()

    if not raw:
        return ()

    # Accept either real blank lines or HTML-style double breaks.
    normalised = re.sub(
        r"(?i)<br\s*/?>\s*<br\s*/?>",
        "\n\n",
        raw,
    )

    blocks = [
        re.sub(
            r"\s+",
            " ",
            block,
        ).strip()
        for block in re.split(
            r"\n\s*\n",
            normalised,
        )
        if block.strip()
    ]

    if not blocks:
        return ()

    if len(blocks) <= 3:
        return tuple(blocks)

    introduction = blocks[0]
    body = " ".join(blocks[1:-1]).strip()
    conclusion = blocks[-1]

    return (
        introduction,
        body,
        conclusion,
    )


def _draw_answer_paragraphs(
    canvas: Canvas,
    rect: Rect,
    answer: str,
) -> None:
    paragraphs = _split_answer_into_three_paragraphs(
        answer,
    )

    if not paragraphs:
        return

    answer_style = paragraph_style(
        name="MainsAnswer",
        font_name=FONT_REGULAR,
        font_size=MAINS_TEXT_SIZE + 1,
        leading=MAINS_LEADING,
        text_color=BLACK,
        alignment=TA_JUSTIFY,
    )

    # Visually similar to roughly 4–5 typed spaces, but implemented
    # as a proper first-line indent so it remains consistent.
    answer_style.firstLineIndent = 5 * mm
    answer_style.spaceBefore = 0
    answer_style.spaceAfter = 0

    paragraph_gap = 2.2 * mm

    measured: list[
        tuple[Paragraph, float]
    ] = []

    for index, text in enumerate(
        paragraphs,
        start=1,
    ):
        paragraph = Paragraph(
            text,
            answer_style,
        )

        _, height = paragraph.wrap(
            rect.width,
            1000 * mm,
        )

        measured.append(
            (
                paragraph,
                height,
            )
        )

    total_height = (
        sum(
            height
            for _, height
            in measured
        )
        + paragraph_gap
        * max(
            0,
            len(measured) - 1,
        )
    )

    # Start at the top. If an unusually long answer exceeds the box,
    # preserve all content and let the existing project word limits
    # remain the controlling constraint.
    current_top = rect.top

    for paragraph, height in measured:
        paragraph_bottom = (
            current_top
            - height
        )

        paragraph.drawOn(
            canvas,
            rect.x,
            paragraph_bottom,
        )

        current_top = (
            paragraph_bottom
            - paragraph_gap
        )


# ============================================================
# PUBLIC RENDERER
# ============================================================

def draw_mains_answer(
    canvas: Canvas,
    rect: Rect,
    data: MainsAnswerData,
) -> None:
    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    # Slightly reduced question area.
    question_height = 16 * mm

    question_rect = Rect(
        x=rect.x + 3 * mm,
        y=(
            heading_rect.y
            - question_height
            + 0.8 * mm
        ),
        width=rect.width - 6 * mm,
        height=question_height - 0.8 * mm,
    )

    question_style = paragraph_style(
        name="MainsQuestion",
        font_name=FONT_BOLD,
        font_size=MAINS_QUESTION_SIZE,
        leading=MAINS_QUESTION_SIZE + 2,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=data.question,
        rect=question_rect,
        style=question_style,
        vertical_align="middle",
    )

    # Smaller gap between question and answer.
    answer_top = (
        question_rect.y
        - 0.4 * mm
    )

    answer_rect = Rect(
        x=rect.x + 3 * mm,
        y=rect.y + 2 * mm,
        width=rect.width - 6 * mm,
        height=max(
            0,
            answer_top
            - rect.y
            - 2.4 * mm,
        ),
    )

    _draw_answer_paragraphs(
        canvas=canvas,
        rect=answer_rect,
        answer=data.answer,
    )
