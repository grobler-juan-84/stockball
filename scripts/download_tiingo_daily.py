"""Download maximum daily history for a ticker from Tiingo into data/raw/.

Usage:
  .venv\\Scripts\\python.exe scripts\\download_tiingo_daily.py SPY
  .venv\\Scripts\\python.exe scripts\\download_tiingo_daily.py QQQ

Writes the API response fields as-is to CSV plus a metadata JSON sidecar.
No calculations, cleaning, or transforms.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"
RAW_DIR = ROOT / "data" / "raw"

# Far enough back that Tiingo returns each ticker's full available history.
DEFAULT_START_DATE = "1970-01-01"

FIELDS = [
    "date",
    "close",
    "high",
    "low",
    "open",
    "volume",
    "adjClose",
    "adjHigh",
    "adjLow",
    "adjOpen",
    "adjVolume",
    "divCash",
    "splitFactor",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Tiingo daily prices for one ticker into data/raw/."
    )
    parser.add_argument(
        "ticker",
        help="Ticker symbol, e.g. SPY or QQQ",
    )
    parser.add_argument(
        "--start-date",
        default=DEFAULT_START_DATE,
        help=f"Requested start date YYYY-MM-DD (default: {DEFAULT_START_DATE})",
    )
    return parser.parse_args()


def normalize_ticker(raw: str) -> str:
    ticker = raw.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,9}", ticker):
        sys.exit(f"Invalid ticker: {raw!r}")
    return ticker


args = parse_args()
ticker = normalize_ticker(args.ticker)
ticker_slug = ticker.lower()
endpoint = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices"
csv_path = RAW_DIR / f"{ticker_slug}_tiingo_daily.csv"
metadata_path = RAW_DIR / f"{ticker_slug}_tiingo_daily.metadata.json"
requested_start = args.start_date

load_dotenv(ENV_PATH)

token = os.getenv("TIINGO_API_TOKEN")
if not token:
    sys.exit(
        "TIINGO_API_TOKEN is missing or empty. "
        "Set it in .env.local at the project root, then re-run."
    )

requested_end = datetime.now(timezone.utc).date().isoformat()
retrieved_at_utc = datetime.now(timezone.utc).isoformat()

headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/json",
}
params = {
    "startDate": requested_start,
    "endDate": requested_end,
}

response = requests.get(endpoint, params=params, headers=headers, timeout=120)

if response.status_code != 200:
    print(f"Tiingo request failed for {ticker}: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

rows = response.json()
if not isinstance(rows, list) or not rows:
    print(f"Unexpected response for {ticker}: expected a non-empty JSON list.")
    print(rows)
    sys.exit(1)

df = pd.DataFrame(rows)
missing = [c for c in FIELDS if c not in df.columns]
if missing:
    sys.exit(f"Tiingo response missing expected fields: {missing}")

df = df[FIELDS]

RAW_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(csv_path, index=False)

actual_start = str(df.iloc[0]["date"])
actual_end = str(df.iloc[-1]["date"])
row_count = int(len(df))

metadata = {
    "provider": "tiingo",
    "ticker": ticker,
    "frequency": "daily",
    "endpoint": endpoint,
    "requested_start_date": requested_start,
    "requested_end_date": requested_end,
    "actual_start_date": actual_start,
    "actual_end_date": actual_end,
    "row_count": row_count,
    "fields": FIELDS,
    "retrieved_at_utc": retrieved_at_utc,
    "transformations": [],
}

metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

print(f"ticker: {ticker}")
print(f"rows: {row_count}")
print(f"actual date range: {actual_start} -> {actual_end}")
print(f"csv: {csv_path}")
print(f"metadata: {metadata_path}")
