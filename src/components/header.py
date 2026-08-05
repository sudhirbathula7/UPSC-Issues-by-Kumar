from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from src.pdf.helpers import (
    draw_text,
    fit_font_size,
)
from src.pdf.logo_loader import draw_logo
from src.pdf.page_setup import Rect
from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    HEADER_CODE_SIZE,
    HEADER_DATE_SIZE,
    HEADER_SUBTITLE_SIZE,
    HEADER_TITLE_SIZE_FULL,
    HEADER_TITLE_SIZE_HALF,
)


@dataclass(frozen=True)
class HeaderData:
    title: str
    subtitle: str
    publication_date: str
    edition_code: str


# ============================================================
# HEADER
# ============================================================

def draw_header(
    canvas: Canvas,
    rect: Rect,
    data: HeaderData,
    compact: bool = False,
    show_bottom_line: bool = True,
) -> None:
    padding_x = 2 * mm
    padding_y = 1 * mm

    inner = Rect(
        x=rect.x + padding_x,
        y=rect.y + padding_y,
        width=rect.width - 2 * padding_x,
        height=max(
            0,
            rect.height - 2 * padding_y,
        ),
    )

    # --------------------------------------------------------
    # OPTIONAL BOTTOM DIVIDER
    # --------------------------------------------------------

    if show_bottom_line:
        canvas.saveState()

        canvas.setStrokeColor(BLACK)
        canvas.setLineWidth(0.45)

        canvas.line(
            rect.x,
            rect.y,
            rect.right,
            rect.y,
        )

        canvas.restoreState()

    # --------------------------------------------------------
    # BRAND LOGO
    # --------------------------------------------------------

    logo_size = (
        13 * mm
        if compact
        else 14* mm
    )

    logo_rect = Rect(
        x=inner.x,
        y=(
            inner.centre_y
            - logo_size / 2
        ),
        width=logo_size,
        height=logo_size,
    )

    draw_logo(
        canvas=canvas,
        filename="brand_logo.png",
        rect=logo_rect,
        preserve_aspect_ratio=True,
    )

    # --------------------------------------------------------
    # TITLE + SUBTITLE
    # --------------------------------------------------------

    title_x = (
        logo_rect.right
        + 2.5 * mm
    )

    title_area_width = (
        inner.width * 0.46
    )

    preferred_title_size = (
        HEADER_TITLE_SIZE_HALF
        if compact
        else HEADER_TITLE_SIZE_FULL
    )

    fitted_title_size = fit_font_size(
        text=data.title,
        font_name=FONT_BOLD,
        preferred_size=preferred_title_size,
        available_width=title_area_width,
        minimum_size=10.5,
    )

    title_baseline = (
        inner.centre_y
        + 1.1 * mm
    )

    draw_text(
        canvas=canvas,
        text=data.title,
        x=title_x,
        y=title_baseline,
        font_name=FONT_BOLD,
        font_size=fitted_title_size,
        color=BLACK,
    )

    fitted_subtitle_size = fit_font_size(
        text=data.subtitle,
        font_name=FONT_BOLD,
        preferred_size=HEADER_SUBTITLE_SIZE,
        available_width=title_area_width,
        minimum_size=6.5,
    )

    subtitle_baseline = (
        inner.y
        + 1.15 * mm
    )

    draw_text(
        canvas=canvas,
        text=data.subtitle,
        x=title_x,
        y=subtitle_baseline,
        font_name=FONT_BOLD,
        font_size=fitted_subtitle_size,
        color=BLACK,
    )

    # --------------------------------------------------------
    # RIGHT METADATA
    # --------------------------------------------------------

    metadata_right = inner.right

    date_text = (
        f"Daily Edition | "
        f"{data.publication_date}"
    )

    fitted_date_size = fit_font_size(
        text=date_text,
        font_name=FONT_BOLD,
        preferred_size=HEADER_DATE_SIZE,
        available_width=58 * mm,
        minimum_size=6.5,
    )

    fitted_code_size = fit_font_size(
        text=data.edition_code,
        font_name=FONT_BOLD,
        preferred_size=HEADER_CODE_SIZE,
        available_width=30 * mm,
        minimum_size=6.5,
    )

    date_text_width = canvas.stringWidth(
        date_text,
        FONT_BOLD,
        fitted_date_size,
    )

    calendar_size = (
        6.7 * mm
        if compact
        else 7.2 * mm
    )

    calendar_gap = 1.7 * mm

    calendar_rect = Rect(
        x=(
            metadata_right
            - date_text_width
            - calendar_gap
            - calendar_size
        ),
        y=(
            inner.centre_y
            - calendar_size / 2
        ),
        width=calendar_size,
        height=calendar_size,
    )

    draw_logo(
        canvas=canvas,
        filename="calendar.svg",
        rect=calendar_rect,
        preserve_aspect_ratio=True,
    )

    date_baseline = (
        inner.centre_y
        + 1.5 * mm
    )

    code_baseline = (
        inner.centre_y
        - 2.2 * mm
    )

    canvas.saveState()

    canvas.setFillColor(BLACK)

    canvas.setFont(
        FONT_BOLD,
        fitted_date_size,
    )

    canvas.drawRightString(
        metadata_right,
        date_baseline,
        date_text,
    )

    canvas.setFont(
        FONT_BOLD,
        fitted_code_size,
    )

    canvas.drawRightString(
        metadata_right,
        code_baseline,
        data.edition_code,
    )

    canvas.restoreState()