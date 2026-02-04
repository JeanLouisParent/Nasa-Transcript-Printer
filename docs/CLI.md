# CLI Reference

## Main Entry Point

```bash
python -m nasa_transcript_printer [OPTIONS]
```

## Common Options

- `--config`: TOML configuration file (default: `config/default.toml`).
- `--json`: input JSON path.
- `--out`: output PDF path.
- `--pages`: JSON page list/ranges (`3,5,10-12`).
- `--pdf-pages`: 1-based PDF pages (`3,5,10-12`) mapped with `--pdf-offset`.
- `--start-page` / `--end-page`: JSON page range.
- `--font`: explicit `.ttf` font path.
- `--columns`: monospaced grid width.
- `--fit-to-page` / `--no-fit-to-page`: vertical fitting behavior.
- `--dpi`: reference DPI stored in metadata.
- `--page-width-pt` / `--page-height-pt`: page dimensions.
- `--top-margin-pt` / `--bottom-margin-pt`: vertical margins.

## Path Resolution Rules

- If `--json` is only a filename (for example `AS11_TEC_merged.json`), the tool also checks `input/`.
- If `--out` is only a filename (for example `result.pdf`), the file is written under `output/`.
- Project default config uses Courier Prime and `dpi = 1200`.

## Examples

Generate 10 pages using default config:

```bash
python -m nasa_transcript_printer \
  --config config/default.toml \
  --pdf-pages 3-12 \
  --pdf-offset 2
```

Force a specific font:

```bash
python -m nasa_transcript_printer \
  --config config/default.toml \
  --pages 3-6 \
  --font ~/Library/Fonts/CourierPrime-Regular.ttf \
  --out output/courierprime.pdf
```
