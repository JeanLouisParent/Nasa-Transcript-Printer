"""Formatting helpers for transcript blocks."""

from __future__ import annotations

from typing import Any

from constants import (
    CONTINUATION_COL,
    META_COL,
    SPEAKER_COL,
    TEXT_COL,
    TIMESTAMP_COL,
)


def parse_pages_arg(pages_arg: str) -> list[int]:
    pages: list[int] = []
    if not pages_arg:
        return pages

    for part in pages_arg.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            start_s, end_s = token.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            step = 1 if end >= start else -1
            pages.extend(range(start, end + step, step))
        else:
            pages.append(int(token))
    return pages


def wrap_text(text: str, width: int, space_len: int = 1) -> list[str]:
    if width <= 0:
        return [text]

    words = text.split()
    if not words:
        return []

    lines: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        word_len = len(word)
        tentative_len = word_len if not current else current_len + space_len + word_len
        if tentative_len <= width or not current:
            current.append(word)
            current_len = tentative_len
            continue
        lines.append((" " * space_len).join(current))
        current = [word]
        current_len = word_len

    if current:
        lines.append((" " * space_len).join(current))

    return lines


def align_center(line: str, width: int) -> str:
    if len(line) >= width:
        return line
    pad = (width - len(line)) // 2
    return " " * pad + line


def format_comm(block: dict[str, Any], columns: int, wrap_space_len: int = 1) -> list[str]:
    timestamp = block.get("timestamp", "").strip()
    speaker = block.get("speaker", "").strip()
    text = block.get("text", "").strip()
    location = block.get("location")

    prefix = ""
    if timestamp:
        prefix += timestamp
    if len(prefix) < SPEAKER_COL:
        prefix += " " * (SPEAKER_COL - len(prefix))
    prefix += speaker
    if len(prefix) < TEXT_COL:
        prefix += " " * (TEXT_COL - len(prefix))
    if location:
        prefix += f"({location}) "

    available = columns - len(prefix)
    wrapped = wrap_text(text, available, space_len=wrap_space_len)
    if not wrapped:
        return [prefix.rstrip()]

    lines = [prefix + wrapped[0]]
    if len(wrapped) > 1:
        continuation_prefix = " " * TEXT_COL
        lines.extend(continuation_prefix + part for part in wrapped[1:])
    return lines


def format_indented(text: str, indent_col: int, columns: int, wrap_space_len: int = 1) -> list[str]:
    stripped = text.strip()
    wrapped = wrap_text(stripped, columns - indent_col, space_len=wrap_space_len)
    if not wrapped:
        return ["".ljust(indent_col)]
    prefix = " " * indent_col
    return [prefix + line for line in wrapped]


def format_annotation(text: str, columns: int, wrap_space_len: int = 1) -> list[str]:
    wrapped = wrap_text(text.strip(), columns, space_len=wrap_space_len)
    return [align_center(line, columns) for line in wrapped]


def format_footer(text: str, columns: int, wrap_space_len: int = 1) -> list[str]:
    wrapped = wrap_text(text.strip(), columns - TIMESTAMP_COL, space_len=wrap_space_len)
    prefix = " " * TIMESTAMP_COL
    return [prefix + line for line in wrapped]


def build_page_lines(
    page: dict[str, Any],
    columns: int,
    space_len: int,
    mission_style: dict[str, Any],
) -> list[str]:
    lines: list[str] = []
    header = page.get("header", {})
    tape = header.get("tape")
    page_num = header.get("page")
    is_title = header.get("is_apollo_title")
    title_line = str(mission_style.get("title_line", "AIR-TO-GROUND VOICE TRANSCRIPTION"))
    goss_line_text = str(mission_style.get("goss_line", "(GOSS NET 1)"))
    annotation_top_blank_lines = int(mission_style.get("annotation_top_blank_lines", 1))
    end_of_tape_indent_col = int(mission_style.get("end_of_tape_indent_col", TIMESTAMP_COL))

    if tape or is_title:
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

    for block in page.get("blocks", []):
        block_type = block.get("type")
        text = block.get("text", "")

        if block_type == "comm":
            lines.extend(format_comm(block, columns, wrap_space_len=space_len))
            lines.append("")
            continue

        if block_type == "annotation":
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend([""] * annotation_top_blank_lines)
            lines.extend(format_annotation(text, columns, wrap_space_len=space_len))
            lines.extend(["", ""])
            continue

        if block_type == "meta":
            meta_type = block.get("meta_type", "")
            if meta_type == "end_of_tape" or text.strip() == "END OF TAPE":
                lines.extend(
                    format_indented(
                        text,
                        end_of_tape_indent_col,
                        columns,
                        wrap_space_len=space_len,
                    )
                )
            else:
                lines.extend(format_indented(text, META_COL, columns, wrap_space_len=space_len))
            lines.append("")
            continue

        if block_type == "continuation":
            lines.extend(format_indented(text, CONTINUATION_COL, columns, wrap_space_len=space_len))
            lines.append("")
            continue

        if block_type == "footer":
            lines.extend(format_footer(text, columns, wrap_space_len=space_len))
            lines.append("")
            continue

        lines.extend(format_indented(text, CONTINUATION_COL, columns, wrap_space_len=space_len))
        lines.append("")

    return lines
