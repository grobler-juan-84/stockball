"""Temporary smoke test: .env.local -> Python -> Tiingo -> SPY sample.

Does not save files or transform data. Delete or replace once connectivity
and the raw Tiingo schema are confirmed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env.local"

load_dotenv(ENV_PATH)

token = os.getenv("TIINGO_API_TOKEN")
if not token:
    sys.exit(
        "TIINGO_API_TOKEN is missing or empty. "
        "Set it in .env.local at the project root, then re-run."
    )

url = "https://api.tiingo.com/tiingo/daily/SPY/prices"
params = {
    "startDate": "2024-01-02",
    "endDate": "2024-01-16",
}
headers = {
    "Authorization": f"Token {token}",
    "Accept": "application/json",
}

response = requests.get(url, params=params, headers=headers, timeout=30)

if response.status_code != 200:
    print(f"Tiingo request failed: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

rows = response.json()
if not isinstance(rows, list) or not rows:
    print("Unexpected response: expected a non-empty JSON list.")
    print(rows)
    sys.exit(1)

print(f"rows: {len(rows)}")
print(f"fields: {list(rows[0].keys())}")
print("sample observations:")
print(json.dumps(rows[:5], indent=2))
