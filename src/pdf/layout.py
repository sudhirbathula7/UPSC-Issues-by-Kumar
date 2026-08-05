from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from src.config import (
    CONTENT_HEIGHT,
    CONTENT_WIDTH,
    PAGE_MARGIN_BOTTOM,
    PAGE_MARGIN_LEFT,
)
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BORDER_GREY,
    BOX_BORDER_WIDTH,
    BOX_RADIUS,
    DIVIDER_WIDTH,
    WHITE,
)


# ============================================================
# DISPLAY SWITCHES
# ============================================================

SHOW_BOXES = True
SHOW_DIVIDERS = True
SHOW_ICONS = True
SHOW_HEADER = True
SHOW_FOOTER = True
SHOW_OUTER_FRAME = False


# ============================================================
# PAGE AREA
# ============================================================

PAGE_X = PAGE_MARGIN_LEFT
PAGE_Y = PAGE_MARGIN_BOTTOM
PAGE_WIDTH = CONTENT_WIDTH
PAGE_HEIGHT = CONTENT_HEIGHT


# ============================================================
# MASTER FULL-PAGE DIMENSIONS
# ============================================================

HEADER_HEIGHT = 12 * mm
FOOTER_HEIGHT = 6 * mm

SECTION_GAP = 1.2 * mm
COLUMN_GAP = 1.2* mm

QUESTION_PANEL_HEIGHT = 21 * mm

# Top question-panel split:
# 86% Curiosity Question
# 14% GS Mapping
GS_MAPPING_RATIO = 0.15

TOP_CONTENT_LEFT_RATIO = 0.50
BOTTOM_CONTENT_LEFT_RATIO = 0.50

QUICK_FACTS_RATIO = 0.73


# ============================================================
# BOX APPEARANCE
# ============================================================

SECTION_BOX_RADIUS = BOX_RADIUS
SECTION_BOX_BORDER_WIDTH = BOX_BORDER_WIDTH
SECTION_BOX_BORDER_COLOR = BORDER_GREY
SECTION_BOX_FILL_COLOR = WHITE

INTERNAL_DIVIDER_WIDTH = DIVIDER_WIDTH
INTERNAL_DIVIDER_COLOR = BORDER_GREY

BOX_EDGE_INSET = 0 * mm


# ============================================================
# FULL-PAGE LAYOUT DATA
# ============================================================

@dataclass(frozen=True, slots=True)
class FullPageLayout:
    page: Rect

    header: Rect
    footer: Rect

    body: Rect
    top_half: Rect
    bottom_half: Rect

    question_panel: Rect
    curiosity_box: Rect
    gs_mapping: Rect

    top_content: Rect
    knowledge_points: Rect
    right_top_column: Rect
    quick_facts: Rect
    takeaway: Rect

    bottom_content: Rect
    mains_answer: Rect
    mcqs: Rect


# ============================================================
# FULL-PAGE GEOMETRY
# ============================================================

