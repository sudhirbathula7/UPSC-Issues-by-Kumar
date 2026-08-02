from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

from src.pdf.page_setup import Rect


LOGO_DIRECTORY = (
    Path(__file__).resolve().parent
    / "assets"
    / "logos"
)


def get_logo_path(
    filename: str,
) -> Path:
    path = LOGO_DIRECTORY / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Logo file not found: {path}"
        )

    return path


@lru_cache(maxsize=32)
def _load_svg(
    path_string: str,
):
    drawing = svg2rlg(path_string)

    if drawing is None:
        raise ValueError(
            f"Unable to load SVG logo: {path_string}"
        )

    return drawing


@lru_cache(maxsize=32)
def _load_raster(
    path_string: str,
) -> ImageReader:
    return ImageReader(path_string)


def draw_logo(
    canvas: Canvas,
    filename: str,
    rect: Rect,
    *,
    preserve_aspect_ratio: bool = True,
) -> None:
    """
    Draw an SVG or raster logo inside a rectangle.

    Supported:
    - SVG
    - PNG
    - JPG
    - JPEG
    """

    path = get_logo_path(filename)
    suffix = path.suffix.casefold()

    if suffix == ".svg":
        drawing = _load_svg(
            str(path)
        )

        source_width = float(
            drawing.width or 1
        )
        source_height = float(
            drawing.height or 1
        )

        scale_x = (
            rect.width
            / source_width
        )

        scale_y = (
            rect.height
            / source_height
        )

        if preserve_aspect_ratio:
            scale = min(
                scale_x,
                scale_y,
            )

            drawn_width = (
                source_width
                * scale
            )

            drawn_height = (
                source_height
                * scale
            )

            draw_x = (
                rect.x
                + (
                    rect.width
                    - drawn_width
                )
                / 2
            )

            draw_y = (
                rect.y
                + (
                    rect.height
                    - drawn_height
                )
                / 2
            )

            canvas.saveState()

            canvas.translate(
                draw_x,
                draw_y,
            )

            canvas.scale(
                scale,
                scale,
            )

            renderPDF.draw(
                drawing,
                canvas,
                0,
                0,
            )

            canvas.restoreState()

            return

        canvas.saveState()

        canvas.translate(
            rect.x,
            rect.y,
        )

        canvas.scale(
            scale_x,
            scale_y,
        )

        renderPDF.draw(
            drawing,
            canvas,
            0,
            0,
        )

        canvas.restoreState()

        return

    if suffix in {
        ".png",
        ".jpg",
        ".jpeg",
    }:
        image = _load_raster(
            str(path)
        )

        canvas.drawImage(
            image,
            rect.x,
            rect.y,
            width=rect.width,
            height=rect.height,
            preserveAspectRatio=(
                preserve_aspect_ratio
            ),
            anchor="c",
            mask="auto",
        )

        return

    raise ValueError(
        f"Unsupported logo format: {path.suffix}"
    )