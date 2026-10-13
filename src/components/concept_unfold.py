"""Centred, content-aware Concept Unfold panel for UPSC Anchor PDFs.

Preserves the public data models and draw_concept_unfold(canvas, rect, data)
interface used by the existing PDF generator.
"""
from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.pdfgen.canvas import Canvas

from src.pdf.helpers import paragraph_style
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    CONCEPT_UNFOLD_LEADING,
    CONCEPT_UNFOLD_SIZE,
    FONT_BOLD,
    FONT_REGULAR,
    HEADING_BLUE,
    SECTION_CONTENT_GAP,
    SECTION_HEADING_HEIGHT,
    SECTION_TITLE_SIZE,
    SECTION_TOP_GAP,
)


@dataclass(frozen=True)
class ConceptUnfoldConsequence:
    title: str
    explanation: str


@dataclass(frozen=True)
class ConceptUnfoldData:
    concept: str
    consequences: tuple[
        ConceptUnfoldConsequence,
        ConceptUnfoldConsequence,
        ConceptUnfoldConsequence,
    ]
    title: str = "CONCEPT UNFOLD"


def _style(name: str, font: str, size: float, leading: float):
    return paragraph_style(
        name=name,
        font_name=font,
        font_size=size,
        leading=leading,
        text_color=BLACK,
        alignment=TA_CENTER,
    )


def _paragraph(text: str, style, width: float):
    # Paragraph supports existing ReportLab markup such as <b>recall anchors</b>.
    p = Paragraph(text, style)
    _, height = p.wrap(width, 10000)
    return p, height


def _draw_heading(canvas: Canvas, rect: Rect, title: str) -> float:
    """Draw the section heading and return the lower boundary of its area."""
    heading_bottom = rect.top - SECTION_TOP_GAP - SECTION_HEADING_HEIGHT
    canvas.saveState()
    canvas.setFillColor(HEADING_BLUE)
    canvas.setFont(FONT_BOLD, SECTION_TITLE_SIZE)
    baseline = heading_bottom + (SECTION_HEADING_HEIGHT - SECTION_TITLE_SIZE) / 2 + 1.4
    canvas.drawCentredString(rect.centre_x, baseline, title)
    canvas.restoreState()
    return heading_bottom


def _layout(data: ConceptUnfoldData, width: float, size: float):
    """Measure every paragraph before allocating vertical space."""
    leading = CONCEPT_UNFOLD_LEADING * (size / CONCEPT_UNFOLD_SIZE)
    blocks = []
    concept_style = _style("ConceptUnfoldConcept", FONT_BOLD, size, leading)
    blocks.append(_paragraph(data.concept.strip(), concept_style, width))
    for index, item in enumerate(data.consequences[:3], 1):
        title_style = _style(f"ConceptUnfoldHeading{index}", FONT_BOLD, size, leading)
        body_style = _style(f"ConceptUnfoldExplanation{index}", FONT_REGULAR, size, leading)
        blocks.append(_paragraph(item.title, title_style, width))
        blocks.append(_paragraph(item.explanation, body_style, width))
    return blocks, sum(h for _, h in blocks), leading


def draw_concept_unfold(canvas: Canvas, rect: Rect, data: ConceptUnfoldData) -> None:
    """Draw a centred concept followed by three evenly separated consequences.

    Text heights are measured, so arrows cannot land inside explanation text.
    The entire content is fitted to the existing panel without changing its size.
    """
    if not data.concept.strip() or len(data.consequences) != 3:
        return

    heading_bottom = _draw_heading(canvas, rect, data.title)
    horizontal_padding = 2.5 * mm
    width = rect.width - 2 * horizontal_padding
    if width <= 0:
        return

    top = heading_bottom - SECTION_CONTENT_GAP
    bottom = rect.y + 1.5 * mm
    available = top - bottom
    if available <= 0:
        return

    # Layout sequence: concept, arrow, title 1, explanation 1, arrow,
    # title 2, explanation 2, arrow, title 3, explanation 3.
    # The three arrow slots each have equal height; every paragraph is
    # measured using the actual wrapping width before anything is drawn.
    size = float(CONCEPT_UNFOLD_SIZE)
    min_size = max(5.0, size * 0.75)
    blocks = []
    arrow_slot = 0.0
    title_body_gap = 0.0
    for _ in range(35):
        blocks, text_height, leading = _layout(data, width, size)
        arrow_slot = max(leading * 1.30, 3.5 * mm)
        title_body_gap = max(0.5 * mm, leading * 0.18)
        required = text_height + 3 * arrow_slot + 3 * title_body_gap
        if required <= available or size <= min_size:
            break
        size = max(min_size, size - 0.15)

    # If exceptionally long input cannot fit even at the minimum size,
    # raise an explicit error rather than silently overlapping/clipping text.
    if required > available + 0.1:
        raise ValueError(
            "Concept Unfold content is too long for its PDF panel. "
            "Shorten the concept or consequence explanations."
        )

    # Distribute spare height equally between the 3 arrow slots and
    # the top/bottom margins, avoiding large unexplained blank areas.
    spare = max(0.0, available - required)
    arrow_slot += spare * 0.23
    y = top - spare * 0.155

    def draw_block(block):
        nonlocal y
        paragraph, height = block
        y -= height
        paragraph.drawOn(canvas, rect.x + horizontal_padding, y)

    def draw_arrow():
        nonlocal y
        # Arrow is centred within its own reserved vertical slot.
        center_y = y - arrow_slot / 2
        arrow_size = max(size + 1.0, SECTION_TITLE_SIZE)
        canvas.saveState()
        canvas.setFillColor(HEADING_BLUE)
        canvas.setFont(FONT_BOLD, arrow_size)
        canvas.drawCentredString(rect.centre_x, center_y - arrow_size * 0.32, "↓")
        canvas.restoreState()
        y -= arrow_slot

    draw_block(blocks[0])  # Basic concept
    for i in range(3):
        draw_arrow()
        draw_block(blocks[1 + i * 2])  # Consequence heading
        y -= title_body_gap
        draw_block(blocks[2 + i * 2])  # Consequence explanation
