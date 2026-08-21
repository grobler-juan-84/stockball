"""Assign Experiment 001 chronological discovery/validation partitions.

Authority: experiments/EXPERIMENT_001.md §13 (LOCKED 2026-08-21).
This script implements that specification; it must not redefine methodology.

For each ETF's eligible observations (chronological order):
  first 80%  → discovery  → experiments/001/discovery/input/
  final 20%  → validation → experiments/001/validation/input/

Safeguard: discovery and validation rows are written to separate directories.
No combined performance file is produced.

Does NOT compute A/B/C/D, forward returns, MAE/MFE, or outcome metrics.

Usage:
  .venv\\Scripts\\python.exe scripts\\partition_experiment_001_discovery_validation.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "experiments" / "EXPERIMENT_001.md"
UNIVERSE_PATH = ROOT / "config" / "research_universe.json"
ELIGIBLE_DIR = ROOT / "experiments" / "001" / "eligible"
DISCOVERY_DIR = ROOT / "experiments" / "001" / "discovery" / "input"
VALIDATION_DIR = ROOT / "experiments" / "001" / "validation" / "input"

DISCOVERY_FRACTION = 0.80  # EXPERIMENT_001.md §13


def load_universe() -> list[str]:
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    tickers = [str(t).strip().upper() for t in data["equity_etfs"]]
    if not tickers:
        sys.exit(f"equity_etfs empty in {UNIVERSE_PATH}")
    return tickers


def split_eligible(eligible: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Return discovery, validation, and discovery_count (floor of 80%)."""
    n = len(eligible)
    if n < 2:
        sys.exit(f"Need at least 2 eligible rows to form an 80/20 split; got {n}")

    n_discovery = int(n * DISCOVERY_FRACTION)  # floor(80%)
    # Ensure validation is non-empty when n >= 2
    if n_discovery >= n:
        n_discovery = n - 1
    if n_discovery < 1:
        n_discovery = 1

    discovery = eligible.iloc[:n_discovery].copy()
    validation = eligible.iloc[n_discovery:].copy()
    discovery["research_partition"] = "discovery"
    validation["research_partition"] = "validation"
    return discovery, validation, n_discovery


def main() -> None:
    if not SPEC_PATH.exists():
        sys.exit(f"Missing locked specification: {SPEC_PATH}")

    tickers = load_universe()
    DISCOVERY_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

    created_at = datetime.now(timezone.utc).isoformat()
    audit_rows: list[dict] = []
    failures: list[str] = []

    print(f"specification: {SPEC_PATH.relative_to(ROOT)} §13 (authority)")
    print(f"discovery out: {DISCOVERY_DIR.relative_to(ROOT)}")
    print(f"validation out: {VALIDATION_DIR.relative_to(ROOT)}")
    print()
    print(
        "Ticker | Eligible | Discovery rows | Validation rows | "
        "Last discovery date | First validation date | Order OK"
    )

    for ticker in tickers:
        src = ELIGIBLE_DIR / f"{ticker.lower()}_eligible_base.csv"
        if not src.exists():
            sys.exit(f"Missing eligible base (run Step 26 first): {src}")

        base = pd.read_csv(src)
        base["date"] = pd.to_datetime(base["date"], utc=True)
        eligible = (
            base.loc[base["eligible"]]
            .sort_values("date")
            .reset_index(drop=True)
        )

        discovery, validation, n_discovery = split_eligible(eligible)

        last_disc = discovery["date"].max()
        first_val = validation["date"].min()
        order_ok = bool(last_disc < first_val)
        if not order_ok:
            failures.append(ticker)

        # Separate outputs — do not write a combined discovery+validation table
        disc_out = discovery.copy()
        val_out = validation.copy()
        disc_out["date"] = disc_out["date"].dt.strftime("%Y-%m-%dT00:00:00.000Z")
        val_out["date"] = val_out["date"].dt.strftime("%Y-%m-%dT00:00:00.000Z")

        disc_csv = DISCOVERY_DIR / f"{ticker.lower()}_discovery_input.csv"
        val_csv = VALIDATION_DIR / f"{ticker.lower()}_validation_input.csv"
        disc_out.to_csv(disc_csv, index=False)
        val_out.to_csv(val_csv, index=False)

        last_disc_s = last_disc.strftime("%Y-%m-%d")
        first_val_s = first_val.strftime("%Y-%m-%d")

        meta_common = {
            "experiment": "001",
            "specification": "experiments/EXPERIMENT_001.md",
            "specification_section": "§13 Discovery / Validation Split",
            "specification_status": "LOCKED",
            "specification_locked": "2026-08-21",
            "ticker": ticker,
            "source_eligible_base": str(src.relative_to(ROOT)).replace("\\", "/"),
            "eligible_row_count": int(len(eligible)),
            "discovery_row_count": int(len(discovery)),
            "validation_row_count": int(len(validation)),
            "discovery_fraction_rule": "first floor(80%) of eligible rows by date",
            "last_discovery_date": last_disc_s,
            "first_validation_date": first_val_s,
            "chronological_order_ok": order_ok,
            "explicitly_not_computed": [
                "A/B/C/D membership",
                "forward returns",
                "MAE/MFE",
                "win rates or other outcome metrics",
            ],
            "created_at_utc": created_at,
        }

        disc_meta = {
            **meta_common,
            "research_partition": "discovery",
            "output_csv": str(disc_csv.relative_to(ROOT)).replace("\\", "/"),
        }
        val_meta = {
            **meta_common,
            "research_partition": "validation",
            "output_csv": str(val_csv.relative_to(ROOT)).replace("\\", "/"),
        }
        (DISCOVERY_DIR / f"{ticker.lower()}_discovery_input.metadata.json").write_text(
            json.dumps(disc_meta, indent=2) + "\n", encoding="utf-8"
        )
        (VALIDATION_DIR / f"{ticker.lower()}_validation_input.metadata.json").write_text(
            json.dumps(val_meta, indent=2) + "\n", encoding="utf-8"
        )

        audit_rows.append(
            {
                "ticker": ticker,
                "eligible": int(len(eligible)),
                "discovery_rows": int(len(discovery)),
                "validation_rows": int(len(validation)),
                "last_discovery_date": last_disc_s,
                "first_validation_date": first_val_s,
                "chronological_order_ok": order_ok,
            }
        )
        print(
            f"{ticker} | {len(eligible)} | {len(discovery)} | {len(validation)} | "
            f"{last_disc_s} | {first_val_s} | {'PASS' if order_ok else 'FAIL'}"
        )

    run_meta = {
        "experiment": "001",
        "specification": "experiments/EXPERIMENT_001.md",
        "specification_section": "§13",
        "specification_status": "LOCKED",
        "step": "27 — chronological discovery/validation partition only",
        "discovery_directory": "experiments/001/discovery/input",
        "validation_directory": "experiments/001/validation/input",
        "note": "Partitions stored separately; no combined outcome file.",
        "audit": audit_rows,
        "created_at_utc": created_at,
    }
    (ROOT / "experiments" / "001" / "partition_run.metadata.json").write_text(
        json.dumps(run_meta, indent=2) + "\n", encoding="utf-8"
    )

    print()
    if failures:
        print(f"CHRONOLOGICAL ORDER FAILED for: {', '.join(failures)}")
        sys.exit(1)
    print("All ETFs: max(discovery date) < min(validation date).")
    print("No A/B/C/D, returns, or MAE/MFE computed.")


if __name__ == "__main__":
    main()
