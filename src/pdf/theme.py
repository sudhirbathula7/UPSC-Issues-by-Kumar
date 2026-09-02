from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import mm


# ============================================================
# COLOURS
# ============================================================

BLACK: Final[Color] = HexColor("#111827")
TEXT_BLACK: Final[Color] = HexColor("#172033")

HEADING_BLUE: Final[Color] = HexColor("#102A5C")

DARK_GREY: Final[Color] = HexColor("#4B5563")
MEDIUM_GREY: Final[Color] = HexColor("#7A8699")

LIGHT_GREY: Final[Color] = HexColor("#B8C5D8")
VERY_LIGHT_GREY: Final[Color] = HexColor("#E7ECF3")

WHITE: Final[Color] = HexColor("#FFFFFF")


# ============================================================
# COMPATIBILITY COLOURS
# ============================================================

NAVY: Final[Color] = HEADING_BLUE
DARK_NAVY: Final[Color] = HEADING_BLUE

BORDER_GREY: Final[Color] = LIGHT_GREY
LIGHT_BORDER: Final[Color] = LIGHT_GREY
DIVIDER_GREY: Final[Color] = LIGHT_GREY

ANSWER_BLUE: Final[Color] = HEADING_BLUE
LIGHT_BLUE: Final[Color] = WHITE
OFF_WHITE: Final[Color] = WHITE


# ============================================================
# FONTS
# ============================================================

FONT_REGULAR: Final[str] = "Calibri"
FONT_BOLD: Final[str] = "Calibri-Bold"
FONT_ITALIC: Final[str] = "Calibri-Italic"
FONT_BOLD_ITALIC: Final[str] = "Calibri-BoldItalic"

FONT_OBLIQUE: Final[str] = FONT_ITALIC
FONT_BOLD_OBLIQUE: Final[str] = FONT_BOLD_ITALIC


# ============================================================
# HEADER
# ============================================================

HEADER_TITLE_SIZE: Final[float] = 20
HEADER_TITLE_SIZE_FULL: Final[float] = 20
HEADER_TITLE_SIZE_HALF: Final[float] = 19

HEADER_SUBTITLE_SIZE: Final[float] = 9
HEADER_DATE_LABEL_SIZE: Final[float] = 9
HEADER_DATE_SIZE: Final[float] = 9
HEADER_CODE_SIZE: Final[float] = 9

HEADER_RADIUS: Final[float] = 2 * mm


# ============================================================
# QUESTION
# ============================================================

QUESTION_SIZE: Final[float] = 15
QUESTION_LEADING: Final[float] = 18

QUESTION_SIZE_FULL: Final[float] = 15
QUESTION_LEADING_FULL: Final[float] = 18

QUESTION_SIZE_HALF: Final[float] = 14
QUESTION_LEADING_HALF: Final[float] = 17

ANCHOR_LABEL_SIZE: Final[float] = 9
ANCHOR_SIZE: Final[float] = 9
ANCHOR_TEXT_SIZE: Final[float] = 9
ANCHOR_LEADING: Final[float] = 11


# ============================================================
# GS MAPPING
# ============================================================

GS_PAPER_SIZE: Final[float] = 10
GS_SUBJECT_SIZE: Final[float] = 9
GS_TOPIC_SIZE: Final[float] = 8
GS_TOPIC_LEADING: Final[float] = 10


# ============================================================
# SECTION TITLES
# ============================================================

SECTION_TITLE_SIZE: Final[float] = 11

SECTION_HEADING_SIZE_FULL: Final[float] = 11
SECTION_HEADING_SIZE_HALF: Final[float] = 10


# ============================================================
# KNOWLEDGE POINTS
# ============================================================

KNOWLEDGE_NUMBER_SIZE: Final[float] = 14
KNOWLEDGE_NUMBER_SIZE_FULL: Final[float] = 14
KNOWLEDGE_NUMBER_SIZE_HALF: Final[float] = 13

KNOWLEDGE_HEADING_SIZE: Final[float] = 10

KNOWLEDGE_TEXT_SIZE: Final[float] = 8.8
KNOWLEDGE_LEADING: Final[float] = 10

KNOWLEDGE_TEXT_SIZE_FULL: Final[float] = 8.8
KNOWLEDGE_LEADING_FULL: Final[float] = 10

KNOWLEDGE_TEXT_SIZE_HALF: Final[float] = 8.8
KNOWLEDGE_LEADING_HALF: Final[float] = 10


# ============================================================
# QUICK FACTS
# ============================================================

QUICK_FACT_SIZE: Final[float] = 8.8
QUICK_FACT_LEADING: Final[float] = 10

QUICK_FACT_SIZE_FULL: Final[float] = 8.8
QUICK_FACT_LEADING_FULL: Final[float] = 10

QUICK_FACT_SIZE_HALF: Final[float] = 8.8
QUICK_FACT_LEADING_HALF: Final[float] = 10


# ============================================================
# KEY TAKEAWAY
# ============================================================

TAKEAWAY_SIZE: Final[float] = 8.8
TAKEAWAY_LEADING: Final[float] = 10

TAKEAWAY_SIZE_FULL: Final[float] = 8.8
TAKEAWAY_LEADING_FULL: Final[float] = 10

TAKEAWAY_SIZE_HALF: Final[float] = 8.8
TAKEAWAY_LEADING_HALF: Final[float] = 10


# ============================================================
# MAINS ANSWER
# ============================================================

MAINS_QUESTION_SIZE: Final[float] = 8
MAINS_TEXT_SIZE: Final[float] = 8

MAINS_LEADING: Final[float] = 10
MAINS_TEXT_LEADING: Final[float] = 10

MAINS_WORD_NOTE_SIZE: Final[float] = 7


# ============================================================
# MCQS
# ============================================================

MCQ_QUESTION_SIZE: Final[float] = 8
MCQ_OPTION_SIZE: Final[float] = 8

MCQ_LEADING: Final[float] = 10
MCQ_ANSWER_SIZE: Final[float] = 8


# ============================================================
# FOOTER
# ============================================================

FOOTER_SIZE: Final[float] = 7


# ============================================================
# BORDERS AND SHAPES
# ============================================================

BOX_RADIUS: Final[float] = 2 * mm

BOX_BORDER_WIDTH: Final[float] = 0.42
DIVIDER_WIDTH: Final[float] = 0.35

ICON_STROKE: Final[float] = 1.1

OUTER_BORDER_WIDTH: Final[float] = 0.45
INNER_BORDER_WIDTH: Final[float] = BOX_BORDER_WIDTH
ICON_STROKE_WIDTH: Final[float] = ICON_STROKE


# ============================================================
# PADDING
# ============================================================

BOX_PADDING_X: Final[float] = 4 * mm
BOX_PADDING_Y: Final[float] = 3 * mm
TEXT_PADDING: Final[float] = 2 * mm

QUESTION_PADDING_X: Final[float] = 4 * mm
QUESTION_PADDING_Y: Final[float] = 3 * mm

COLUMN_GAP: Final[float] = 2 * mm


# ============================================================
# THEME OBJECT
# ============================================================

@dataclass(frozen=True)
class Theme:
    text: Color = TEXT_BLACK
    heading: Color = HEADING_BLUE
    border: Color = LIGHT_GREY
    divider: Color = LIGHT_GREY
    background: Color = WHITE

    regular_font: str = FONT_REGULAR
    bold_font: str = FONT_BOLD
    italic_font: str = FONT_ITALIC
    bold_italic_font: str = FONT_BOLD_ITALIC


THEME = Theme()