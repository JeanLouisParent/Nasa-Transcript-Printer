"""Command-line interface for NASA transcript PDF reconstruction."""

from __future__ import annotations

import argparse
from typing import Any

from config import config_defaults, load_merged_config
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
    TOP_MARGIN_PT,
)
from io_utils import (
    load_pages,
    locate_font,
    resolve_input_json_path,
    resolve_output_pdf_path,
)
from layout import parse_pages_arg
from renderer import render_pdf, resolve_page_selection


def build_parser(defaults: dict[str, Any] | None = None) -> argparse.ArgumentParser:
    defaults = defaults or {}
    parser = argparse.ArgumentParser(
        prog="nasa-transcript-printer",
        description="Recreate transcript PDF from JSON using a monospaced typeface.",
    )
    parser.add_argument(
        "--common-config",
        default=defaults.get("common_config", DEFAULT_COMMON_CONFIG),
        help=f"Common TOML configuration (default: {DEFAULT_COMMON_CONFIG})",
    )
    parser.add_argument(
        "--mission-config",
        default=defaults.get("mission_config", DEFAULT_MISSION_CONFIG),
        help=f"Mission TOML configuration (default: {DEFAULT_MISSION_CONFIG})",
    )
    parser.add_argument(
        "--json",
        default=defaults.get("json", DEFAULT_JSON),
        help="Path to JSON input",
    )
    parser.add_argument(
        "--out",
        default=defaults.get("out", DEFAULT_OUT),
        help="Output PDF path",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=int(defaults.get("start_page", DEFAULT_START_PAGE)),
        help="First page number to include (default: 3)",
    )
    parser.add_argument(
        "--end-page",
        type=int,
        default=defaults.get("end_page"),
        help="Last page number to include",
    )
    parser.add_argument("--pages", default="", help="CSV page numbers or ranges: 3,5,10-12")
    parser.add_argument("--pdf-pages", default="", help="PDF pages or ranges (1-based)")
    parser.add_argument("--pdf-start-page", type=int, default=None, help="First PDF page (1-based)")
    parser.add_argument("--pdf-end-page", type=int, default=None, help="Last PDF page (1-based)")
    parser.add_argument(
        "--pdf-offset",
        type=int,
        default=int(defaults.get("pdf_offset", PDF_PAGE_OFFSET)),
        help="PDF page N maps to JSON page (N - offset).",
    )
    parser.add_argument("--font", default=defaults.get("font", ""), help="Path to TTF font")
    parser.add_argument(
        "--font-size",
        type=float,
        default=float(defaults.get("font_size", 10.0)),
        help="Font size in points",
    )
    parser.add_argument(
        "--left-margin-pt",
        type=float,
        default=defaults.get("left_margin_pt"),
        help="Left margin in points (default: auto-center text block)",
    )
    parser.add_argument(
        "--line-height-multiplier",
        type=float,
        default=float(defaults.get("line_height_multiplier", LINE_HEIGHT_MULTIPLIER)),
        help=f"Line height multiplier (default: {LINE_HEIGHT_MULTIPLIER})",
    )
    parser.add_argument(
        "--columns",
        type=int,
        default=int(defaults.get("columns", COLUMNS)),
        help=f"Total columns (default: {COLUMNS})",
    )
    parser.add_argument(
        "--space-len",
        type=int,
        default=int(defaults.get("space_len", SPACE_LEN)),
        help="Spaces between wrapped words",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=int(defaults.get("dpi", DEFAULT_DPI)),
        help="Reference DPI for layout config",
    )
    parser.add_argument(
        "--page-width-pt",
        type=float,
        default=float(defaults.get("page_width_pt", PAGE_SIZE[0])),
        help=f"Page width in points (default: {PAGE_SIZE[0]})",
    )
    parser.add_argument(
        "--page-height-pt",
        type=float,
        default=float(defaults.get("page_height_pt", PAGE_SIZE[1])),
        help=f"Page height in points (default: {PAGE_SIZE[1]})",
    )
    parser.add_argument(
        "--top-margin-pt",
        type=float,
        default=float(defaults.get("top_margin_pt", TOP_MARGIN_PT)),
        help=f"Top margin in points (default: {TOP_MARGIN_PT})",
    )
    parser.add_argument(
        "--bottom-margin-pt",
        type=float,
        default=float(defaults.get("bottom_margin_pt", BOTTOM_MARGIN_PT)),
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
    parser.add_argument(
        "--faux-bold-pt",
        type=float,
        default=float(defaults.get("faux_bold_pt", DEFAULT_FAUX_BOLD_PT)),
        help="Extra draw offset in points to simulate a slightly bolder font",
    )
    parser.add_argument(
        "--title-line",
        default=defaults.get("title_line", "AIR-TO-GROUND VOICE TRANSCRIPTION"),
        help="Header title line for mission pages",
    )
    parser.add_argument(
        "--goss-line",
        default=defaults.get("goss_line", "(GOSS NET 1)"),
        help="Left header line text",
    )
    parser.add_argument(
        "--annotation-top-blank-lines",
        type=int,
        default=int(defaults.get("annotation_top_blank_lines", 1)),
        help="Extra blank lines before annotation blocks",
    )
    parser.add_argument(
        "--end-of-tape-indent-col",
        type=int,
        default=int(defaults.get("end_of_tape_indent_col", 0)),
        help="Column index for END OF TAPE alignment",
    )
    parser.add_argument(
        "--center-rest-period-text",
        action="store_true",
        default=bool(defaults.get("center_rest_period_text", True)),
        help="Center rest-period text block",
    )
    parser.add_argument(
        "--no-center-rest-period-text",
        action="store_false",
        dest="center_rest_period_text",
        help="Disable centered rest-period text",
    )
    parser.add_argument(
        "--rest-period-keep-header",
        action="store_true",
        default=bool(defaults.get("rest_period_keep_header", True)),
        help="Keep normal page header on centered rest-period pages",
    )
    parser.add_argument(
        "--no-rest-period-keep-header",
        action="store_false",
        dest="rest_period_keep_header",
        help="Hide page header on centered rest-period pages",
    )
    parser.add_argument(
        "--rest-period-only-when-no-comm",
        action="store_true",
        default=bool(defaults.get("rest_period_only_when_no_comm", True)),
        help="Apply rest-period centering only on pages with no comm blocks",
    )
    parser.add_argument(
        "--no-rest-period-only-when-no-comm",
        action="store_false",
        dest="rest_period_only_when_no_comm",
        help="Apply rest-period centering even when comm blocks exist",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--common-config", default=DEFAULT_COMMON_CONFIG)
    pre_parser.add_argument("--mission-config", default=DEFAULT_MISSION_CONFIG)
    pre_args, _ = pre_parser.parse_known_args(argv)
    merged_config = load_merged_config(pre_args.common_config, pre_args.mission_config)
    defaults = config_defaults(merged_config)

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

    mission_style: dict[str, Any] = {
        "title_line": defaults.get("title_line"),
        "goss_line": defaults.get("goss_line"),
        "annotation_top_blank_lines": defaults.get("annotation_top_blank_lines"),
        "end_of_tape_indent_col": defaults.get("end_of_tape_indent_col"),
        "center_rest_period_text": defaults.get("center_rest_period_text"),
        "rest_period_keep_header": defaults.get("rest_period_keep_header"),
        "rest_period_only_when_no_comm": defaults.get("rest_period_only_when_no_comm"),
        "note_pages": defaults.get("note_pages", []),
        "note_heading": defaults.get("note_heading"),
        "note_top_blank_lines": defaults.get("note_top_blank_lines"),
        "note_center_vertical": defaults.get("note_center_vertical"),
        "note_block_columns": defaults.get("note_block_columns"),
        "rest_period_isolated_pages": defaults.get("rest_period_isolated_pages", []),
        "rest_period_mixed_pages": defaults.get("rest_period_mixed_pages", []),
        "footer_pages": defaults.get("footer_pages", []),
    }
    mission_style.update(
        {
            "title_line": args.title_line,
            "goss_line": args.goss_line,
            "annotation_top_blank_lines": args.annotation_top_blank_lines,
            "end_of_tape_indent_col": args.end_of_tape_indent_col,
            "center_rest_period_text": args.center_rest_period_text,
            "rest_period_keep_header": args.rest_period_keep_header,
            "rest_period_only_when_no_comm": args.rest_period_only_when_no_comm,
        }
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
        faux_bold_pt=args.faux_bold_pt,
        mission_style=mission_style,
    )
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
