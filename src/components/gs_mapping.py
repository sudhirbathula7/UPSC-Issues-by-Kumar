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
    Render GS Mapping as a compact three-line block.

    Target:

        GS II - Policies
        Developed and
        Developing Countries
    """

    # --------------------------------------------------------
    # SHORT PAPER NAME
    # --------------------------------------------------------

    paper_short = (
        item.paper
        .replace("GS Paper ", "GS ")
        .strip()
    )

    first_line = (
        f"{paper_short} - {item.subject}"
    )

    # --------------------------------------------------------
    # INNER AREA
    # --------------------------------------------------------

    inner = rect.inset(
        horizontal=0.7 * mm,
        vertical=0.5 * mm,
    )

    if (
        inner.width <= 0
        or inner.height <= 0
    ):
        return

    # --------------------------------------------------------
    # FONT SIZES
    # --------------------------------------------------------

    first_line_size = (
        GS_TOPIC_SIZE - 0.2
        if compact
        else GS_TOPIC_SIZE
    )

    topic_size = (
        GS_TOPIC_SIZE - 0.4
        if compact
        else GS_TOPIC_SIZE - 0.2
    )

    first_line_leading = (
        first_line_size + 0.8
    )

    topic_leading = (
        topic_size + 1.0
    )

    # --------------------------------------------------------
    # THREE-LINE LAYOUT
    # --------------------------------------------------------
    #
    # Line 1:
    #     GS II - Policies
    #
    # Lines 2-3:
    #     Developed and
    #     Developing Countries
    # --------------------------------------------------------

    first_line_height = (
        inner.height * 0.32
    )

    topic_height = (
        inner.height
        - first_line_height
    )

    first_line_rect = Rect(
        x=inner.x,
        y=inner.top - first_line_height,
        width=inner.width,
        height=first_line_height,
    )

    topic_rect = Rect(
        x=inner.x,
        y=inner.y,
        width=inner.width,
        height=topic_height,
    )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    first_line_style = paragraph_style(
        name=f"GSFirstLine{index}",
        font_name=FONT_BOLD,
        font_size=first_line_size,
        leading=first_line_leading,
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

    first_line_style.spaceBefore = 0
    first_line_style.spaceAfter = 0

    topic_style.spaceBefore = 0
    topic_style.spaceAfter = 0

    # --------------------------------------------------------
    # DRAW
    # --------------------------------------------------------

    draw_paragraph(
        canvas=canvas,
        text=first_line,
        rect=first_line_rect,
        style=first_line_style,
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