from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas

from src.config import (
    PAGE_MARGIN_BOTTOM,
    PAGE_MARGIN_LEFT,
    PAGE_MARGIN_RIGHT,
    PAGE_MARGIN_TOP,
    PAGE_WIDTH,
    PAGE_HEIGHT,
)


# ============================================================
# RECT
# ============================================================

@dataclass(slots=True)
class Rect:

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self):
        return self.x + self.width

    @property
    def top(self):
        return self.y + self.height

    @property
    def centre_x(self):
        return self.x + self.width / 2

    @property
    def centre_y(self):
        return self.y + self.height / 2

    def inset(
        self,
        horizontal: float = 0,
        vertical: float = 0,
    ):
        return Rect(
            self.x + horizontal,
            self.y + vertical,
            self.width - horizontal * 2,
            self.height - vertical * 2,
        )

    def split_vertical(
        self,
        left_ratio: float,
        gap: float = 0,
    ):
        left_width = (
            self.width - gap
        ) * left_ratio

        right_width = (
            self.width - gap
        ) - left_width

        left = Rect(
            self.x,
            self.y,
            left_width,
            self.height,
        )

        right = Rect(
            left.right + gap,
            self.y,
            right_width,
            self.height,
        )

        return left, right

    def split_horizontal(
        self,
        top_ratio: float,
        gap: float = 0,
    ):
        top_height = (
            self.height - gap
        ) * top_ratio

        bottom_height = (
            self.height - gap
        ) - top_height

        top = Rect(
            self.x,
            self.top - top_height,
            self.width,
            top_height,
        )

        bottom = Rect(
            self.x,
            self.y,
            self.width,
            bottom_height,
        )

        return top, bottom


# ============================================================
# CANVAS
# ============================================================

def create_canvas(
    filename: str,
):
    return Canvas(
        filename,
        pagesize=A4,
    )


def begin_page(
    canvas: Canvas,
):
    canvas.setTitle(
        "UPSC Issues by Kumar"
    )


def finish_page(
    canvas: Canvas,
):
    canvas.showPage()


def page_content_rect():

    return Rect(
        PAGE_MARGIN_LEFT,
        PAGE_MARGIN_BOTTOM,
        PAGE_WIDTH
        - PAGE_MARGIN_LEFT
        - PAGE_MARGIN_RIGHT,
        PAGE_HEIGHT
        - PAGE_MARGIN_TOP
        - PAGE_MARGIN_BOTTOM,
    )