from __future__ import annotations

from dataclasses import dataclass
import re

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
    canvas.setFillColor(HEADING_BLUE)
    canvas.setFont(FONT_BOLD, SECTION_TITLE_SIZE)
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

def _split_numberable_items(
    body: str,
) -> list[str]:
    """
    Split the statement/pair block into separate items.

    Prefer real line breaks. If the converter has collapsed a
    statement-based question into one line, fall back to sentence
    boundaries.
    """
    lines = [
        line.strip()
        for line in body.split("\n")
        if line.strip()
    ]

    if len(lines) >= 2:
        items = lines
    else:
        items = [
            part.strip()
            for part in re.split(
                r"(?<=[.!?])\s+",
                body.strip(),
            )
            if part.strip()
        ]

    cleaned: list[str] = []

    for item in items:
        item = re.sub(
            r"^\s*\d+\s*[.)]\s*",
            "",
            item,
        ).strip()

        if item:
            cleaned.append(item)

    return cleaned


def _format_mcq_question(
    question: str,
) -> str:
    """
    Format UPSC-style statement/pair MCQs so that the internal
    statements are visibly numbered.

    Handles forms such as:
      - Consider the following statements:
      - With reference to ..., consider the following statements:
      - Consider the following pairs:
    """
    raw = (
        question
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )

    if not raw:
        return ""

    # Find "consider the following statements/pairs" anywhere in
    # the opening sentence, not only at the very start.
    intro_match = re.search(
        r"(?is)\bconsider\s+the\s+following\s+"
        r"(?:statements|pairs)\s*:?\s*",
        raw,
    )

    if intro_match:
        intro = raw[:intro_match.end()].strip()

        remainder = raw[
            intro_match.end():
        ].strip()

        # Common UPSC closing prompts.
        tail_match = re.search(
            r"(?is)\b("
            r"Which\s+of\s+the\s+(?:statements|pairs)\s+given\s+above.*"
            r"|Which\s+of\s+the\s+above.*"
            r"|How\s+many\s+of\s+the\s+above.*"
            r"|How\s+many\s+of\s+these.*"
            r")$",
            remainder,
        )

        if tail_match:
            body = remainder[
                :tail_match.start()
            ].strip()

            tail = tail_match.group(1).strip()

            items = _split_numberable_items(
                body
            )

            if items:
                parts = [
                    intro,
                    "<br/>",
                ]

                for item_index, item in enumerate(
                    items,
                    start=1,
                ):
                    parts.append(
                        f"{item_index}. {item}"
                    )

                    if item_index < len(items):
                        parts.append("<br/>")

                parts.extend(
                    [
                        "<br/>",
                        tail,
                    ]
                )

                return "".join(parts)

    # --------------------------------------------------------
    # LINE-BASED LIST MCQ
    # --------------------------------------------------------
    # Handles questions such as:
    #
    #   In the context of ..., which of the following ...?
    #   Encouraging ...
    #   Improving ...
    #   Promoting ...
    #   Increasing ...
    #   Select the correct answer using the code below:
    #
    # The middle lines are rendered as 1., 2., 3., 4.
    lines = [
        line.strip()
        for line in raw.split("\n")
        if line.strip()
    ]

    if not lines:
        return ""

    if len(lines) >= 4:
        tail_start = None

        for line_index, line in enumerate(lines):
            if re.match(
                r"(?i)^select\s+the\s+correct\s+answer\b",
                line,
            ):
                tail_start = line_index
                break

        if (
            tail_start is not None
            and tail_start >= 3
        ):
            intro = lines[0]
            items = lines[1:tail_start]
            tail_lines = lines[tail_start:]

            # Number only genuinely list-like middle content.
            # Avoid double-numbering source text that already begins
            # with a number or option label.
            if (
                len(items) >= 2
                and all(
                    not re.match(
                        r"(?i)^(?:\d+[.)]|[A-D][.)])\s*",
                        item,
                    )
                    for item in items
                )
            ):
                parts = [
                    intro,
                    "<br/>",
                ]

                for item_index, item in enumerate(
                    items,
                    start=1,
                ):
                    parts.append(
                        f"{item_index}. {item}"
                    )

                    if item_index < len(items):
                        parts.append("<br/>")

                parts.append("<br/>")
                parts.append("<br/>".join(tail_lines))

                return "".join(parts)

    # Normal MCQ: preserve any source line breaks.
    return "<br/>".join(lines)


