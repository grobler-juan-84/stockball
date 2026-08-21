"""Create processed adjusted-price base from a raw Tiingo daily CSV.

Usage:
  .venv\\Scripts\\python.exe scripts\\process_tiingo_daily.py SPY
  .venv\\Scripts\\python.exe scripts\\process_tiingo_daily.py QQQ

Selects and renames Tiingo adjusted OHLCV fields only.
Does not drop rows, fill values, or calculate indicators/returns.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

COLUMN_MAP = {
    "date": "date",
    "adjOpen": "open",
    "adjHigh": "high",
    "adjLow": "low",
    "adjClose": "close",
    "adjVolume": "volume",
}
OUT_COLUMNS = ["date", "open", "high", "low", "close", "volume"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process raw Tiingo daily CSV into adjusted OHLCV base."
    )
    parser.add_argument("ticker", help="Ticker symbol, e.g. SPY or QQQ")
    return parser.parse_args()


def normalize_ticker(raw: str) -> str:
    ticker = raw.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", ticker):
        sys.exit(f"Invalid ticker: {raw!r}")
    return ticker


args = parse_args()
ticker = normalize_ticker(args.ticker)
slug = ticker.lower()

raw_csv = RAW_DIR / f"{slug}_tiingo_daily.csv"
raw_meta_path = RAW_DIR / f"{slug}_tiingo_daily.metadata.json"
out_csv = PROCESSED_DIR / f"{slug}_daily.csv"
out_meta = PROCESSED_DIR / f"{slug}_daily.metadata.json"

if not raw_csv.exists():
    sys.exit(f"Missing raw CSV: {raw_csv}")

raw = pd.read_csv(raw_csv)
missing = [c for c in COLUMN_MAP if c not in raw.columns]
if missing:
    sys.exit(f"Raw CSV missing expected columns: {missing}")

# Selection + rename only. No row drops, no value changes.
processed = raw[list(COLUMN_MAP.keys())].rename(columns=COLUMN_MAP)[OUT_COLUMNS]

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
processed.to_csv(out_csv, index=False)

raw_meta = {}
if raw_meta_path.exists():
    raw_meta = json.loads(raw_meta_path.read_text(encoding="utf-8"))

metadata = {
    "source_file": f"data/raw/{slug}_tiingo_daily.csv",
    "source_provider": raw_meta.get("provider", "tiingo"),
    "ticker": raw_meta.get("ticker", ticker),
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

out_meta.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

print(f"ticker: {ticker}")
print(f"rows: {len(processed)}")
print(f"date range: {metadata['actual_start_date']} -> {metadata['actual_end_date']}")
print(f"csv: {out_csv}")
print(f"metadata: {out_meta}")
