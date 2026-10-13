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
    QUESTION_LEADING_FULL,
    QUESTION_LEADING_HALF,
    QUESTION_SIZE_FULL,
    QUESTION_SIZE_HALF,
)


# ============================================================
# DATA MODEL
# ============================================================

@dataclass(frozen=True)
class CuriosityData:
    question: str

    # Recall Anchors are retained in the data interface for now
    # so existing callers remain compatible.
    #
    # They are intentionally NOT rendered in the Curiosity box.
    anchors: tuple[str, ...] = ()


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
# CURIOSITY BOX
# ============================================================

def draw_curiosity_box(
    canvas: Canvas,
    rect: Rect,
    data: CuriosityData,
    compact: bool = False,
) -> None:
    """
    Render Today's Question.

    Recall Anchors are intentionally not displayed here.

    They remain available elsewhere in the data pipeline for
    internal keyword highlighting in the Pro PDF.
    """

    # --------------------------------------------------------
    # FULL QUESTION AREA
    # --------------------------------------------------------

    content_rect = Rect(
        x=rect.x,
        y=rect.y,
        width=rect.width,
        height=rect.height,
    )

    # --------------------------------------------------------
    # LIGHTBULB ICON
    # --------------------------------------------------------

    icon_width = (
        11.5 * mm
        if compact
        else 13 * mm
    )

    icon_left_gap = 2.5 * mm

    icon_vertical_gap = (
        2.5 * mm
        if compact
        else 3 * mm
    )

    icon_rect = Rect(
        x=content_rect.x + icon_left_gap,
        y=content_rect.y + icon_vertical_gap,
        width=icon_width,
        height=max(
            0,
            content_rect.height
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

    question_left_gap = 2 * mm
    question_right_gap = 2.5 * mm

    question_vertical_gap = (
        3 * mm
        if compact
        else 4 * mm
    )

    question_rect = Rect(
        x=(
            icon_rect.right
            + question_left_gap
        ),
        y=(
            content_rect.y
            + question_vertical_gap
        ),
        width=max(
            0,
            content_rect.right
            - icon_rect.right
            - question_left_gap
            - question_right_gap,
        ),
        height=max(
            0,
            content_rect.height
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