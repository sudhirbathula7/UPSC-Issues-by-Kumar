

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
    ANCHOR_LEADING,
    ANCHOR_TEXT_SIZE,
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    QUESTION_LEADING_FULL,
    QUESTION_LEADING_HALF,
    QUESTION_SIZE_FULL,
    QUESTION_SIZE_HALF,
)


@dataclass(frozen=True)
class CuriosityData:
    question: str
    anchors: tuple[str, ...]


# ============================================================
# LIGHTBULB ICON
# ============================================================

def draw_lightbulb_icon(
    canvas: Canvas,
    rect: Rect,
) -> None:
    canvas.saveState()

    canvas.setStrokeColor(BLACK)
    canvas.setFillColor(BLACK)
    canvas.setLineWidth(0.95)

    centre_x = rect.centre_x
    bulb_centre_y = (
        rect.y
        + rect.height * 0.63
    )

    bulb_radius = min(
        rect.width,
        rect.height,
    ) * 0.19

    canvas.circle(
        centre_x,
        bulb_centre_y,
        bulb_radius,
        stroke=1,
        fill=0,
    )

    neck_top = (
        bulb_centre_y
        - bulb_radius * 0.72
    )

    neck_bottom = (
        rect.y
        + rect.height * 0.25
    )

    neck_half_width = (
        bulb_radius * 0.38
    )

    canvas.line(
        centre_x - neck_half_width,
        neck_top,
        centre_x - neck_half_width * 0.62,
        neck_bottom,
    )

    canvas.line(
        centre_x + neck_half_width,
        neck_top,
        centre_x + neck_half_width * 0.62,
        neck_bottom,
    )

    base_width = (
        bulb_radius * 0.66
    )

    canvas.line(
        centre_x - base_width,
        neck_bottom,
        centre_x + base_width,
        neck_bottom,
    )

    canvas.line(
        centre_x - base_width * 0.78,
        neck_bottom - 1.1 * mm,
        centre_x + base_width * 0.78,
        neck_bottom - 1.1 * mm,
    )

    ray_start = (
        bulb_radius * 1.34
    )

    ray_end = (
        bulb_radius * 1.62
    )

    rays = (
        (0, 1),
        (0.72, 0.72),
        (1, 0),
        (-0.72, 0.72),
        (-1, 0),
    )

    for dx, dy in rays:
        canvas.line(
            centre_x + dx * ray_start,
            bulb_centre_y + dy * ray_start,
            centre_x + dx * ray_end,
            bulb_centre_y + dy * ray_end,
        )

    canvas.restoreState()


# ============================================================
# ANCHOR FORMATTER
# ============================================================

def _format_anchors(
    anchors: tuple[str, ...],
) -> str:
    cleaned = [
        anchor.strip()
        for anchor in anchors
        if anchor.strip()
    ]

    return (
        " &nbsp;&nbsp;•&nbsp;&nbsp; "
        .join(cleaned)
    )


# ============================================================
# CURIOSITY BOX
# ============================================================

def draw_curiosity_box(
    canvas: Canvas,
    rect: Rect,
    data: CuriosityData,
    compact: bool = False,
) -> None:
    """
    If Recall Anchors are present:
        - question uses the original upper area
        - anchors use the original lower area

    If Recall Anchors are absent:
        - the question uses the full curiosity-box height
        - the lightbulb and question are vertically centred
        - no empty anchor space is reserved
    """

    anchor_text = _format_anchors(
        data.anchors,
    )

    has_anchors = bool(
        anchor_text.strip()
    )

    # --------------------------------------------------------
    # VERTICAL LAYOUT
    # --------------------------------------------------------

    if has_anchors:
        top_height = (
            rect.height * 0.65
        )

        anchor_height = (
            rect.height * 0.35
        )

        top_rect = Rect(
            x=rect.x,
            y=rect.top - top_height,
            width=rect.width,
            height=top_height,
        )

        anchor_rect = Rect(
            x=rect.x + 3 * mm,
            y=rect.y + 1 * mm,
            width=rect.width - 6 * mm,
            height=anchor_height - 2 * mm,
        )

    else:
        # No anchors: reclaim the entire curiosity box for
        # Today's Question so there is no empty lower strip.
        top_rect = Rect(
            x=rect.x,
            y=rect.y,
            width=rect.width,
            height=rect.height,
        )

        anchor_rect = None

    # --------------------------------------------------------
    # LIGHTBULB ICON
    # --------------------------------------------------------

    icon_width = (
        11.5 * mm
        if compact
        else 13 * mm
    )

    icon_left_gap = (
        2.5 * mm
    )

    if has_anchors:
        icon_vertical_gap = 2 * mm
    else:
        # Slightly more breathing room when the full box is used.
        icon_vertical_gap = 3 * mm

    icon_rect = Rect(
        x=top_rect.x + icon_left_gap,
        y=top_rect.y + icon_vertical_gap,
        width=icon_width,
        height=max(
            0,
            top_rect.height
            - 2 * icon_vertical_gap,
        ),
    )

    draw_lightbulb_icon(
        canvas=canvas,
        rect=icon_rect,
    )

    # --------------------------------------------------------
    # TODAY'S QUESTION
    # --------------------------------------------------------

    question_left_gap = (
        2 * mm
    )

    question_right_gap = (
        2.5 * mm
    )

    if has_anchors:
        question_vertical_gap = 1.5 * mm
    else:
        # Use the full height but retain a clean internal margin.
        question_vertical_gap = 4 * mm

    question_rect = Rect(
        x=(
            icon_rect.right
            + question_left_gap
        ),
        y=(
            top_rect.y
            + question_vertical_gap
        ),
        width=max(
            0,
            top_rect.right
            - icon_rect.right
            - question_left_gap
            - question_right_gap,
        ),
        height=max(
            0,
            top_rect.height
            - 2 * question_vertical_gap,
        ),
    )

    question_size = (
        QUESTION_SIZE_HALF
        if compact
        else QUESTION_SIZE_FULL
    )

    question_leading = (
        QUESTION_LEADING_HALF
        if compact
        else QUESTION_LEADING_FULL
    )

    question_style = paragraph_style(
        name="CuriosityQuestion",
        font_name=FONT_BOLD,
        font_size=question_size,
        leading=question_leading,
        text_color=BLACK,
        alignment=TA_CENTER,
    )

    draw_paragraph(
        canvas=canvas,
        text=data.question,
        rect=question_rect,
        style=question_style,
        vertical_align="middle",
    )

    # --------------------------------------------------------
    # RECALL ANCHORS
    # --------------------------------------------------------

    if (
        has_anchors
        and anchor_rect is not None
    ):
        anchor_style = paragraph_style(
            name="RecallAnchors",
            font_name=FONT_REGULAR,
            font_size=(
                ANCHOR_TEXT_SIZE - 0.5
                if compact
                else ANCHOR_TEXT_SIZE
            ),
            leading=(
                ANCHOR_LEADING - 0.5
                if compact
                else ANCHOR_LEADING
            ),
            text_color=BLACK,
            alignment=TA_CENTER,
        )

        draw_paragraph(
            canvas=canvas,
            text=anchor_text,
            rect=anchor_rect,
            style=anchor_style,
            vertical_align="middle",
        )
