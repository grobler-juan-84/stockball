"""Validate raw SPY Tiingo daily CSV — report anomalies, do not repair.

Acquire → Validate → (later) Process
Reads data/raw only. Writes nothing under data/processed/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "raw" / "spy_tiingo_daily.csv"
METADATA_PATH = ROOT / "data" / "raw" / "spy_tiingo_daily.metadata.json"

EXPECTED_ROW_COUNT = 8447
EXPECTED_FIELDS = [
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
CRITICAL_OHLCV = ["open", "high", "low", "close", "volume"]

failures: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"[{status}] {name}{suffix}")
    if not ok:
        failures.append(name)


if not CSV_PATH.exists():
    sys.exit(f"Missing raw CSV: {CSV_PATH}")
if not METADATA_PATH.exists():
    sys.exit(f"Missing metadata: {METADATA_PATH}")

df = pd.read_csv(CSV_PATH)
metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

print(f"csv: {CSV_PATH}")
print(f"metadata: {METADATA_PATH}")
print()

# --- structural checks ---
check(
    "exact row count",
    len(df) == EXPECTED_ROW_COUNT,
    f"got {len(df)}, expected {EXPECTED_ROW_COUNT}",
)
check(
    "exact 13 expected columns",
    list(df.columns) == EXPECTED_FIELDS,
    f"got {list(df.columns)}",
)

# --- dates ---
dates = df["date"]
check("dates are unique", dates.is_unique, f"unique={dates.nunique()}, rows={len(dates)}")
chrono_ok = bool(dates.is_monotonic_increasing)
chrono_detail = "ascending"
if not chrono_ok:
    sorted_dates = dates.sort_values().reset_index(drop=True)
    chrono_detail = f"first disorder at index {int((dates.reset_index(drop=True) != sorted_dates).idxmax())}"
check("dates are chronological", chrono_ok, chrono_detail)

# Duplicate full observations (all columns identical)
dup_obs = int(df.duplicated().sum())
check("no duplicate observations", dup_obs == 0, f"duplicate_rows={dup_obs}")

# --- critical OHLCV nulls ---
null_counts = {c: int(df[c].isna().sum()) for c in CRITICAL_OHLCV}
null_total = sum(null_counts.values())
check(
    "no missing/null values in critical OHLCV",
    null_total == 0,
    str(null_counts),
)

# --- price / volume sanity ---
high_ge_low = df["high"] >= df["low"]
n_bad_hl = int((~high_ge_low).sum())
check("high >= low", n_bad_hl == 0, f"violations={n_bad_hl}")

ohlc_positive = (df[["open", "high", "low", "close"]] > 0).all(axis=1)
n_nonpos = int((~ohlc_positive).sum())
check("OHLC prices are positive", n_nonpos == 0, f"violations={n_nonpos}")

n_neg_vol = int((df["volume"] < 0).sum())
check("volume is not negative", n_neg_vol == 0, f"violations={n_neg_vol}")

n_bad_split = int((df["splitFactor"] <= 0).sum())
check(
    "splitFactor is positive",
    n_bad_split == 0,
    f"non_positive={n_bad_split}",
)

# --- metadata agreement ---
actual_start = str(df.iloc[0]["date"])
actual_end = str(df.iloc[-1]["date"])
check(
    "first date agrees with metadata",
    actual_start == metadata.get("actual_start_date"),
    f"csv={actual_start}, metadata={metadata.get('actual_start_date')}",
)
check(
    "last date agrees with metadata",
    actual_end == metadata.get("actual_end_date"),
    f"csv={actual_end}, metadata={metadata.get('actual_end_date')}",
)
check(
    "row_count agrees with metadata",
    len(df) == metadata.get("row_count"),
    f"csv={len(df)}, metadata={metadata.get('row_count')}",
)

# --- informational corporate-action counts (not failures) ---
n_div = int((df["divCash"] != 0).sum())
n_split = int((df["splitFactor"] != 1).sum())
notes.append(f"rows with divCash != 0: {n_div}")
notes.append(f"rows with splitFactor != 1: {n_split}")

print()
print("Notes (not failures):")
for note in notes:
    print(f"  - {note}")

print()
if failures:
    print(f"VALIDATION FAILED ({len(failures)} check(s)):")
    for name in failures:
        print(f"  - {name}")
    print("Raw data was not modified.")
    sys.exit(1)

print("VALIDATION PASSED - raw data looks internally sensible.")
print("Raw data was not modified. No processed/ output written.")
