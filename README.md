<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg" alt="NASA Logo" width="160"/>

# NASA Transcript Printer

_Legacy-Layout Apollo Transcript Reprinting Engine_

</div>

Python pipeline to reconstruct high-quality Apollo transcript PDFs from structured JSON.

## About

This repository is the legacy-layout print engine of the Apollo transcript effort.

I started this work to make mission transcripts easier to preserve, read, and share in a modern format, while staying as faithful as possible to the original NASA pages. The long-term objective is to reprint transcripts for all Apollo missions with mission-aware rules, not one-off manual tweaks.

This project consumes structured JSON generated upstream by:
<https://github.com/JeanLouisParent/Nasa-Transcript-Processor>

In short:

- `Nasa-Transcript-Processor` builds and normalizes the transcript data.
- `nasa_transcript_printer` rebuilds print-ready PDFs from that data.

## Goals

- Reproduce the historical transcript layout (columns, headers, annotations, metadata).
- Provide a clear, packageable CLI.
- Keep a maintainable base: clear package layout, quality tooling, and documentation.

## Project Structure

```text
.
├── input/                    # source files (JSON, TXT, PDF)
├── output/                   # generated PDFs
├── config/
│   ├── common.toml           # shared defaults across missions
│   └── missions/
│       ├── _template.toml    # template for new missions
│       └── apollo11.toml     # mission-specific overrides
├── docs/
│   ├── ARCHITECTURE.md
│   └── CLI.md
├── src/
│   ├── cli.py
│   ├── config.py
│   ├── constants.py
│   ├── io_utils.py
│   ├── layout.py
│   └── renderer.py
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
python src/cli.py \
  --common-config config/common.toml \
  --mission-config config/missions/apollo11.toml \
  --pdf-pages 3-12
```

Add a new mission by copying `config/missions/_template.toml` to
`config/missions/<mission>.toml`, then run with `--mission-config`.
Mission configs can include `special_pages` lists for page-specific layouts.

Render the full Apollo 11 transcript with defaults:

```bash
python src/cli.py \
  --common-config config/common.toml \
  --mission-config config/missions/apollo11.toml \
  --start-page 1 \
  --out output/AS11_TEC_full.pdf
```

## Quality Checks

```bash
python -m ruff check .
python -m mypy src
```

## Notes

- Default shared font is Prestige (`~/Library/Fonts/prestige.ttf`).
- Fallback order is Courier Prime, then built-in `Courier` if no TTF is found.
- If `--json` is a filename only, the CLI automatically looks in `input/`.
- If `--out` is a filename only, output is automatically written to `output/`.
- Default reference DPI is `1200` (configurable in `config/common.toml`).
- Mission-specific rendering rules are configurable per mission TOML.
