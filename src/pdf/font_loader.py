from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont(
            "Calibri",
            r"C:\Windows\Fonts\calibri.ttf",
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "Calibri-Bold",
            r"C:\Windows\Fonts\calibrib.ttf",
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "Calibri-Italic",
            r"C:\Windows\Fonts\calibrii.ttf",
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "Calibri-BoldItalic",
            r"C:\Windows\Fonts\calibriz.ttf",
        )
    )

    # --------------------------------------------------------
    # REGISTER CALIBRI AS A FONT FAMILY
    # --------------------------------------------------------
    # This allows ReportLab Paragraph markup such as:
    #
    # <b>text</b>
    # <i>text</i>
    # <b><i>text</i></b>
    #
    # to switch automatically to the correct Calibri font face.

    pdfmetrics.registerFontFamily(
        "Calibri",
        normal="Calibri",
        bold="Calibri-Bold",
        italic="Calibri-Italic",
        boldItalic="Calibri-BoldItalic",
    )