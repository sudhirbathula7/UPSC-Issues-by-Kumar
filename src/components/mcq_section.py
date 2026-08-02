from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from src.pdf.helpers import paragraph_style
from src.pdf.logo_loader import draw_logo
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    HEADING_BLUE,
    MCQ_LEADING,
    MCQ_OPTION_SIZE,
    MCQ_QUESTION_SIZE,
    SECTION_TITLE_SIZE,
)


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class MCQ:
    question: str
    options: tuple[str, str, str, str]
    correct_option: str | None = None
    explanation: str | None = None


@dataclass(frozen=True)
class MCQData:
    title: str
    questions: tuple[MCQ, ...]


@dataclass(frozen=True)
class _MeasuredMCQ:
    paragraph: Paragraph
    height: float
    leading: float


# ============================================================
# SECTION TITLE
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
        filename="mcqs.svg",
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
# MCQ TEXT
# ============================================================

def _build_mcq_text(
    mcq: MCQ,
    question_size: float,
) -> str:
    return (
        f"<font name='{FONT_BOLD}' "
        f"size='{question_size}'>"
        f"{mcq.question}"
        f"</font>"
        f"<br/><br/>"
        f"A. {mcq.options[0]}"
        f"<br/>"
        f"B. {mcq.options[1]}"
        f"<br/>"
        f"C. {mcq.options[2]}"
        f"<br/>"
        f"D. {mcq.options[3]}"
    )


def _build_mcq_paragraph(
    mcq: MCQ,
    index: int,
    *,
    question_size: float,
    option_size: float,
    leading: float,
) -> Paragraph:
    style = paragraph_style(
        name=f"MCQBlock{index}",
        font_name=FONT_REGULAR,
        font_size=option_size,
        leading=leading,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    style.spaceBefore = 0
    style.spaceAfter = 0

    return Paragraph(
        _build_mcq_text(
            mcq=mcq,
            question_size=question_size,
        ),
        style,
    )


# ============================================================
# MEASUREMENT
# ============================================================

def _measure_questions(
    questions: tuple[MCQ, ...],
    *,
    text_width: float,
    question_size: float,
    option_size: float,
    leading: float,
) -> tuple[_MeasuredMCQ, ...]:
    measured: list[_MeasuredMCQ] = []

    for index, mcq in enumerate(
        questions,
        start=1,
    ):
        paragraph = _build_mcq_paragraph(
            mcq=mcq,
            index=index,
            question_size=question_size,
            option_size=option_size,
            leading=leading,
        )

        _, paragraph_height = paragraph.wrap(
            text_width,
            1000 * mm,
        )

        measured.append(
            _MeasuredMCQ(
                paragraph=paragraph,
                height=paragraph_height,
                leading=leading,
            )
        )

    return tuple(measured)


def _select_text_sizes(
    questions: tuple[MCQ, ...],
    *,
    text_width: float,
    available_height: float,
    minimum_gap: float,
) -> tuple[
    float,
    float,
    float,
    tuple[_MeasuredMCQ, ...],
]:
    question_size = float(
        MCQ_QUESTION_SIZE
    )

    option_size = float(
        MCQ_OPTION_SIZE
    )

    original_option_size = max(
        float(MCQ_OPTION_SIZE),
        0.1,
    )

    leading_ratio = (
        float(MCQ_LEADING)
        / original_option_size
    )

    minimum_question_size = 6.2
    minimum_option_size = 5.8

    while (
        question_size >= minimum_question_size
        and option_size >= minimum_option_size
    ):
        leading = max(
            option_size * leading_ratio,
            option_size + 1.1,
        )

        measured = _measure_questions(
            questions=questions,
            text_width=text_width,
            question_size=question_size,
            option_size=option_size,
            leading=leading,
        )

        total_height = (
            sum(
                item.height
                for item in measured
            )
            + minimum_gap
            * max(
                0,
                len(measured) - 1,
            )
        )

        if total_height <= available_height:
            return (
                question_size,
                option_size,
                leading,
                measured,
            )

        question_size -= 0.15
        option_size -= 0.15

    question_size = max(
        question_size,
        minimum_question_size,
    )

    option_size = max(
        option_size,
        minimum_option_size,
    )

    leading = max(
        option_size * leading_ratio,
        option_size + 1.1,
    )

    measured = _measure_questions(
        questions=questions,
        text_width=text_width,
        question_size=question_size,
        option_size=option_size,
        leading=leading,
    )

    return (
        question_size,
        option_size,
        leading,
        measured,
    )


# ============================================================
# BULLET
# ============================================================

def _draw_bullet(
    canvas: Canvas,
    *,
    x: float,
    y: float,
) -> None:
    canvas.saveState()

    canvas.setFillColor(
        BLACK,
    )

    canvas.circle(
        x,
        y,
        0.75 * mm,
        stroke=0,
        fill=1,
    )

    canvas.restoreState()


# ============================================================
# PUBLIC RENDERER
# ============================================================

def draw_mcqs(
    canvas: Canvas,
    rect: Rect,
    data: MCQData,
) -> None:
    questions = data.questions[:3]

    if not questions:
        return

    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    # Reduced top gap below the heading.
    content_rect = Rect(
        x=rect.x + 2.5 * mm,
        y=rect.y + 3 * mm,
        width=rect.width - 5 * mm,
        height=(
            heading_rect.y
            - rect.y
            - 3 * mm
        ),
    )

    bullet_column_width = 4.5 * mm
    bullet_text_gap = 1.2 * mm

    text_x = (
        content_rect.x
        + bullet_column_width
        + bullet_text_gap
    )

    text_width = (
        content_rect.width
        - bullet_column_width
        - bullet_text_gap
    )

    minimum_mcq_gap = 4 * mm

    (
        _question_size,
        _option_size,
        _leading,
        measured_questions,
    ) = _select_text_sizes(
        questions=questions,
        text_width=text_width,
        available_height=content_rect.height,
        minimum_gap=minimum_mcq_gap,
    )

    total_text_height = sum(
        item.height
        for item in measured_questions
    )

    available_gap_space = max(
        0,
        content_rect.height
        - total_text_height,
    )

    if len(measured_questions) > 1:
        distributed_gap = max(
            minimum_mcq_gap,
            available_gap_space
            / (
                len(measured_questions)
                - 1
            ),
        )
    else:
        distributed_gap = 0

    required_height = (
        total_text_height
        + distributed_gap
        * max(
            0,
            len(measured_questions) - 1,
        )
    )

    if required_height > content_rect.height:
        distributed_gap = minimum_mcq_gap

    current_top = (
        content_rect.top
        + 0.2 * mm
    )

    for measured in measured_questions:
        paragraph_bottom = (
            current_top
            - measured.height
        )

        measured.paragraph.drawOn(
            canvas,
            text_x,
            paragraph_bottom,
        )

        bullet_y = (
            current_top
            - measured.leading * 0.55
        )

        _draw_bullet(
            canvas=canvas,
            x=(
                content_rect.x
                + 1.3 * mm
            ),
            y=bullet_y,
        )

        current_top = (
            paragraph_bottom
            - distributed_gap
        )