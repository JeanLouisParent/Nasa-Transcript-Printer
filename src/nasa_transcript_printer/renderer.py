"""PDF rendering for transcript pages."""

from __future__ import annotations

from reportlab.lib.pagesizes import portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .layout import build_page_lines


def resolve_page_selection(
    pages_by_num: dict[int, dict],
    pages: list[int],
    page_start: int,
    page_end: int | None,
    pdf_pages: list[int],
    pdf_start: int | None,
    pdf_end: int | None,
    pdf_offset: int,
) -> list[int]:
    if pdf_pages:
        selected = [page - pdf_offset for page in pdf_pages]
    elif pdf_start is not None:
        end = pdf_end if pdf_end is not None else pdf_start
        step = 1 if end >= pdf_start else -1
        selected = [page - pdf_offset for page in range(pdf_start, end + step, step)]
    elif pages:
        selected = pages
    else:
        end = page_end if page_end is not None else max(pages_by_num.keys())
        step = 1 if end >= page_start else -1
        selected = list(range(page_start, end + step, step))

    existing = [page for page in selected if page in pages_by_num]
    if not existing:
        raise ValueError("No matching pages found for the given selection.")
    return existing


def render_pdf(
    *,
    pages_by_num: dict[int, dict],
    output_path: str,
    selected_pages: list[int],
    columns: int,
    space_len: int,
    font_path: str,
    font_size: float,
    left_margin_pt: float | None,
    line_height_multiplier: float,
    fit_to_page: bool,
    page_width_pt: float,
    page_height_pt: float,
    top_margin_pt: float,
    bottom_margin_pt: float,
    dpi: int,
) -> None:
    if font_path:
        pdfmetrics.registerFont(TTFont("CustomFont", font_path))
        font_name = "CustomFont"
    else:
        font_name = "Courier"

    page_width, page_height = portrait((page_width_pt, page_height_pt))

    char_width = pdfmetrics.stringWidth("M", font_name, font_size)
    text_width = char_width * columns
    if left_margin_pt is None:
        left_margin = max(0.0, (page_width - text_width) / 2)
    else:
        left_margin = max(0.0, left_margin_pt)

    base_line_height = font_size * line_height_multiplier
    top_y = page_height - top_margin_pt

    pdf = canvas.Canvas(output_path, pagesize=(page_width, page_height))
    pdf.setSubject(f"Rendered with reference DPI {dpi}")
    pdf.setFont(font_name, font_size)

    for page_num in selected_pages:
        page = pages_by_num[page_num]
        lines = build_page_lines(page, columns, space_len)

        line_height = base_line_height
        max_lines = int((page_height - top_margin_pt - bottom_margin_pt) / line_height)

        if fit_to_page and len(lines) > max_lines and len(lines) > 1:
            line_height = (page_height - top_margin_pt - bottom_margin_pt) / (len(lines) - 1)
        else:
            lines = lines[:max_lines]

        y = top_y
        for line in lines:
            pdf.drawString(left_margin, y, line)
            y -= line_height
        pdf.showPage()
        pdf.setFont(font_name, font_size)

    pdf.save()
