"""Classify Experiment 001 A/B/C/D signal groups on discovery inputs only.

Authority: experiments/EXPERIMENT_001.md §§5, 9 (LOCKED 2026-08-21).
This script implements that specification; it must not redefine methodology.

For each eligible discovery row, overlapping boolean membership:
  momentum_signal = etf_momentum_20d > 0.05   (strict >)
  positive_regime = spy_close > spy_200dma     (strict >)
  group_A = True
  group_B = momentum_signal
  group_C = positive_regime
  group_D = momentum_signal AND positive_regime

A/B/C/D are overlapping comparison sets, not mutually exclusive buckets.

Reads:  experiments/001/discovery/input/
Writes: experiments/001/discovery/signals/

Does NOT:
  - compute forward returns, win rates, MAE/MFE, or other outcomes
  - classify or inspect validation partition files

Usage:
  .venv\\Scripts\\python.exe scripts\\classify_experiment_001_discovery_groups.py
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
DISCOVERY_IN = ROOT / "experiments" / "001" / "discovery" / "input"
DISCOVERY_SIGNALS = ROOT / "experiments" / "001" / "discovery" / "signals"

# Locked thresholds from EXPERIMENT_001.md §5
MOMENTUM_THRESHOLD = 0.05  # strict >


def load_universe() -> list[str]:
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    return [str(t).strip().upper() for t in data["equity_etfs"]]


def classify(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if not (out["research_partition"] == "discovery").all():
        bad = out.loc[out["research_partition"] != "discovery", "research_partition"].unique()
        sys.exit(f"Expected discovery-only rows; found partitions: {bad}")

    # §5 strict inequalities
    out["momentum_signal"] = out["etf_momentum_20d"] > MOMENTUM_THRESHOLD
    out["positive_regime"] = out["spy_close"] > out["spy_200dma"]

    # §9 overlapping groups
    out["group_A"] = True
    out["group_B"] = out["momentum_signal"]
    out["group_C"] = out["positive_regime"]
    out["group_D"] = out["momentum_signal"] & out["positive_regime"]
    return out


def main() -> None:
    if not SPEC_PATH.exists():
        sys.exit(f"Missing locked specification: {SPEC_PATH}")

    tickers = load_universe()
    DISCOVERY_SIGNALS.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    audit: list[dict] = []
    inequality_failures: list[str] = []

    print(f"specification: {SPEC_PATH.relative_to(ROOT)} §§5,9 (authority)")
    print(f"input:  {DISCOVERY_IN.relative_to(ROOT)}")
    print(f"output: {DISCOVERY_SIGNALS.relative_to(ROOT)}")
    print("validation: not read / not classified")
    print()
    print("Ticker | A count | B count | C count | D count | Inequalities OK")

    for ticker in tickers:
        src = DISCOVERY_IN / f"{ticker.lower()}_discovery_input.csv"
        if not src.exists():
            sys.exit(f"Missing discovery input (run Step 27 first): {src}")

        raw = pd.read_csv(src)
        classified = classify(raw)

        a = int(classified["group_A"].sum())
        b = int(classified["group_B"].sum())
        c = int(classified["group_C"].sum())
        d = int(classified["group_D"].sum())

        # Sanity: overlapping-set inequalities
        ok = (d <= b) and (d <= c) and (b <= a) and (c <= a) and (a == len(classified))
        if not ok:
            inequality_failures.append(ticker)

        out_csv = DISCOVERY_SIGNALS / f"{ticker.lower()}_discovery_signals.csv"
        classified.to_csv(out_csv, index=False)

        meta = {
            "experiment": "001",
            "specification": "experiments/EXPERIMENT_001.md",
            "specification_sections": ["§5 Exact Signal Definitions", "§9 A/B/C/D Comparison Groups"],
            "specification_status": "LOCKED",
            "specification_locked": "2026-08-21",
            "ticker": ticker,
            "research_partition": "discovery",
            "source_csv": str(src.relative_to(ROOT)).replace("\\", "/"),
            "output_csv": str(out_csv.relative_to(ROOT)).replace("\\", "/"),
            "row_count": int(len(classified)),
            "group_A_count": a,
            "group_B_count": b,
            "group_C_count": c,
            "group_D_count": d,
            "inequalities_ok": ok,
            "group_semantics": "overlapping comparison sets (not mutually exclusive)",
            "explicitly_not_computed": [
                "forward returns",
                "win rates / average returns",
                "MAE/MFE",
                "validation classification",
            ],
            "created_at_utc": created_at,
        }
        (DISCOVERY_SIGNALS / f"{ticker.lower()}_discovery_signals.metadata.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )

        audit.append(
            {
                "ticker": ticker,
                "A": a,
                "B": b,
                "C": c,
                "D": d,
                "inequalities_ok": ok,
            }
        )
        print(f"{ticker} | {a} | {b} | {c} | {d} | {'PASS' if ok else 'FAIL'}")

    run_meta = {
        "experiment": "001",
        "specification": "experiments/EXPERIMENT_001.md",
        "step": "28 — discovery A/B/C/D signal classification only",
        "discovery_signals_directory": "experiments/001/discovery/signals",
        "validation_touched": False,
        "audit": audit,
        "created_at_utc": created_at,
    }
    (DISCOVERY_SIGNALS / "discovery_signals_run.metadata.json").write_text(
        json.dumps(run_meta, indent=2) + "\n", encoding="utf-8"
    )

    print()
    if inequality_failures:
        print(f"Inequality check FAILED for: {', '.join(inequality_failures)}")
        sys.exit(1)
    print("All ETFs: D≤B, D≤C, B≤A, C≤A.")
    print("Validation left untouched. No outcomes computed.")


if __name__ == "__main__":
    main()
