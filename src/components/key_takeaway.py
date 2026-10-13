from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

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
    SECTION_CONTENT_GAP,
    SECTION_HEADING_HEIGHT,
    SECTION_TITLE_SIZE,
    SECTION_TOP_GAP,
    TAKEAWAY_LEADING,
    TAKEAWAY_SIZE,
)


@dataclass(frozen=True)
class KeyTakeawayData:
    title: str
    takeaway: str


# ============================================================
# SECTION HEADING
# ============================================================

def _draw_section_title(
    canvas: Canvas,
    rect: Rect,
    title: str,
) -> Rect:
    heading_rect = Rect(
        x=rect.x + 3 * mm,
        y=(
            rect.top
            - SECTION_TOP_GAP
            - SECTION_HEADING_HEIGHT
        ),
        width=rect.width - 6 * mm,
        height=SECTION_HEADING_HEIGHT,
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
        filename="key_takeaway.svg",
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
# PUBLIC RENDERER
# ============================================================

def draw_key_takeaway(
    canvas: Canvas,
    rect: Rect,
    data: KeyTakeawayData,
) -> None:
    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    # --------------------------------------------------------
    # CONTENT AREA
    # --------------------------------------------------------

    bottom_padding = 1.8 * mm

    content_top = (
        heading_rect.y
        - SECTION_CONTENT_GAP
    )

    content_rect = Rect(
        x=rect.x + 3 * mm,
        y=rect.y + bottom_padding,
        width=rect.width - 6 * mm,
        height=max(
            0,
            content_top
            - rect.y
            - bottom_padding,
        ),
    )

    if content_rect.height <= 0:
        return

    # --------------------------------------------------------
    # TAKEAWAY TEXT
    # --------------------------------------------------------

    style = paragraph_style(
        name="KeyTakeaway",
        font_name=FONT_REGULAR,
        font_size=TAKEAWAY_SIZE,
        leading=TAKEAWAY_LEADING,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=data.takeaway,
        rect=content_rect,
        style=style,
        vertical_align="top",
    )