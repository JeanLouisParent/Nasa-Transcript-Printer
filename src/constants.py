"""Project constants for transcript layout and rendering."""

from __future__ import annotations

DEFAULT_JSON = "input/AS11_TEC_merged.json"
DEFAULT_OUT = "output/AS11_TEC_full.pdf"
DEFAULT_COMMON_CONFIG = "config/common.toml"
DEFAULT_MISSION_CONFIG = "config/missions/apollo11.toml"
DEFAULT_START_PAGE = 3
DEFAULT_FONT_HINT = "Prestige Elite"
DEFAULT_DPI = 1200
DEFAULT_FAUX_BOLD_PT = 0.0

# Layout tuning (in characters or points where noted).
COLUMNS = 80
TIMESTAMP_COL = 0
SPEAKER_COL = 18
TEXT_COL = 30
META_COL = 30
CONTINUATION_COL = 30
LINE_HEIGHT_MULTIPLIER = 1.2
TOP_MARGIN_PT = 30
BOTTOM_MARGIN_PT = 30
PDF_PAGE_OFFSET = 2  # PDF page 3 corresponds to JSON page 1
SPACE_LEN = 1

PAGE_SIZE = (605, 756)
