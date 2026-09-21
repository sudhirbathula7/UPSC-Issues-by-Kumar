from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.enums import TA_CENTER
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
    Draw the underlying concept/cause.

    The concept is centered and deliberately has no side arrow.
    The flow arrow is rendered separately below it.
    """

    style = paragraph_style(
        name="ConceptUnfoldConcept",
        font_name=FONT_BOLD,
        font_size=CONCEPT_UNFOLD_SIZE,
        leading=CONCEPT_UNFOLD_LEADING,
        text_color=BLACK,
        alignment=TA_CENTER,
    )

    draw_paragraph(
        canvas=canvas,
        text=concept,
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
    Draw one centered consequence.

    The title and explanation are both centered.
    Paragraph rendering is retained so Pro PDF
    recall-anchor highlighting continues to work.
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
        alignment=TA_CENTER,
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
        alignment=TA_CENTER,
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
    rect: Rect,
) -> None:
    """
    Draw a downward arrow exactly in the centre of a dedicated
    arrow region.

    Using a dedicated rectangle prevents arrows from touching
    either the text above or the text below.
    """

    if rect.height <= 0:
        return

    canvas.saveState()

    canvas.setFillColor(
        HEADING_BLUE,
    )

    canvas.setFont(
        FONT_BOLD,
        CONCEPT_UNFOLD_SIZE,
    )

    # Approximate vertical centering of the text glyph inside
    # the dedicated arrow region.
    baseline = (
        rect.y
        + (rect.height - CONCEPT_UNFOLD_SIZE) / 2
        + 1.4
    )

    canvas.drawCentredString(
        rect.centre_x,
        baseline,
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
    Render Concept Unfold as a clean vertical cause/consequence
    learning flow:

        CONCEPT UNFOLD

        Basic Concept

             ↓

        Consequence 1
        Explanation

             ↓

        Consequence 2
        Explanation

             ↓

        Consequence 3
        Explanation

    Every arrow receives its own reserved vertical region.
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
    # HEADING -> CONTENT GAP
    # --------------------------------------------------------

    usable_top = (
        content_rect.top
        - SECTION_CONTENT_GAP
    )

    usable_height = max(
        0,
        usable_top - content_rect.y,
    )

    if usable_height <= 0:
        return

    # --------------------------------------------------------
    # VERTICAL ALLOCATION
    # --------------------------------------------------------
    #
    # The arrows now have dedicated rows.
    #
    # This is the important change that prevents:
    #
    # explanation
    #      ↓
    #
    # from visually colliding.
    # --------------------------------------------------------

    concept_height = min(
        5.5 * mm,
        usable_height * 0.14,
    )

    arrow_height = min(
        6.0 * mm,
        usable_height * 0.085,
    )

    total_arrow_height = (
        arrow_height * 3
    )

    available_consequence_height = max(
        0,
        usable_height
        - concept_height
        - total_arrow_height,
    )

    consequence_height = (
        available_consequence_height / 3
    )

    if consequence_height <= 0:
        return

    # --------------------------------------------------------
    # CONCEPT / CAUSE
    # --------------------------------------------------------

    cursor_top = usable_top

    concept_rect = Rect(
        x=content_rect.x,
        y=cursor_top - concept_height,
        width=content_rect.width,
        height=concept_height,
    )

    _draw_concept(
        canvas=canvas,
        rect=concept_rect,
        concept=data.concept,
    )

    cursor_top = concept_rect.y

    # --------------------------------------------------------
    # ARROW 1
    # Concept -> Consequence 1
    # --------------------------------------------------------

    arrow_1_rect = Rect(
        x=content_rect.x,
        y=cursor_top - arrow_height,
        width=content_rect.width,
        height=arrow_height,
    )

    _draw_flow_arrow(
        canvas=canvas,
        rect=arrow_1_rect,
    )

    cursor_top = arrow_1_rect.y

    # --------------------------------------------------------
    # CONSEQUENCE 1
    # --------------------------------------------------------

    consequence_1_rect = Rect(
        x=content_rect.x,
        y=cursor_top - consequence_height,
        width=content_rect.width,
        height=consequence_height,
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_1_rect,
        consequence=consequences[0],
        index=1,
    )

    cursor_top = consequence_1_rect.y

    # --------------------------------------------------------
    # ARROW 2
    # Consequence 1 -> Consequence 2
    # --------------------------------------------------------

    arrow_2_rect = Rect(
        x=content_rect.x,
        y=cursor_top - arrow_height,
        width=content_rect.width,
        height=arrow_height,
    )

    _draw_flow_arrow(
        canvas=canvas,
        rect=arrow_2_rect,
    )

    cursor_top = arrow_2_rect.y

    # --------------------------------------------------------
    # CONSEQUENCE 2
    # --------------------------------------------------------

    consequence_2_rect = Rect(
        x=content_rect.x,
        y=cursor_top - consequence_height,
        width=content_rect.width,
        height=consequence_height,
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_2_rect,
        consequence=consequences[1],
        index=2,
    )

    cursor_top = consequence_2_rect.y

    # --------------------------------------------------------
    # ARROW 3
    # Consequence 2 -> Consequence 3
    # --------------------------------------------------------

    arrow_3_rect = Rect(
        x=content_rect.x,
        y=cursor_top - arrow_height,
        width=content_rect.width,
        height=arrow_height,
    )

    _draw_flow_arrow(
        canvas=canvas,
        rect=arrow_3_rect,
    )

    cursor_top = arrow_3_rect.y

    # --------------------------------------------------------
    # CONSEQUENCE 3
    # --------------------------------------------------------

    consequence_3_rect = Rect(
        x=content_rect.x,
        y=content_rect.y,
        width=content_rect.width,
        height=max(
            0,
            cursor_top - content_rect.y,
        ),
    )

    _draw_consequence(
        canvas=canvas,
        rect=consequence_3_rect,
        consequence=consequences[2],
        index=3,
    )