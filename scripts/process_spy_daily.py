"""Create processed SPY adjusted-price base from raw Tiingo daily CSV.

Selects and renames Tiingo adjusted OHLCV fields only.
Does not drop rows, fill values, or calculate indicators/returns.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_CSV = ROOT / "data" / "raw" / "spy_tiingo_daily.csv"
RAW_META = ROOT / "data" / "raw" / "spy_tiingo_daily.metadata.json"
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_CSV = PROCESSED_DIR / "spy_daily.csv"
OUT_META = PROCESSED_DIR / "spy_daily.metadata.json"

COLUMN_MAP = {
    "date": "date",
    "adjOpen": "open",
    "adjHigh": "high",
    "adjLow": "low",
    "adjClose": "close",
    "adjVolume": "volume",
}
OUT_COLUMNS = ["date", "open", "high", "low", "close", "volume"]

if not RAW_CSV.exists():
    sys.exit(f"Missing raw CSV: {RAW_CSV}")

raw = pd.read_csv(RAW_CSV)
missing = [c for c in COLUMN_MAP if c not in raw.columns]
if missing:
    sys.exit(f"Raw CSV missing expected columns: {missing}")

# Selection + rename only. No row drops, no value changes.
processed = raw[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)[OUT_COLUMNS]

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
processed.to_csv(OUT_CSV, index=False)

raw_meta = {}
if RAW_META.exists():
    raw_meta = json.loads(RAW_META.read_text(encoding="utf-8"))

metadata = {
    "source_file": "data/raw/spy_tiingo_daily.csv",
    "source_provider": raw_meta.get("provider", "tiingo"),
    "ticker": raw_meta.get("ticker", "SPY"),
    "frequency": "daily",
    "row_count": int(len(processed)),
    "actual_start_date": str(processed.iloc[0]["date"]),
    "actual_end_date": str(processed.iloc[-1]["date"]),
    "fields": OUT_COLUMNS,
    "column_mapping": {
        "date": "date",
        "open": "adjOpen",
        "high": "adjHigh",
        "low": "adjLow",
        "close": "adjClose",
        "volume": "adjVolume",
    },
    "transformations": [
        "selected date and Tiingo adjusted OHLCV fields",
        "renamed adjOpen/adjHigh/adjLow/adjClose/adjVolume to open/high/low/close/volume",
    ],
    "rows_dropped": 0,
    "values_altered": False,
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
}

OUT_META.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

print(f"rows: {len(processed)}")
print(f"date range: {metadata['actual_start_date']} -> {metadata['actual_end_date']}")
print(f"csv: {OUT_CSV}")
print(f"metadata: {OUT_META}")
