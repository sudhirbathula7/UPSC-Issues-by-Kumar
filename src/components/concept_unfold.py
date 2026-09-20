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


# ============================================================
# DATA MODELS
# ============================================================

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

    # Keep this calculation so heading geometry remains
    # consistent with the existing component.
    stringWidth(
        title,
        FONT_BOLD,
        SECTION_TITLE_SIZE,
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

    canvas.drawCentredString(
        heading_rect.centre_x,
        heading_baseline,
        title,
    )

    canvas.restoreState()

    return heading_rect


# ============================================================
# CONCEPT
# ============================================================

def _draw_concept(
    canvas: Canvas,
    rect: Rect,
    concept: str,
) -> None:
    """
    Draw the underlying UPSC concept.
    """

    style = paragraph_style(
        name="ConceptUnfoldConcept",
        font_name=FONT_BOLD,
        font_size=CONCEPT_UNFOLD_SIZE,
        leading=CONCEPT_UNFOLD_LEADING,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=f"{concept} →",
        rect=rect,
        style=style,
        vertical_align="top",
    )


# ============================================================
# CONSEQUENCE
# ============================================================

def _draw_consequence(
    canvas: Canvas,
    rect: Rect,
    consequence: ConceptUnfoldConsequence,
    index: int,
) -> None:
    """
    Draw one consequence.

    Paragraph rendering is used for both heading and explanation
    so Pro PDF recall-anchor highlighting markup remains supported.
    """

    if rect.height <= 0:
        return

    heading_height = min(
        5.0 * mm,
        rect.height,
    )

    heading_rect = Rect(
        x=rect.x,
        y=rect.top - heading_height,
        width=rect.width,
        height=heading_height,
    )

    heading_style = paragraph_style(
        name=f"ConceptUnfoldHeading{index}",
        font_name=FONT_BOLD,
        font_size=CONCEPT_UNFOLD_SIZE,
        leading=CONCEPT_UNFOLD_LEADING,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=consequence.title,
        rect=heading_rect,
        style=heading_style,
        vertical_align="top",
    )

    explanation_height = max(
        0,
        rect.height - heading_height,
    )

    if explanation_height <= 0:
        return

    explanation_rect = Rect(
        x=rect.x,
        y=rect.y,
        width=rect.width,
        height=explanation_height,
    )

    explanation_style = paragraph_style(
        name=f"ConceptUnfoldConsequence{index}",
        font_name=FONT_REGULAR,
        font_size=CONCEPT_UNFOLD_SIZE,
        leading=CONCEPT_UNFOLD_LEADING,
        text_color=BLACK,
        alignment=TA_LEFT,
    )

    draw_paragraph(
        canvas=canvas,
        text=consequence.explanation,
        rect=explanation_rect,
        style=explanation_style,
        vertical_align="top",
    )


# ============================================================
# FLOW ARROW
# ============================================================

def _draw_flow_arrow(
    canvas: Canvas,
    x: float,
    y: float,
) -> None:
    """
    Draw a small downward arrow to visually connect
    the concept and consequences.
    """

    canvas.saveState()

    canvas.setFillColor(
        HEADING_BLUE,
    )

    canvas.setFont(
        FONT_BOLD,
        CONCEPT_UNFOLD_SIZE,
    )

    canvas.drawCentredString(
        x,
        y,
        "↓",
    )

    canvas.restoreState()


# ============================================================
# PUBLIC RENDERER
# ============================================================

def draw_concept_unfold(
    canvas: Canvas,
    rect: Rect,
    data: ConceptUnfoldData,
) -> None:
    """
    Render one Concept Unfold with exactly three consequences.

    Vertical structure:

        CONCEPT UNFOLD
        [SECTION_CONTENT_GAP]
        Basic concept →
              ↓
        Consequence 1
              ↓
        Consequence 2
              ↓
        Consequence 3
    """

    if not data.concept.strip():
        return

    consequences = data.consequences[:3]

    if len(consequences) != 3:
        return

    # --------------------------------------------------------
    # SECTION TITLE
    # --------------------------------------------------------

    heading_rect = _draw_section_title(
        canvas=canvas,
        rect=rect,
        title=data.title,
    )

    # --------------------------------------------------------
    # CONTENT AREA
    # --------------------------------------------------------

    bottom_padding = 1.5 * mm

    content_rect = Rect(
        x=rect.x + 2.5 * mm,
        y=rect.y + bottom_padding,
        width=max(
            0,
            rect.width - 5 * mm,
        ),
        height=max(
            0,
            heading_rect.y
            - rect.y
            - bottom_padding,
        ),
    )

    if content_rect.height <= 0:
        return

    # --------------------------------------------------------
    # HEADING -> FIRST CONTENT SPACING
    # --------------------------------------------------------

    concept_top = max(
        content_rect.y,
        content_rect.top
        - SECTION_CONTENT_GAP,
    )

    # --------------------------------------------------------
    # VERTICAL LAYOUT
    # --------------------------------------------------------

    concept_height = min(
        10.0 * mm,
        max(
            0,
            content_rect.height
            - SECTION_CONTENT_GAP,
        )
        * 0.18,
    )

    arrow_height = min(
        3.2 * mm,
        content_rect.height * 0.055,
    )

    consequence_gap = min(
        0.8 * mm,
        content_rect.height * 0.012,
    )

    # --------------------------------------------------------
    # CONCEPT
    # --------------------------------------------------------

    concept_rect = Rect(
        x=content_rect.x,
        y=max(
            content_rect.y,
            concept_top - concept_height,
        ),
        width=content_rect.width,
        height=max(
            0,
            min(
                concept_height,
                concept_top - content_rect.y,
            ),
        ),
    )

    _draw_concept(
        canvas=canvas,
        rect=concept_rect,
        concept=data.concept,
    )

    # --------------------------------------------------------
    # FIRST FLOW ARROW
    # Concept -> Consequence 1
    # --------------------------------------------------------

    first_arrow_y = (
        concept_rect.y
        - 0.4 * mm
    )

    _draw_flow_arrow(
        canvas=canvas,
        x=content_rect.centre_x,
        y=first_arrow_y,
    )

    # --------------------------------------------------------
    # CONSEQUENCE REGION
    # --------------------------------------------------------

    consequences_top = (
        first_arrow_y
        - arrow_height
    )

    consequences_bottom = (
        content_rect.y
    )

    total_internal_arrow_space = (
        2 * arrow_height
    )

    total_gap_space = (
        2 * consequence_gap
    )

    available_consequence_height = max(
        0,
        consequences_top
        - consequences_bottom
        - total_internal_arrow_space
        - total_gap_space,
    )

    consequence_height = (
        available_consequence_height
        / 3
    )

    if consequence_height <= 0:
        return

    # --------------------------------------------------------
    # CONSEQUENCE 1
    # --------------------------------------------------------

    consequence_1_top = consequences_top

    consequence_1_bottom = (
        consequence_1_top
        - consequence_height
    )

    consequence_1_rect = Rect(
        x=content_rect.x,
        y=consequence_1_bottom,
        width=content_rect.width,
        height=consequence_height,
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_1_rect,
        consequence=consequences[0],
        index=1,
    )

    # --------------------------------------------------------
    # SECOND FLOW ARROW
    # Consequence 1 -> Consequence 2
    # --------------------------------------------------------

    second_arrow_y = (
        consequence_1_bottom
        - 0.4 * mm
    )

    _draw_flow_arrow(
        canvas=canvas,
        x=content_rect.centre_x,
        y=second_arrow_y,
    )

    # --------------------------------------------------------
    # CONSEQUENCE 2
    # --------------------------------------------------------

    consequence_2_top = (
        second_arrow_y
        - arrow_height
        - consequence_gap
    )

    consequence_2_bottom = (
        consequence_2_top
        - consequence_height
    )

    consequence_2_rect = Rect(
        x=content_rect.x,
        y=consequence_2_bottom,
        width=content_rect.width,
        height=consequence_height,
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_2_rect,
        consequence=consequences[1],
        index=2,
    )

    # --------------------------------------------------------
    # THIRD FLOW ARROW
    # Consequence 2 -> Consequence 3
    # --------------------------------------------------------

    third_arrow_y = (
        consequence_2_bottom
        - 0.4 * mm
    )

    _draw_flow_arrow(
        canvas=canvas,
        x=content_rect.centre_x,
        y=third_arrow_y,
    )

    # --------------------------------------------------------
    # CONSEQUENCE 3
    # --------------------------------------------------------

    consequence_3_top = (
        third_arrow_y
        - arrow_height
        - consequence_gap
    )

    consequence_3_rect = Rect(
        x=content_rect.x,
        y=content_rect.y,
        width=content_rect.width,
        height=max(
            0,
            consequence_3_top
            - content_rect.y,
        ),
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_3_rect,
        consequence=consequences[2],
        index=3,
    )