"""Configuration loading from TOML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import (
    BOTTOM_MARGIN_PT,
    COLUMNS,
    DEFAULT_CONFIG,
    DEFAULT_DPI,
    DEFAULT_JSON,
    DEFAULT_OUT,
    DEFAULT_START_PAGE,
    LINE_HEIGHT_MULTIPLIER,
    PAGE_SIZE,
    PDF_PAGE_OFFSET,
    SPACE_LEN,
    TOP_MARGIN_PT,
)

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def _safe_get(section: dict[str, Any], key: str, default: Any) -> Any:
    value = section.get(key, default)
    return default if value is None else value


def load_config(config_path: str) -> dict[str, Any]:
    path = Path(config_path)
    if not path.is_file():
        return {}
    with path.open("rb") as file:
        data = tomllib.load(file)
    return data


def config_defaults(config_data: dict[str, Any]) -> dict[str, Any]:
    paths = config_data.get("paths", {})
    pagination = config_data.get("pagination", {})
    font = config_data.get("font", {})
    layout = config_data.get("layout", {})
    page = config_data.get("page", {})

    return {
        "config": DEFAULT_CONFIG,
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
        "dpi": int(_safe_get(page, "dpi", DEFAULT_DPI)),
        "page_width_pt": float(_safe_get(page, "width_pt", PAGE_SIZE[0])),
        "page_height_pt": float(_safe_get(page, "height_pt", PAGE_SIZE[1])),
        "top_margin_pt": float(_safe_get(page, "top_margin_pt", TOP_MARGIN_PT)),
        "bottom_margin_pt": float(_safe_get(page, "bottom_margin_pt", BOTTOM_MARGIN_PT)),
    }
