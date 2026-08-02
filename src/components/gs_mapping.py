from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from src.pdf.helpers import (
    draw_paragraph,
    paragraph_style,
)
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    GS_SUBJECT_SIZE,
    GS_TOPIC_LEADING,
    GS_TOPIC_SIZE,
)


@dataclass(frozen=True)
class GSMappingItem:
    paper: str
    subject: str
    topic: str


# ============================================================
# SINGLE GS MAPPING ITEM
# ============================================================

def _draw_mapping_item(
    canvas: Canvas,
    rect: Rect,
    item: GSMappingItem,
    index: int,
    compact: bool,
) -> None:
    """
    Draw one GS Mapping item in three centred lines:

    GS II
    International Relations
    West Asia
    """

    paper_size = (
        GS_SUBJECT_SIZE - 0.1
        if compact
        else GS_SUBJECT_SIZE
    )

    subject_size = (
        GS_TOPIC_SIZE - 0.1
        if compact
        else GS_TOPIC_SIZE
    )

    topic_size = (
        GS_TOPIC_SIZE - 0.2
        if compact
        else GS_TOPIC_SIZE
    )

    paper_leading = (
        paper_size + 1.2
    )

    subject_leading = (
        subject_size + 1.1
    )

    topic_leading = (
        GS_TOPIC_LEADING - 0.3
        if compact
        else GS_TOPIC_LEADING
    )

    inner = rect.inset(
        horizontal=1.5 * mm,
        vertical=1.5 * mm,
    )

    paper_height = min(
        5 * mm,
        inner.height * 0.24,
    )

    subject_height = min(
        7 * mm,
        inner.height * 0.34,
    )

    topic_height = max(
        0,
        inner.height
        - paper_height
        - subject_height
        - 1.5 * mm,
    )

    paper_rect = Rect(
        x=inner.x,
        y=inner.top - paper_height,
        width=inner.width,
        height=paper_height,
    )

    subject_rect = Rect(
        x=inner.x,
        y=paper_rect.y - subject_height,
        width=inner.width,
        height=subject_height,
    )

    topic_rect = Rect(
        x=inner.x,
        y=inner.y,
        width=inner.width,
        height=topic_height,
    )

    paper_style = paragraph_style(
        name=f"GSPaper{index}",
        font_name=FONT_BOLD,
        font_size=paper_size,
        leading=paper_leading,
        text_color=BLACK,
        alignment=TA_CENTER,
    )

    subject_style = paragraph_style(
        name=f"GSSubject{index}",
        font_name=FONT_REGULAR,
        font_size=subject_size,
        leading=subject_leading,
        text_color=BLACK,
        alignment=TA_CENTER,
    )

    topic_style = paragraph_style(
        name=f"GSTopic{index}",
        font_name=FONT_REGULAR,
        font_size=topic_size,
        leading=topic_leading,
        text_color=BLACK,
        alignment=TA_CENTER,
    )

    draw_paragraph(
        canvas=canvas,
        text=item.paper,
        rect=paper_rect,
        style=paper_style,
        vertical_align="middle",
    )

    draw_paragraph(
        canvas=canvas,
        text=item.subject,
        rect=subject_rect,
        style=subject_style,
        vertical_align="middle",
    )

    draw_paragraph(
        canvas=canvas,
        text=item.topic,
        rect=topic_rect,
        style=topic_style,
        vertical_align="middle",
    )


# ============================================================
# GS MAPPING SIDEBAR
# ============================================================

def draw_gs_mapping(
    canvas: Canvas,
    rect: Rect,
    items: tuple[GSMappingItem, ...],
    compact: bool = False,
) -> None:
    """
    Draw the GS Mapping sidebar.

    Behaviour:
    - One GS item: centred vertically.
    - Two or more GS items: stacked equally.
    - Each item is rendered as exactly three visual levels:
      paper, subject, and specific topic.
    """

    if not items:
        return

    canvas.saveState()

    canvas.setStrokeColor(BLACK)
    canvas.setLineWidth(0.55)

    # Vertical separator between curiosity and GS Mapping.
    canvas.line(
        rect.x,
        rect.y + 2 * mm,
        rect.x,
        rect.top - 2 * mm,
    )

    inner = rect.inset(
        horizontal=2 * mm,
        vertical=2 * mm,
    )

    item_count = len(items)

    if item_count == 1:
        centred_height = min(
            inner.height,
            22 * mm,
        )

        item_rect = Rect(
            x=inner.x,
            y=inner.centre_y - centred_height / 2,
            width=inner.width,
            height=centred_height,
        )

        _draw_mapping_item(
            canvas=canvas,
            rect=item_rect,
            item=items[0],
            index=0,
            compact=compact,
        )

        canvas.restoreState()
        return

    item_height = (
        inner.height
        / item_count
    )

    for index, item in enumerate(items):
        item_top = (
            inner.top
            - index * item_height
        )

        item_bottom = (
            item_top
            - item_height
        )

        item_rect = Rect(
            x=inner.x,
            y=item_bottom,
            width=inner.width,
            height=item_height,
        )

        _draw_mapping_item(
            canvas=canvas,
            rect=item_rect,
            item=item,
            index=index,
            compact=compact,
        )

        if index < item_count - 1:
            canvas.setLineWidth(0.40)

            canvas.line(
                inner.x,
                item_bottom,
                inner.right,
                item_bottom,
            )

    canvas.restoreState()