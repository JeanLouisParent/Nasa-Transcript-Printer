"""I/O helpers for loading transcript data and fonts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")


def resolve_input_json_path(json_path: str) -> str:
    candidate = Path(json_path)
    if candidate.is_file():
        return str(candidate)

    if not candidate.is_absolute():
        fallback = INPUT_DIR / candidate
        if fallback.is_file():
            return str(fallback)

    return str(candidate)


def resolve_output_pdf_path(output_path: str) -> str:
    candidate = Path(output_path)
    if not candidate.is_absolute() and candidate.parent == Path("."):
        candidate = OUTPUT_DIR / candidate
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return str(candidate)


def load_pages(json_path: str) -> dict[int, dict[str, Any]]:
    with open(json_path, encoding="utf-8") as file:
        data = json.load(file)

    pages_by_num: dict[int, dict[str, Any]] = {}
    for page in data["pages"].values():
        page_num = page.get("header", {}).get("page")
        if page_num is None:
            continue
        pages_by_num[page_num] = page
    return pages_by_num


def locate_font(path_hint: str) -> str:
    hint_path = Path(path_hint).expanduser()
    if path_hint and hint_path.is_file():
        return str(hint_path)

    candidates = [
        Path("~/Library/Fonts/CourierPrime-Regular.ttf").expanduser(),
        Path("~/Library/Fonts/Courier Prime.ttf").expanduser(),
        Path("/Library/Fonts/CourierPrime-Regular.ttf"),
        Path("/Library/Fonts/Courier Prime.ttf"),
        Path("~/Library/Fonts/prestige.ttf").expanduser(),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            return str(candidate)
    return ""