def _build_mcq_text(
    mcq: MCQ,
    question_size: float,
) -> str:
    formatted_question = _format_mcq_question(
        mcq.question
    )

    return (
        f"<font name='{FONT_REGULAR}' "
        f"size='{question_size}'>"
        f"{formatted_question}"
        f"</font>"
        f"<br/>"
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

    # Numbered hanging-indent layout:
    # the MCQ number stays in a narrow left column while the
    # question, wrapped lines, and options all align to the right.
    style.leftIndent = 5.0 * mm
    style.firstLineIndent = 0
    style.bulletIndent = 0
    style.bulletFontName = FONT_BOLD
    style.bulletFontSize = question_size
    style.bulletOffsetY = 0

    return Paragraph(
        _build_mcq_text(
            mcq=mcq,
            question_size=question_size,
        ),
        style,
        bulletText=f"{index}.",
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
    question_size = float(MCQ_QUESTION_SIZE)
    option_size = float(MCQ_OPTION_SIZE)

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
            sum(item.height for item in measured)
            + minimum_gap
            * max(0, len(measured) - 1)
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
    canvas.setFillColor(BLACK)
    canvas.circle(
        x,
        y,
        0.50 * mm,
        stroke=0,
        fill=1,
    )
    canvas.restoreState()


# ============================================================
# ANSWER KEY FOOTER
# ============================================================

def _normalise_correct_option(
    correct_option: str | None,
) -> str:
    if not correct_option:
        return "-"

    option = correct_option.strip().upper()

    if option.startswith("(") and option.endswith(")"):
        option = option[1:-1].strip()

    if option in {"A", "B", "C", "D"}:
        return option

    return "-"


def _build_answer_key(
    questions: tuple[MCQ, ...],
) -> str:
    answers = [
        (
            f"{index}-"
            f"{_normalise_correct_option(mcq.correct_option)}"
        )
        for index, mcq in enumerate(
            questions,
            start=1,
        )
    ]

    return "Answer Key  •  " + "  •  ".join(answers)


def _draw_answer_key_footer(
    canvas: Canvas,
    rect: Rect,
    questions: tuple[MCQ, ...],
) -> None:
    separator_y = rect.top - 0.8 * mm

    canvas.saveState()

    canvas.setStrokeColorRGB(
        0.78,
        0.78,
        0.78,
    )
    canvas.setLineWidth(0.35)
    canvas.line(
        rect.x,
        separator_y,
        rect.right,
        separator_y,
    )

    canvas.setFillColorRGB(
        0.28,
        0.28,
        0.28,
    )
    canvas.setFont(FONT_BOLD, 7.2)
    canvas.drawCentredString(
        rect.centre_x,
        rect.y + 1.45 * mm,
        _build_answer_key(questions),
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

    footer_height = 6 * mm
    footer_bottom_margin = 1.5 * mm

    footer_rect = Rect(
        x=rect.x + 3 * mm,
        y=rect.y + footer_bottom_margin,
        width=rect.width - 6 * mm,
        height=footer_height,
    )

    content_bottom = footer_rect.top + 1.2 * mm

    content_rect = Rect(
        x=rect.x + 2.5 * mm,
        y=content_bottom,
        width=rect.width - 5 * mm,
        height=max(
            0,
            heading_rect.y - content_bottom,
        ),
    )

    text_x = content_rect.x
    text_width = content_rect.width

    minimum_mcq_gap = 2 * mm

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
            / (len(measured_questions) - 1),
        )
    else:
        distributed_gap = 0

    required_height = (
        total_text_height
        + distributed_gap
        * max(0, len(measured_questions) - 1)
    )

    if required_height > content_rect.height:
        distributed_gap = minimum_mcq_gap

    current_top = content_rect.top + 0.2 * mm

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

        current_top = (
            paragraph_bottom
            - distributed_gap
        )

    _draw_answer_key_footer(
        canvas=canvas,
        rect=footer_rect,
        questions=questions,
    )