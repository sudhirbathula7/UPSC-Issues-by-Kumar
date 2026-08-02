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
    Top area:
    - small lightbulb icon
    - centred curiosity question

    Bottom area:
    - recall anchors across the full curiosity width
    """

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

    # Smaller icon in both layouts.
    icon_width = (
        11.5 * mm
        if compact
        else 13 * mm
    )

    icon_left_gap = (
        2.5 * mm
    )

    icon_rect = Rect(
        x=top_rect.x + icon_left_gap,
        y=top_rect.y + 2 * mm,
        width=icon_width,
        height=top_rect.height - 4 * mm,
    )

    draw_lightbulb_icon(
        canvas=canvas,
        rect=icon_rect,
    )

    # Question occupies everything between
    # the icon and the right edge of the curiosity box.
    question_left_gap = (
        2 * mm
    )

    question_right_gap = (
        2.5 * mm
    )

    question_rect = Rect(
        x=(
            icon_rect.right
            + question_left_gap
        ),
        y=top_rect.y + 1.5 * mm,
        width=max(
            0,
            top_rect.right
            - icon_rect.right
            - question_left_gap
            - question_right_gap,
        ),
        height=(
            top_rect.height
            - 3 * mm
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

    anchor_text = (
        _format_anchors(
            data.anchors,
        )
    )

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