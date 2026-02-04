"""PDF rendering for transcript pages."""

from __future__ import annotations

from reportlab.lib.pagesizes import portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from layout import align_center, build_page_lines, wrap_text


def is_note_page(page: dict, mission_style: dict) -> bool:
    page_num = page.get("header", {}).get("page")
    note_pages = {int(p) for p in mission_style.get("note_pages", [])}
    return page_num in note_pages


def is_centered_rest_period_page(page: dict, mission_style: dict) -> bool:
    header = page.get("header", {})
    if header.get("page_type") != "rest_period":
        return False
    if not bool(mission_style.get("center_rest_period_text", True)):
        return False
    blocks = page.get("blocks", [])
    if not bool(mission_style.get("rest_period_only_when_no_comm", True)):
        return True
    return all(block.get("type") != "comm" for block in blocks)


def build_rest_period_lines(page: dict, columns: int, space_len: int) -> list[str]:
    blocks = page.get("blocks", [])
    texts: list[str] = []
    for block in blocks:
        if block.get("meta_type") == "rest_period":
            text = block.get("text", "").strip()
            if text:
                texts.append(text)
    if not texts:
        for block in blocks:
            text = block.get("text", "").strip()
            if text:
                texts.append(text)

    lines: list[str] = []
    for text in texts:
        wrapped = wrap_text(text, columns, space_len=space_len)
        lines.extend(wrapped)
    return lines


def build_rest_period_header_lines(page: dict, columns: int, mission_style: dict) -> list[str]:
    lines: list[str] = []
    header = page.get("header", {})
    tape = header.get("tape")
    page_num = header.get("page")
    is_title = header.get("is_apollo_title")
    title_line = str(mission_style.get("title_line", "AIR-TO-GROUND VOICE TRANSCRIPTION"))
    goss_line_text = str(mission_style.get("goss_line", "(GOSS NET 1)"))

    if is_title:
        lines.extend([align_center(title_line, columns), "", ""])
    if tape:
        tape_str = f"Tape {tape}"
        if len(goss_line_text) + len(tape_str) + 1 <= columns:
            goss_line = (
                goss_line_text
                + " " * (columns - len(goss_line_text) - len(tape_str))
                + tape_str
            )
        else:
            goss_line = goss_line_text
        lines.append(goss_line)
        lines.append(f"Page {page_num}".rjust(columns))
        lines.extend(["", ""])
    return lines


def build_note_lines(page: dict, columns: int, space_len: int, mission_style: dict) -> list[str]:
    heading = str(mission_style.get("note_heading", "NOTE")).strip()
    lines: list[str] = [align_center(heading, columns), ""]
    block_columns = int(mission_style.get("note_block_columns", columns))
    block_columns = max(1, min(columns, block_columns))
    blocks = page.get("blocks", [])
    body_texts = []
    for block in blocks:
        text = (block.get("text") or "").strip()
        if text:
            body_texts.append(text)
    for text in body_texts:
        wrapped = wrap_text(text, block_columns, space_len=space_len)
        lines.extend(align_center(line, columns) for line in wrapped)
    return lines


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
    faux_bold_pt: float,
    mission_style: dict,
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
        note_page = is_note_page(page, mission_style)
        centered_rest_page = is_centered_rest_period_page(page, mission_style)
        line_height = base_line_height

        if note_page:
            header_lines = build_rest_period_header_lines(page, columns, mission_style)
            note_lines = build_note_lines(page, columns, space_len, mission_style)

            y_header = top_y
            for line in header_lines:
                pdf.drawString(left_margin, y_header, line)
                if faux_bold_pt > 0:
                    pdf.drawString(left_margin + faux_bold_pt, y_header, line)
                y_header -= line_height

            if note_lines:
                if bool(mission_style.get("note_center_vertical", False)):
                    content_height = (len(note_lines) - 1) * line_height
                    y = (page_height + content_height) / 2
                else:
                    top_blanks = int(mission_style.get("note_top_blank_lines", 2))
                    y = y_header - (top_blanks * line_height)
                for line in note_lines:
                    text_width_line = pdfmetrics.stringWidth(line, font_name, font_size)
                    x = max(0.0, (page_width - text_width_line) / 2)
                    pdf.drawString(x, y, line)
                    if faux_bold_pt > 0:
                        pdf.drawString(x + faux_bold_pt, y, line)
                    y -= line_height
        elif centered_rest_page:
            rest_header_lines: list[str] = []
            if bool(mission_style.get("rest_period_keep_header", True)):
                rest_header_lines = build_rest_period_header_lines(page, columns, mission_style)
            rest_lines = build_rest_period_lines(page, columns, space_len)

            y_header = top_y
            for line in rest_header_lines:
                pdf.drawString(left_margin, y_header, line)
                if faux_bold_pt > 0:
                    pdf.drawString(left_margin + faux_bold_pt, y_header, line)
                y_header -= line_height

            if rest_lines:
                content_height = (len(rest_lines) - 1) * line_height
                y = (page_height + content_height) / 2
                for line in rest_lines:
                    text_width_line = pdfmetrics.stringWidth(line, font_name, font_size)
                    x = max(0.0, (page_width - text_width_line) / 2)
                    pdf.drawString(x, y, line)
                    if faux_bold_pt > 0:
                        pdf.drawString(x + faux_bold_pt, y, line)
                    y -= line_height
        else:
            lines = build_page_lines(page, columns, space_len, mission_style)
            max_lines = int((page_height - top_margin_pt - bottom_margin_pt) / line_height)

            if fit_to_page and len(lines) > max_lines and len(lines) > 1:
                line_height = (page_height - top_margin_pt - bottom_margin_pt) / (len(lines) - 1)
            else:
                lines = lines[:max_lines]

            y = top_y
            for line in lines:
                pdf.drawString(left_margin, y, line)
                if faux_bold_pt > 0:
                    pdf.drawString(left_margin + faux_bold_pt, y, line)
                y -= line_height
        pdf.showPage()
        pdf.setFont(font_name, font_size)

    pdf.save()
