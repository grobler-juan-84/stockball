"""Download SPY maximum daily history from Tiingo into data/raw/.

Writes the API response fields as-is to CSV plus a metadata JSON sidecar.
No calculations, cleaning, or transforms.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"
RAW_DIR = ROOT / "data" / "raw"
CSV_PATH = RAW_DIR / "spy_tiingo_daily.csv"
METADATA_PATH = RAW_DIR / "spy_tiingo_daily.metadata.json"

ENDPOINT = "https://api.tiingo.com/tiingo/daily/SPY/prices"
REQUESTED_START = "1993-01-29"
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
    "startDate": REQUESTED_START,
    "endDate": requested_end,
}

response = requests.get(ENDPOINT, params=params, headers=headers, timeout=120)

if response.status_code != 200:
    print(f"Tiingo request failed: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

rows = response.json()
if not isinstance(rows, list) or not rows:
    print("Unexpected response: expected a non-empty JSON list.")
    print(rows)
    sys.exit(1)

df = pd.DataFrame(rows)
missing = [c for c in FIELDS if c not in df.columns]
if missing:
    sys.exit(f"Tiingo response missing expected fields: {missing}")

df = df[FIELDS]

RAW_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(CSV_PATH, index=False)

actual_start = str(df.iloc[0]["date"])
actual_end = str(df.iloc[-1]["date"])
row_count = int(len(df))

metadata = {
    "provider": "tiingo",
    "ticker": "SPY",
    "frequency": "daily",
    "endpoint": ENDPOINT,
    "requested_start_date": REQUESTED_START,
    "requested_end_date": requested_end,
    "actual_start_date": actual_start,
    "actual_end_date": actual_end,
    "row_count": row_count,
    "fields": FIELDS,
    "retrieved_at_utc": retrieved_at_utc,
    "transformations": [],
}

METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

print(f"rows: {row_count}")
print(f"actual date range: {actual_start} -> {actual_end}")
print(f"csv: {CSV_PATH}")
print(f"metadata: {METADATA_PATH}")