def build_full_page_layout() -> FullPageLayout:
    page = Rect(
        x=PAGE_X,
        y=PAGE_Y,
        width=PAGE_WIDTH,
        height=PAGE_HEIGHT,
    )

    header = Rect(
        x=page.x,
        y=page.top - HEADER_HEIGHT,
        width=page.width,
        height=HEADER_HEIGHT,
    )

    footer = Rect(
        x=page.x,
        y=page.y,
        width=page.width,
        height=FOOTER_HEIGHT,
    )

    body_top = header.y - SECTION_GAP
    body_bottom = footer.top + SECTION_GAP

    body = Rect(
        x=page.x,
        y=body_bottom,
        width=page.width,
        height=max(
            0,
            body_top - body_bottom,
        ),
    )

    half_height = (
        body.height - SECTION_GAP
    ) / 2

    bottom_half = Rect(
        x=body.x,
        y=body.y,
        width=body.width,
        height=half_height,
    )

    top_half = Rect(
        x=body.x,
        y=bottom_half.top + SECTION_GAP,
        width=body.width,
        height=half_height,
    )

    # ========================================================
    # QUESTION PANEL
    # ========================================================

    question_panel = Rect(
        x=top_half.x,
        y=top_half.top - QUESTION_PANEL_HEIGHT,
        width=top_half.width,
        height=QUESTION_PANEL_HEIGHT,
    )

    gs_mapping_width = (
        question_panel.width
        * GS_MAPPING_RATIO
    )

    curiosity_width = max(
        0,
        question_panel.width
        - gs_mapping_width,
    )

    curiosity_box = Rect(
        x=question_panel.x,
        y=question_panel.y,
        width=curiosity_width,
        height=question_panel.height,
    )

    gs_mapping = Rect(
        x=curiosity_box.right,
        y=question_panel.y,
        width=gs_mapping_width,
        height=question_panel.height,
    )

    # ========================================================
    # TOP CONTENT
    # ========================================================

    top_content = Rect(
        x=top_half.x,
        y=top_half.y,
        width=top_half.width,
        height=max(
            0,
            question_panel.y
            - SECTION_GAP
            - top_half.y,
        ),
    )

    knowledge_points, right_top_column = (
        top_content.split_vertical(
            left_ratio=TOP_CONTENT_LEFT_RATIO,
            gap=COLUMN_GAP,
        )
    )

    available_right_height = (
        right_top_column.height
        - SECTION_GAP
    )

    quick_facts_height = (
        available_right_height
        * QUICK_FACTS_RATIO
    )

    takeaway_height = (
        available_right_height
        - quick_facts_height
    )

    quick_facts = Rect(
        x=right_top_column.x,
        y=right_top_column.top
        - quick_facts_height,
        width=right_top_column.width,
        height=quick_facts_height,
    )

    takeaway = Rect(
        x=right_top_column.x,
        y=right_top_column.y,
        width=right_top_column.width,
        height=takeaway_height,
    )

    # ========================================================
    # BOTTOM CONTENT
    # ========================================================

    bottom_content = Rect(
        x=bottom_half.x,
        y=bottom_half.y,
        width=bottom_half.width,
        height=bottom_half.height,
    )

    mains_answer, mcqs = (
        bottom_content.split_vertical(
            left_ratio=BOTTOM_CONTENT_LEFT_RATIO,
            gap=COLUMN_GAP,
        )
    )

    return FullPageLayout(
        page=page,
        header=header,
        footer=footer,
        body=body,
        top_half=top_half,
        bottom_half=bottom_half,
        question_panel=question_panel,
        curiosity_box=curiosity_box,
        gs_mapping=gs_mapping,
        top_content=top_content,
        knowledge_points=knowledge_points,
        right_top_column=right_top_column,
        quick_facts=quick_facts,
        takeaway=takeaway,
        bottom_content=bottom_content,
        mains_answer=mains_answer,
        mcqs=mcqs,
    )


# ============================================================
# CENTRAL BOX DRAWING
# ============================================================

def draw_layout_box(
    canvas: Canvas,
    rect: Rect,
    *,
    enabled: bool | None = None,
    radius: float = SECTION_BOX_RADIUS,
    border_width: float = SECTION_BOX_BORDER_WIDTH,
    stroke_color=SECTION_BOX_BORDER_COLOR,
    fill_color=SECTION_BOX_FILL_COLOR,
) -> None:
    should_draw = (
        SHOW_BOXES
        if enabled is None
        else enabled
    )

    if not should_draw:
        return

    canvas.saveState()

    canvas.setStrokeColor(stroke_color)
    canvas.setFillColor(fill_color)
    canvas.setLineWidth(border_width)

    canvas.roundRect(
        rect.x + BOX_EDGE_INSET,
        rect.y + BOX_EDGE_INSET,
        rect.width - 2 * BOX_EDGE_INSET,
        rect.height - 2 * BOX_EDGE_INSET,
        radius,
        stroke=1,
        fill=1,
    )

    canvas.restoreState()


def draw_horizontal_divider(
    canvas: Canvas,
    *,
    x_left: float,
    x_right: float,
    y: float,
) -> None:
    if not SHOW_DIVIDERS:
        return

    canvas.saveState()

    canvas.setStrokeColor(
        INTERNAL_DIVIDER_COLOR
    )
    canvas.setLineWidth(
        INTERNAL_DIVIDER_WIDTH
    )

    canvas.line(
        x_left,
        y,
        x_right,
        y,
    )

    canvas.restoreState()


def draw_vertical_divider(
    canvas: Canvas,
    *,
    x: float,
    y_bottom: float,
    y_top: float,
) -> None:
    if not SHOW_DIVIDERS:
        return

    canvas.saveState()

    canvas.setStrokeColor(
        INTERNAL_DIVIDER_COLOR
    )
    canvas.setLineWidth(
        INTERNAL_DIVIDER_WIDTH
    )

    canvas.line(
        x,
        y_bottom,
        x,
        y_top,
    )

    canvas.restoreState()


# ============================================================
# ACCESSOR
# ============================================================

_FULL_PAGE_LAYOUT = build_full_page_layout()


def get_full_page_layout() -> FullPageLayout:
    return _FULL_PAGE_LAYOUT


def get_layout() -> FullPageLayout:
    return _FULL_PAGE_LAYOUT