# NASA Transcript Printer

Python pipeline to reconstruct high-quality Apollo transcript PDFs from structured JSON.

## Goals

- Reproduce the historical transcript layout (columns, headers, annotations, metadata).
- Provide a clear, packageable CLI.
- Keep a maintainable base: `src/` layout, quality tooling, and documentation.

## Project Structure

```text
.
├── input/                    # source files (JSON, TXT, PDF)
├── output/                   # generated PDFs
├── config/
│   └── default.toml          # main configuration (font, DPI, layout)
├── docs/
│   ├── ARCHITECTURE.md
│   └── CLI.md
├── src/
│   └── nasa_transcript_printer/
│       ├── cli.py
│       ├── config.py
│       ├── constants.py
│       ├── io_utils.py
│       ├── layout.py
│       └── renderer.py
├── recreate_pdf.py           # legacy compatibility wrapper
├── pyproject.toml
└── LICENSE
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Quick Usage

```bash
python -m nasa_transcript_printer \
  --config config/default.toml \
  --pdf-pages 3-12
```

Legacy command is still supported:

```bash
python recreate_pdf.py --json input/AS11_TEC_merged.json --out output/recreated.pdf
```

## Quality Checks

```bash
python -m ruff check .
python -m mypy src
```

## Notes

- Default font is Courier Prime (`~/Library/Fonts/CourierPrime-Regular.ttf` when available).
- Font fallback automatically uses `Courier` when no TTF is found.
- If `--json` is a filename only, the CLI automatically looks in `input/`.
- If `--out` is a filename only, output is automatically written to `output/`.
- Default reference DPI is `1200` (configurable in `config/default.toml`).
- Rendering settings (DPI, font, margins, page size, columns) are configurable via `config/default.toml`.
