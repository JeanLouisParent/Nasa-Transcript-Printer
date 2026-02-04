"""Command-line interface for NASA transcript PDF reconstruction."""

from __future__ import annotations

import argparse

from .config import config_defaults, load_config
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
from .io_utils import (
    load_pages,
    locate_font,
    resolve_input_json_path,
    resolve_output_pdf_path,
)
from .layout import parse_pages_arg
from .renderer import render_pdf, resolve_page_selection


def build_parser(defaults: dict[str, object] | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nasa-transcript-printer",
        description="Recreate transcript PDF from JSON using a monospaced typeface.",
    )
    parser.set_defaults(**(defaults or {}))
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        help=f"TOML configuration file (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument("--json", default=DEFAULT_JSON, help="Path to JSON input")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Output PDF path")
    parser.add_argument(
        "--start-page",
        type=int,
        default=DEFAULT_START_PAGE,
        help="First page number to include (default: 3)",
    )
    parser.add_argument("--end-page", type=int, default=None, help="Last page number to include")
    parser.add_argument("--pages", default="", help="CSV page numbers or ranges: 3,5,10-12")
    parser.add_argument("--pdf-pages", default="", help="PDF pages or ranges (1-based)")
    parser.add_argument("--pdf-start-page", type=int, default=None, help="First PDF page (1-based)")
    parser.add_argument("--pdf-end-page", type=int, default=None, help="Last PDF page (1-based)")
    parser.add_argument(
        "--pdf-offset",
        type=int,
        default=PDF_PAGE_OFFSET,
        help="PDF page N maps to JSON page (N - offset).",
    )
    parser.add_argument("--font", default="", help="Path to TTF font")
    parser.add_argument("--font-size", type=float, default=10.0, help="Font size in points")
    parser.add_argument(
        "--left-margin-pt",
        type=float,
        default=None,
        help="Left margin in points (default: auto-center text block)",
    )
    parser.add_argument(
        "--line-height-multiplier",
        type=float,
        default=LINE_HEIGHT_MULTIPLIER,
        help=f"Line height multiplier (default: {LINE_HEIGHT_MULTIPLIER})",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=COLUMNS,
        help=f"Total columns (default: {COLUMNS})",
    )
    parser.add_argument(
        "--space-len",
        type=int,
        default=SPACE_LEN,
        help="Spaces between wrapped words",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help="Reference DPI for layout config",
    )
    parser.add_argument(
        "--page-width-pt",
        type=float,
        default=PAGE_SIZE[0],
        help=f"Page width in points (default: {PAGE_SIZE[0]})",
    )
    parser.add_argument(
        "--page-height-pt",
        type=float,
        default=PAGE_SIZE[1],
        help=f"Page height in points (default: {PAGE_SIZE[1]})",
    )
    parser.add_argument(
        "--top-margin-pt",
        type=float,
        default=TOP_MARGIN_PT,
        help=f"Top margin in points (default: {TOP_MARGIN_PT})",
    )
    parser.add_argument(
        "--bottom-margin-pt",
        type=float,
        default=BOTTOM_MARGIN_PT,
        help=f"Bottom margin in points (default: {BOTTOM_MARGIN_PT})",
    )
    parser.add_argument(
        "--fit-to-page",
        action="store_true",
        default=True,
        help="Auto-reduce line height to fit full page (default: on)",
    )
    parser.add_argument(
        "--no-fit-to-page",
        action="store_false",
        dest="fit_to_page",
        help="Disable line-height auto-fit",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config", default=DEFAULT_CONFIG)
    pre_args, _ = pre_parser.parse_known_args(argv)
    defaults = config_defaults(load_config(pre_args.config))

    parser = build_parser(defaults=defaults)
    args = parser.parse_args(argv)

    pages_by_num = load_pages(resolve_input_json_path(args.json))
    selected_pages = resolve_page_selection(
        pages_by_num=pages_by_num,
        pages=parse_pages_arg(args.pages),
        page_start=args.start_page,
        page_end=args.end_page,
        pdf_pages=parse_pages_arg(args.pdf_pages),
        pdf_start=args.pdf_start_page,
        pdf_end=args.pdf_end_page,
        pdf_offset=args.pdf_offset,
    )

    render_pdf(
        pages_by_num=pages_by_num,
        output_path=resolve_output_pdf_path(args.out),
        selected_pages=selected_pages,
        columns=args.columns,
        space_len=args.space_len,
        font_path=locate_font(args.font),
        font_size=args.font_size,
        left_margin_pt=args.left_margin_pt,
        line_height_multiplier=args.line_height_multiplier,
        fit_to_page=args.fit_to_page,
        page_width_pt=args.page_width_pt,
        page_height_pt=args.page_height_pt,
        top_margin_pt=args.top_margin_pt,
        bottom_margin_pt=args.bottom_margin_pt,
        dpi=args.dpi,
    )
    return 0


def main() -> None:
    raise SystemExit(run())
