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
    QUICK_FACT_LEADING,
    QUICK_FACT_SIZE,
    SECTION_TITLE_SIZE,
)


@dataclass(frozen=True)
class QuickFactsData:
    title: str
    facts: tuple[str, ...]


# ============================================================
# SECTION HEADING
# ============================================================

def _draw_section_title(
    canvas: Canvas,
    rect: Rect,
    title: str,
) -> Rect:
    """
    Draw a tiny Quick Facts logo immediately to the left
    of the title. The combined icon-title group is centred.
    """

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
        filename="quick_facts.svg",
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
# BULLET
# ============================================================

def _draw_bullet(
    canvas: Canvas,
    rect: Rect,
) -> None:
    canvas.saveState()

    canvas.setFillColor(
        BLACK,
    )

    canvas.circle(
        rect.centre_x,
        rect.centre_y,
        0.50* mm,
        stroke=0,
        fill=1,
    )

    canvas.restoreState()


# ============================================================
# SINGLE FACT
# ============================================================

def _draw_fact(
    canvas: Canvas,
    rect: Rect,
    fact: str,
    index: int,
) -> None:
    bullet_width = 4.5 * mm
    bullet_text_gap = 1.2 * mm

    bullet_rect = Rect(
        x=rect.x,
        y=rect.y,
        width=bullet_width,
        height=rect.height,
    )

    _draw_bullet(
        canvas=canvas,
        rect=bullet_rect,
    )

    text_rect = Rect(
        x=(
            bullet_rect.right
            + bullet_text_gap
        ),
        y=rect.y + 0.5 * mm,
        width=(
            rect.width
            - bullet_width
            - bullet_text_gap
        ),
        height=(
            rect.height
            - 1 * mm
        ),
    )

    style = paragraph_style(
        name=f"QuickFact{index}",
        font_name=FONT_REGULAR,
        font_size=QUICK_FACT_SIZE,
        leading=QUICK_FACT_LEADING,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=fact,
        rect=text_rect,
        style=style,
        vertical_align="middle",
    )


# ============================================================
# PUBLIC RENDERER
# ============================================================

def draw_quick_facts(
    canvas: Canvas,
    rect: Rect,
    data: QuickFactsData,
) -> None:
    facts = data.facts[:4]

    if not facts:
        return

    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    # Reduced gap below the heading so the first fact
    # starts slightly higher.
    content_rect = Rect(
        x=rect.x + 2.5 * mm,
        y=rect.y + 2 * mm,
        width=rect.width - 5 * mm,
        height=(
            heading_rect.y
            - rect.y
            - 2.1 * mm
        ),
    )

    fact_height = (
        content_rect.height
        / len(facts)
    )

    for index, fact in enumerate(
        facts,
        start=1,
    ):
        fact_top = (
            content_rect.top
            - (
                index - 1
            )
            * fact_height
        )

        fact_bottom = (
            fact_top
            - fact_height
        )

        fact_rect = Rect(
            x=content_rect.x,
            y=fact_bottom,
            width=content_rect.width,
            height=fact_height,
        )

        _draw_fact(
            canvas=canvas,
            rect=fact_rect,
            fact=fact,
            index=index,
        )