# Architecture

## Overview

The system is split into 5 layers:

1. `config.py`: loads and normalizes TOML configuration.
2. `cli.py`: parses arguments and orchestrates the workflow.
3. `io_utils.py`: loads JSON pages and resolves font paths.
4. `layout.py`: converts semantic blocks into monospaced lines.
5. `renderer.py`: renders lines into PDF pages using ReportLab.

## Flow

```text
JSON pages -> page selection -> line generation -> PDF rendering
```

## Technical Decisions

- `src/` package layout to avoid ambiguous imports.
- Deterministic text wrapping based on fixed column width.
- Page-by-page rendering with optional line-height fitting.
- `recreate_pdf.py` wrapper retained for backward compatibility.

## Future Extensions

- Support additional missions (Apollo 12, 13, etc.) through layout profiles.
- Add complementary exports (enriched text / HTML).
- Add visual regression checks (page-to-page comparison).
