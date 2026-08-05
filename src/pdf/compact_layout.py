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
SHOW_HEADER = True
SHOW_FOOTER = True


# ============================================================
# PAGE AREA
# ============================================================

PAGE_X = PAGE_MARGIN_LEFT
PAGE_Y = PAGE_MARGIN_BOTTOM
PAGE_WIDTH = CONTENT_WIDTH
PAGE_HEIGHT = CONTENT_HEIGHT


# ============================================================
# PAGE DIMENSIONS
# ============================================================

HEADER_HEIGHT = 12 * mm
FOOTER_HEIGHT = 6 * mm

PAGE_SECTION_GAP = 1.2 * mm
ISSUE_GAP = 1.2 * mm
COLUMN_GAP = 1.2 * mm

QUESTION_PANEL_HEIGHT = 21 * mm

# 86% curiosity area and 14% GS Mapping.
GS_MAPPING_RATIO = 0.15

# Equal-width Knowledge Points and right-side columns.
KNOWLEDGE_COLUMN_RATIO = 0.50

# Within the right column:
# 75% Quick Facts and 25% Key Takeaway.
QUICK_FACTS_RATIO = 0.75


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
# SINGLE ISSUE LAYOUT
# ============================================================

@dataclass(frozen=True, slots=True)
class CompactIssueLayout:
    panel: Rect

    question_panel: Rect
    curiosity_box: Rect
    gs_mapping: Rect

    content: Rect
    knowledge_points: Rect
    right_column: Rect
    quick_facts: Rect
    takeaway: Rect


# ============================================================
# COMPLETE PAGE LAYOUT
# ============================================================

@dataclass(frozen=True, slots=True)
class CompactPageLayout:
    page: Rect

    header: Rect
    footer: Rect
    body: Rect

    top_issue: CompactIssueLayout
    bottom_issue: CompactIssueLayout


# ============================================================
# ISSUE GEOMETRY
# ============================================================

def build_compact_issue_layout(
    panel: Rect,
) -> CompactIssueLayout:

    # The issue begins directly with the question panel.
    # No separate Issue Title is displayed.
    question_panel = Rect(
        x=panel.x,
        y=panel.top - QUESTION_PANEL_HEIGHT,
        width=panel.width,
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

    content_top = (
        question_panel.y
        - PAGE_SECTION_GAP
    )

    content = Rect(
        x=panel.x,
        y=panel.y,
        width=panel.width,
        height=max(
            0,
            content_top - panel.y,
        ),
    )

    knowledge_points, right_column = (
        content.split_vertical(
            left_ratio=KNOWLEDGE_COLUMN_RATIO,
            gap=COLUMN_GAP,
        )
    )

    available_right_height = max(
        0,
        right_column.height
        - PAGE_SECTION_GAP,
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
        x=right_column.x,
        y=right_column.top
        - quick_facts_height,
        width=right_column.width,
        height=quick_facts_height,
    )

    takeaway = Rect(
        x=right_column.x,
        y=right_column.y,
        width=right_column.width,
        height=takeaway_height,
    )

    return CompactIssueLayout(
        panel=panel,
        question_panel=question_panel,
        curiosity_box=curiosity_box,
        gs_mapping=gs_mapping,
        content=content,
        knowledge_points=knowledge_points,
        right_column=right_column,
        quick_facts=quick_facts,
        takeaway=takeaway,
    )


# ============================================================
# FULL PAGE GEOMETRY
# ============================================================

def build_compact_page_layout() -> CompactPageLayout:
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

    body_top = (
        header.y
        - PAGE_SECTION_GAP
    )

    body_bottom = (
        footer.top
        + PAGE_SECTION_GAP
    )

    body = Rect(
        x=page.x,
        y=body_bottom,
        width=page.width,
        height=max(
            0,
            body_top - body_bottom,
        ),
    )

    issue_height = (
        body.height
        - ISSUE_GAP
    ) / 2

    bottom_panel = Rect(
        x=body.x,
        y=body.y,
        width=body.width,
        height=issue_height,
    )

    top_panel = Rect(
        x=body.x,
        y=bottom_panel.top + ISSUE_GAP,
        width=body.width,
        height=issue_height,
    )

    return CompactPageLayout(
        page=page,
        header=header,
        footer=footer,
        body=body,
        top_issue=build_compact_issue_layout(
            top_panel,
        ),
        bottom_issue=build_compact_issue_layout(
            bottom_panel,
        ),
    )


# ============================================================
# BOX DRAWING
# ============================================================

def draw_compact_box(
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

    canvas.setStrokeColor(
        stroke_color,
    )
    canvas.setFillColor(
        fill_color,
    )
    canvas.setLineWidth(
        border_width,
    )

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


def draw_compact_vertical_divider(
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
        INTERNAL_DIVIDER_COLOR,
    )
    canvas.setLineWidth(
        INTERNAL_DIVIDER_WIDTH,
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

_COMPACT_PAGE_LAYOUT = build_compact_page_layout()


def get_compact_page_layout() -> CompactPageLayout:
    return _COMPACT_PAGE_LAYOUT