"""Build Experiment 001 eligible base datasets (signal inputs only).

Authority: experiments/EXPERIMENT_001.md (LOCKED 2026-08-21).
This script implements that specification; it must not redefine methodology.

Scope (Step 26):
  For each ETF/date, align with SPY and compute only:
    - date
    - etf_close
    - etf_momentum_20d
    - spy_close
    - spy_200dma
    - eligible  (True iff both momentum and SPY 200DMA are available)

Does NOT compute:
  - A/B/C/D membership
  - forward returns
  - MAE/MFE
  - discovery/validation splits or results

Usage:
  .venv\\Scripts\\python.exe scripts\\build_experiment_001_eligible.py
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
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_DIR = ROOT / "experiments" / "001" / "eligible"

# Locked formulas from EXPERIMENT_001.md §§5, 10
MOMENTUM_LOOKBACK = 20  # close_T / close_{T-20} - 1
SPY_SMA_WINDOW = 200  # mean of closes T-199 through T


def load_universe() -> list[str]:
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    tickers = data.get("equity_etfs")
    if not isinstance(tickers, list) or not tickers:
        sys.exit(f"equity_etfs missing or empty in {UNIVERSE_PATH}")
    return [str(t).strip().upper() for t in tickers]


def load_processed(ticker: str) -> pd.DataFrame:
    path = PROCESSED_DIR / f"{ticker.lower()}_daily.csv"
    if not path.exists():
        sys.exit(f"Missing processed file (run equity pipeline first): {path}")
    df = pd.read_csv(path)
    required = {"date", "close"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"{path} missing columns: {sorted(missing)}")
    df = df[["date", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="first")
    df = df.reset_index(drop=True)
    return df


def build_spy_features(spy: pd.DataFrame) -> pd.DataFrame:
    """SPY close and 200DMA per EXPERIMENT_001.md §5.2."""
    out = spy.rename(columns={"close": "spy_close"}).copy()
    out["spy_200dma"] = out["spy_close"].rolling(window=SPY_SMA_WINDOW, min_periods=SPY_SMA_WINDOW).mean()
    return out


def build_eligible_base(etf: pd.DataFrame, spy_features: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Align ETF with SPY; compute momentum; mark eligibility per §10."""
    etf = etf.rename(columns={"close": "etf_close"}).copy()
    # §5.1: (close_T / close_{T-20}) - 1 on the ETF trading calendar
    etf["etf_momentum_20d"] = etf["etf_close"] / etf["etf_close"].shift(MOMENTUM_LOOKBACK) - 1.0

    merged = etf.merge(spy_features, on="date", how="inner")
    merged.insert(0, "ticker", ticker)

    # §10: eligible only when ETF 20-day momentum AND SPY 200DMA are available
    merged["eligible"] = merged["etf_momentum_20d"].notna() & merged["spy_200dma"].notna()

    cols = [
        "ticker",
        "date",
        "etf_close",
        "etf_momentum_20d",
        "spy_close",
        "spy_200dma",
        "eligible",
    ]
    return merged[cols]


def main() -> None:
    if not SPEC_PATH.exists():
        sys.exit(f"Missing locked specification: {SPEC_PATH}")

    tickers = load_universe()
    spy = load_processed("SPY")
    spy_features = build_spy_features(spy)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    summary_rows: list[dict] = []

    print(f"specification: {SPEC_PATH.relative_to(ROOT)} (authority)")
    print(f"universe: {UNIVERSE_PATH.relative_to(ROOT)}")
    print(f"output: {OUT_DIR.relative_to(ROOT)}")
    print()

    for ticker in tickers:
        etf = load_processed(ticker)
        base = build_eligible_base(etf, spy_features, ticker)

        out_csv = OUT_DIR / f"{ticker.lower()}_eligible_base.csv"
        # Keep ISO date strings for inspectability
        to_write = base.copy()
        to_write["date"] = to_write["date"].dt.strftime("%Y-%m-%dT00:00:00.000Z")
        to_write.to_csv(out_csv, index=False)

        eligible = base.loc[base["eligible"]]
        first_eligible = (
            eligible["date"].iloc[0].strftime("%Y-%m-%d") if len(eligible) else None
        )
        last_eligible = (
            eligible["date"].iloc[-1].strftime("%Y-%m-%d") if len(eligible) else None
        )

        meta = {
            "experiment": "001",
            "specification": "experiments/EXPERIMENT_001.md",
            "specification_status": "LOCKED",
            "specification_locked": "2026-08-21",
            "ticker": ticker,
            "source_etf": f"data/processed/{ticker.lower()}_daily.csv",
            "source_spy": "data/processed/spy_daily.csv",
            "row_count": int(len(base)),
            "eligible_row_count": int(len(eligible)),
            "first_eligible_date": first_eligible,
            "last_eligible_date": last_eligible,
            "columns": list(to_write.columns),
            "implemented_from_spec": [
                "§5.1 ETF 20-day momentum = (close_T / close_T-20) - 1",
                "§5.2 SPY_200DMA = mean(closes T-199 through T)",
                "§10 eligible iff momentum and SPY 200DMA both available",
            ],
            "explicitly_not_computed": [
                "A/B/C/D membership",
                "forward returns",
                "MAE/MFE",
                "discovery/validation split assignment for results",
            ],
            "created_at_utc": created_at,
        }
        meta_path = OUT_DIR / f"{ticker.lower()}_eligible_base.metadata.json"
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

        summary_rows.append(
            {
                "ticker": ticker,
                "rows": meta["row_count"],
                "eligible_rows": meta["eligible_row_count"],
                "first_eligible_date": first_eligible,
                "last_eligible_date": last_eligible,
                "csv": str(out_csv.relative_to(ROOT)).replace("\\", "/"),
            }
        )
        print(
            f"{ticker}: rows={meta['row_count']} eligible={meta['eligible_row_count']} "
            f"first_eligible={first_eligible}"
        )

    run_meta = {
        "experiment": "001",
        "specification": "experiments/EXPERIMENT_001.md",
        "specification_status": "LOCKED",
        "specification_locked": "2026-08-21",
        "step": "26 — eligible base / signal inputs only",
        "tickers": tickers,
        "outputs": summary_rows,
        "created_at_utc": created_at,
    }
    (OUT_DIR / "eligible_base_run.metadata.json").write_text(
        json.dumps(run_meta, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("Eligible base build complete. No A/B/C/D, returns, or MAE/MFE computed.")


if __name__ == "__main__":
    main()
