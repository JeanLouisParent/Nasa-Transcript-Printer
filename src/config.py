"""Configuration loading and merge utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from constants import (
    BOTTOM_MARGIN_PT,
    COLUMNS,
    DEFAULT_COMMON_CONFIG,
    DEFAULT_DPI,
    DEFAULT_FAUX_BOLD_PT,
    DEFAULT_JSON,
    DEFAULT_MISSION_CONFIG,
    DEFAULT_OUT,
    DEFAULT_START_PAGE,
    LINE_HEIGHT_MULTIPLIER,
    PAGE_SIZE,
    PDF_PAGE_OFFSET,
    SPACE_LEN,
    TIMESTAMP_COL,
    TOP_MARGIN_PT,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def _safe_get(section: dict[str, Any], key: str, default: Any) -> Any:
    value = section.get(key, default)
    return default if value is None else value


def load_config_file(config_path: str) -> dict[str, Any]:
    path = Path(config_path)
    if not path.is_file():
        return {}
    with path.open("rb") as file:
        return tomllib.load(file)


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_merged_config(common_path: str, mission_path: str) -> dict[str, Any]:
    common = load_config_file(common_path)
    mission = load_config_file(mission_path)
    return deep_merge(common, mission)


def config_defaults(config_data: dict[str, Any]) -> dict[str, Any]:
    paths = config_data.get("paths", {})
    pagination = config_data.get("pagination", {})
    font = config_data.get("font", {})
    layout = config_data.get("layout", {})
    page = config_data.get("page", {})
    mission = config_data.get("mission", {})
    special_pages = config_data.get("special_pages", {})

    return {
        "common_config": DEFAULT_COMMON_CONFIG,
        "mission_config": DEFAULT_MISSION_CONFIG,
        "json": _safe_get(paths, "json", DEFAULT_JSON),
        "out": _safe_get(paths, "out", DEFAULT_OUT),
        "start_page": int(_safe_get(pagination, "start_page", DEFAULT_START_PAGE)),
        "end_page": pagination.get("end_page"),
        "pdf_offset": int(_safe_get(pagination, "pdf_offset", PDF_PAGE_OFFSET)),
        "font": _safe_get(font, "path", ""),
        "font_size": float(_safe_get(font, "size", 10.0)),
        "columns": int(_safe_get(layout, "columns", COLUMNS)),
        "space_len": int(_safe_get(layout, "space_len", SPACE_LEN)),
        "line_height_multiplier": float(
            _safe_get(layout, "line_height_multiplier", LINE_HEIGHT_MULTIPLIER)
        ),
        "left_margin_pt": layout.get("left_margin_pt"),
        "fit_to_page": bool(_safe_get(layout, "fit_to_page", True)),
        "faux_bold_pt": float(_safe_get(layout, "faux_bold_pt", DEFAULT_FAUX_BOLD_PT)),
        "dpi": int(_safe_get(page, "dpi", DEFAULT_DPI)),
        "page_width_pt": float(_safe_get(page, "width_pt", PAGE_SIZE[0])),
        "page_height_pt": float(_safe_get(page, "height_pt", PAGE_SIZE[1])),
        "top_margin_pt": float(_safe_get(page, "top_margin_pt", TOP_MARGIN_PT)),
        "bottom_margin_pt": float(_safe_get(page, "bottom_margin_pt", BOTTOM_MARGIN_PT)),
        "title_line": _safe_get(mission, "title_line", "AIR-TO-GROUND VOICE TRANSCRIPTION"),
        "goss_line": _safe_get(mission, "goss_line", "(GOSS NET 1)"),
        "annotation_top_blank_lines": int(_safe_get(mission, "annotation_top_blank_lines", 1)),
        "end_of_tape_indent_col": int(_safe_get(mission, "end_of_tape_indent_col", TIMESTAMP_COL)),
        "center_rest_period_text": bool(_safe_get(mission, "center_rest_period_text", True)),
        "rest_period_keep_header": bool(_safe_get(mission, "rest_period_keep_header", True)),
        "rest_period_only_when_no_comm": bool(
            _safe_get(mission, "rest_period_only_when_no_comm", True)
        ),
        "note_pages": list(_safe_get(special_pages, "note_pages", [])),
        "note_heading": _safe_get(special_pages, "note_heading", "NOTE"),
        "note_top_blank_lines": int(_safe_get(special_pages, "note_top_blank_lines", 2)),
        "note_center_vertical": bool(_safe_get(special_pages, "note_center_vertical", False)),
        "note_block_columns": int(_safe_get(special_pages, "note_block_columns", COLUMNS)),
        "rest_period_isolated_pages": list(
            _safe_get(special_pages, "rest_period_isolated_pages", [])
        ),
        "rest_period_mixed_pages": list(_safe_get(special_pages, "rest_period_mixed_pages", [])),
        "footer_pages": list(_safe_get(special_pages, "footer_pages", [])),
    }
