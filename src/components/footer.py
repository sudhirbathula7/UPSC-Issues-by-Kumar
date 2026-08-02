from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from src.pdf.helpers import (
    draw_centered_text,
    draw_right_text,
    draw_text,
    fit_font_size,
)
from src.pdf.logo_loader import draw_logo
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
    FOOTER_SIZE,
    MEDIUM_GREY,
)


TELEGRAM_HANDLE = "@upscissuesbykumar"


@dataclass(frozen=True)
class FooterData:
    brand_name: str
    publication_code: str
    page_number: int
    total_pages: int


# ============================================================
# FOOTER
# ============================================================

def draw_footer(
    canvas: Canvas,
    rect: Rect,
    data: FooterData,
) -> None:
    horizontal_padding = 1.5 * mm

    inner = Rect(
        x=rect.x + horizontal_padding,
        y=rect.y,
        width=rect.width - 2 * horizontal_padding,
        height=rect.height,
    )

    # --------------------------------------------------------
    # TOP DIVIDER
    # --------------------------------------------------------

    canvas.saveState()

    canvas.setStrokeColor(BLACK)
    canvas.setLineWidth(0.6)

    canvas.line(
        rect.x,
        rect.top,
        rect.right,
        rect.top,
    )

    canvas.restoreState()

    # --------------------------------------------------------
    # COMMON BASELINE
    # --------------------------------------------------------

    text_baseline = (
        rect.y
        + (rect.height - FOOTER_SIZE) / 2
        + 1
    )

    # --------------------------------------------------------
    # LEFT: TELEGRAM ICON + HANDLE
    # --------------------------------------------------------

    left_width = inner.width * 0.38

    telegram_icon_size = 3.8 * mm
    telegram_gap = 1.2 * mm

    telegram_rect = Rect(
        x=inner.x,
        y=(
            rect.centre_y
            - telegram_icon_size / 2
        ),
        width=telegram_icon_size,
        height=telegram_icon_size,
    )

    draw_logo(
        canvas=canvas,
        filename="telegram.svg",
        rect=telegram_rect,
        preserve_aspect_ratio=True,
    )

    handle_x = (
        telegram_rect.right
        + telegram_gap
    )

    available_handle_width = (
        left_width
        - telegram_icon_size
        - telegram_gap
    )

    fitted_handle_size = fit_font_size(
        text=TELEGRAM_HANDLE,
        font_name=FONT_BOLD,
        preferred_size=FOOTER_SIZE,
        available_width=available_handle_width,
        minimum_size=5.5,
    )

    draw_text(
        canvas=canvas,
        text=TELEGRAM_HANDLE,
        x=handle_x,
        y=text_baseline,
        font_name=FONT_BOLD,
        font_size=fitted_handle_size,
        color=BLACK,
    )

    # --------------------------------------------------------
    # CENTRE: PUBLICATION CODE
    # --------------------------------------------------------

    draw_centered_text(
        canvas=canvas,
        text=data.publication_code,
        x=inner.centre_x,
        y=text_baseline,
        font_name=FONT_REGULAR,
        font_size=FOOTER_SIZE,
        color=MEDIUM_GREY,
    )

    # --------------------------------------------------------
    # RIGHT: PAGE NUMBER
    # --------------------------------------------------------

    page_text = (
        f"Page {data.page_number} "
        f"of {data.total_pages}"
    )

    right_width = inner.width * 0.25

    fitted_page_size = fit_font_size(
        text=page_text,
        font_name=FONT_BOLD,
        preferred_size=FOOTER_SIZE,
        available_width=right_width,
        minimum_size=5.5,
    )

    draw_right_text(
        canvas=canvas,
        text=page_text,
        x=inner.right,
        y=text_baseline,
        font_name=FONT_BOLD,
        font_size=fitted_page_size,
        color=BLACK,
    )
    