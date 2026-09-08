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
    KNOWLEDGE_LEADING,
    KNOWLEDGE_TEXT_SIZE,
    SECTION_TITLE_SIZE,
)


@dataclass(frozen=True)
class KnowledgePoint:
    heading: str
    explanation: str


@dataclass(frozen=True)
class KnowledgePointsData:
    title: str
    points: tuple[KnowledgePoint, ...]


@dataclass(frozen=True)
class _MeasuredPoint:
    paragraph: Paragraph
    height: float


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
        filename="knowledge.svg",
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
# KNOWLEDGE POINT PARAGRAPH
# ============================================================

def _build_paragraph(
    point: KnowledgePoint,
    index: int,
    font_size: float,
    leading: float,
) -> Paragraph:
    point_text = (
        f"<b>{point.heading}:</b> "
        f"{point.explanation}"
    )

    style = paragraph_style(
        name=f"KnowledgePoint{index}",
        font_name=FONT_REGULAR,
        font_size=font_size,
        leading=leading,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    style.spaceBefore = 0
    style.spaceAfter = 0

    return Paragraph(
        point_text,
        style,
    )


# ============================================================
# MEASUREMENT
# ============================================================

def _measure_points(
    points: tuple[KnowledgePoint, ...],
    text_width: float,
    font_size: float,
    leading: float,
) -> tuple[_MeasuredPoint, ...]:
    measured: list[_MeasuredPoint] = []

    for index, point in enumerate(
        points,
        start=1,
    ):
        paragraph = _build_paragraph(
            point=point,
            index=index,
            font_size=font_size,
            leading=leading,
        )

        _, paragraph_height = paragraph.wrap(
            text_width,
            1000 * mm,
        )

        measured.append(
            _MeasuredPoint(
                paragraph=paragraph,
                height=paragraph_height,
            )
        )

    return tuple(measured)


def _select_text_size(
    points: tuple[KnowledgePoint, ...],
    text_width: float,
    available_height: float,
    point_gap: float,
) -> tuple[
    float,
    float,
    tuple[_MeasuredPoint, ...],
]:
    minimum_font_size = 5.2

    font_size = float(
        KNOWLEDGE_TEXT_SIZE
    )

    leading_ratio = (
        float(KNOWLEDGE_LEADING)
        / float(KNOWLEDGE_TEXT_SIZE)
    )

    while font_size >= minimum_font_size:
        leading = max(
            font_size * leading_ratio,
            font_size + 1.0,
        )

        measured = _measure_points(
            points=points,
            text_width=text_width,
            font_size=font_size,
            leading=leading,
        )

        total_height = (
            sum(
                item.height
                for item in measured
            )
            + point_gap
            * max(
                0,
                len(measured) - 1,
            )
        )

        if total_height <= available_height:
            return (
                font_size,
                leading,
                measured,
            )

        font_size -= 0.2

    leading = max(
        minimum_font_size * leading_ratio,
        minimum_font_size + 1.0,
    )

    measured = _measure_points(
        points=points,
        text_width=text_width,
        font_size=minimum_font_size,
        leading=leading,
    )

    return (
        minimum_font_size,
        leading,
        measured,
    )


# ============================================================
# BULLET
# ============================================================

def _draw_bullet(
    canvas: Canvas,
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
        0.50 * mm,
        stroke=0,
        fill=1,
    )

    canvas.restoreState()


# ============================================================
# PUBLIC RENDERER
# ============================================================

def draw_knowledge_points(
    canvas: Canvas,
    rect: Rect,
    data: KnowledgePointsData,
) -> None:
    points = data.points[:5]

    if not points:
        return

    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    content_rect = Rect(
        x=rect.x + 2.5 * mm,
        y=rect.y + 2.2 * mm,
        width=rect.width - 5 * mm,
        height=(
            heading_rect.y
            - rect.y
            - 2.2 * mm
        ),
    )

    bullet_column_width = 4.5 * mm
    bullet_text_gap = 1.2 * mm
    point_gap = 1.1 * mm

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

    (
        _font_size,
        _leading,
        measured_points,
    ) = _select_text_size(
        points=points,
        text_width=text_width,
        available_height=content_rect.height,
        point_gap=point_gap,
    )

    total_content_height = (
        sum(
            item.height
            for item in measured_points
        )
        + point_gap
        * max(
            0,
            len(measured_points) - 1,
        )
    )

    extra_space = max(
        0,
        content_rect.height
        - total_content_height,
    )

    if len(measured_points) > 1:
        extra_gap = min(
            extra_space
            / (
                len(measured_points) - 1
            ),
            2.2 * mm,
        )
    else:
        extra_gap = 0

    distributed_gap = (
        point_gap
        + extra_gap
    )

    current_top = (
        content_rect.top
        - 1* mm
    )

    for measured in measured_points:
        paragraph_bottom = (
            current_top
            - measured.height
        )

        measured.paragraph.drawOn(
            canvas,
            text_x,
            paragraph_bottom,
        )

        first_line_y = (
            current_top
            - measured.paragraph.style.leading
            * 0.52
        )

        _draw_bullet(
            canvas=canvas,
            x=(
                content_rect.x
                + 1.3 * mm
            ),
            y=first_line_y,
        )

        current_top = (
            paragraph_bottom
            - distributed_gap
        )