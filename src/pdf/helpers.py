from __future__ import annotations

from functools import lru_cache

from reportlab.lib.enums import (
    TA_CENTER,
    TA_JUSTIFY,
    TA_LEFT,
    TA_RIGHT,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph

from src.pdf.theme import (
    BLACK,
    FONT_BOLD,
    FONT_REGULAR,
)


# ============================================================
# PARAGRAPH STYLE
# ============================================================

@lru_cache(maxsize=256)
def paragraph_style(
    name: str,
    font_name: str = FONT_REGULAR,
    font_size: float = 8.5,
    leading: float = 10,
    text_color=BLACK,
    alignment: int = TA_LEFT,
):

    return ParagraphStyle(
        name=name,
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        textColor=text_color,
        alignment=alignment,
        spaceBefore=0,
        spaceAfter=0,
        leftIndent=0,
        rightIndent=0,
    )


# ============================================================
# PARAGRAPH
# ============================================================

def draw_paragraph(
    canvas,
    text: str,
    rect,
    style,
    vertical_align: str = "top",
):

    paragraph = Paragraph(text, style)

    width, height = paragraph.wrap(
        rect.width,
        rect.height,
    )

    if vertical_align == "middle":
        y = rect.y + (rect.height - height) / 2

    elif vertical_align == "bottom":
        y = rect.y

    else:
        y = rect.top - height

    paragraph.drawOn(
        canvas,
        rect.x,
        y,
    )


# ============================================================
# TEXT
# ============================================================

def draw_text(
    canvas,
    text,
    x,
    y,
    font_name=FONT_REGULAR,
    font_size=8.5,
    color=BLACK,
):

    canvas.setFillColor(color)
    canvas.setFont(font_name, font_size)
    canvas.drawString(x, y, text)


def draw_centered_text(
    canvas,
    text,
    x,
    y,
    font_name=FONT_REGULAR,
    font_size=8.5,
    color=BLACK,
):

    canvas.setFillColor(color)
    canvas.setFont(font_name, font_size)
    canvas.drawCentredString(
        x,
        y,
        text,
    )


def draw_right_text(
    canvas,
    text,
    x,
    y,
    font_name=FONT_REGULAR,
    font_size=8.5,
    color=BLACK,
):

    canvas.setFillColor(color)
    canvas.setFont(font_name, font_size)
    canvas.drawRightString(
        x,
        y,
        text,
    )


# ============================================================
# FONT FIT
# ============================================================

def fit_font_size(
    text: str,
    font_name: str,
    preferred_size: float,
    available_width: float,
    minimum_size: float = 5.5,
):

    size = preferred_size

    while size >= minimum_size:

        width = stringWidth(
            text,
            font_name,
            size,
        )

        if width <= available_width:
            return size

        size -= 0.25

    return minimum_size