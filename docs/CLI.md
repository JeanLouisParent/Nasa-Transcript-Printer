# CLI Reference

## Main Entry Point

```bash
python src/cli.py [OPTIONS]
```

## Common Options

- `--common-config`: shared TOML config (default: `config/common.toml`).
- `--mission-config`: mission TOML config (default: `config/missions/apollo11.toml`).
- `--json`: input JSON path.
- `--out`: output PDF path.
- `--pages`: JSON page list/ranges (`3,5,10-12`).
- `--pdf-pages`: 1-based PDF pages (`3,5,10-12`) mapped with `--pdf-offset`.
- `--start-page` / `--end-page`: JSON page range.
- `--font`: explicit `.ttf` font path.
- `--columns`: monospaced grid width.
- `--fit-to-page` / `--no-fit-to-page`: vertical fitting behavior.
- `--faux-bold-pt`: slight synthetic bold effect by drawing text twice with a tiny offset.
- `--title-line`: mission title header.
- `--goss-line`: mission left header line.
- `--annotation-top-blank-lines`: extra spacing above annotations.
- `--end-of-tape-indent-col`: alignment column for `END OF TAPE`.
- `--center-rest-period-text` / `--no-center-rest-period-text`: center rest-period body text.
- `--rest-period-keep-header` / `--no-rest-period-keep-header`: keep/hide headers on centered rest pages.
- `--rest-period-only-when-no-comm` / `--no-rest-period-only-when-no-comm`: centering scope.
- `--dpi`: reference DPI stored in metadata.
- `--page-width-pt` / `--page-height-pt`: page dimensions.
- `--top-margin-pt` / `--bottom-margin-pt`: vertical margins.

## Path Resolution Rules

- If `--json` is only a filename (for example `AS11_TEC_merged.json`), the tool also checks `input/`.
- If `--out` is only a filename (for example `result.pdf`), the file is written under `output/`.
- Shared config defines common rendering defaults; mission config defines mission-specific rules.
- Mission config can also list special pages (for example Apollo 11 page `8` as a NOTE page).
- For NOTE pages, mission config can narrow text width via `special_pages.note_block_columns`.

## Mission Special Pages (`special_pages`)

- `note_pages`: page numbers rendered with NOTE-style layout.
- `note_heading`: heading text for NOTE pages (default: `NOTE`).
- `note_top_blank_lines`: extra spacing before NOTE block when not vertically centered.
- `note_center_vertical`: center NOTE block vertically.
- `note_block_columns`: max text width (in columns) for NOTE body block.
- `rest_period_isolated_pages`: audit/reference list for rest-period-only pages.
- `rest_period_mixed_pages`: audit/reference list for mixed rest-period pages.
- `footer_pages`: audit/reference list for pages with footer blocks.

## Examples

Generate 10 pages using default config:

```bash
python src/cli.py \
  --common-config config/common.toml \
  --mission-config config/missions/apollo11.toml \
  --pdf-pages 3-12 \
  --pdf-offset 2
```

Force a specific font:

```bash
python src/cli.py \
  --common-config config/common.toml \
  --mission-config config/missions/apollo11.toml \
  --pages 3-6 \
  --font ~/Library/Fonts/prestige.ttf \
  --out output/apollo11_prestige.pdf
```
