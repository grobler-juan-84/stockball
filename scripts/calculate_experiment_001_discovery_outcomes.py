"""Calculate Experiment 001 discovery forward outcomes (mechanics only).

Authority: experiments/EXPERIMENT_001.md §§7–8, 12, 14 MAE/MFE (LOCKED 2026-08-21).
This script implements that specification; it must not redefine methodology.

For each discovery signal row (signal day T):
  Entry = T+1 adjusted open
  Return_n = (T+n adjusted close / T+1 open) - 1
  MAE_n = (min adjusted low from T+1 through T+n / T+1 open) - 1
  MFE_n = (max adjusted high from T+1 through T+n / T+1 open) - 1

Horizons n in {1, 3, 5, 10, 20}. Missing future bars → null for that horizon only (§12).

Writes: experiments/001/discovery/outcomes/
Does NOT summarize A/B/C/D performance, win rates, or evidence ratings.
Does NOT read or write validation files.

Usage:
  .venv\\Scripts\\python.exe scripts\\calculate_experiment_001_discovery_outcomes.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SPEC_PATH = ROOT / "experiments" / "EXPERIMENT_001.md"
UNIVERSE_PATH = ROOT / "config" / "research_universe.json"
PROCESSED_DIR = ROOT / "data" / "processed"
SIGNALS_DIR = ROOT / "experiments" / "001" / "discovery" / "signals"
OUTCOMES_DIR = ROOT / "experiments" / "001" / "discovery" / "outcomes"
VALIDATION_DIR = ROOT / "experiments" / "001" / "validation"

HORIZONS = (1, 3, 5, 10, 20)
SIGNAL_COLS = [
    "ticker",
    "date",
    "etf_close",
    "etf_momentum_20d",
    "spy_close",
    "spy_200dma",
    "eligible",
    "research_partition",
    "momentum_signal",
    "positive_regime",
    "group_A",
    "group_B",
    "group_C",
    "group_D",
]


def load_universe() -> list[str]:
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    return [str(t).strip().upper() for t in data["equity_etfs"]]


def load_ohlc(ticker: str) -> pd.DataFrame:
    path = PROCESSED_DIR / f"{ticker.lower()}_daily.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df = df.sort_values("date").drop_duplicates("date").reset_index(drop=True)
    return df


def compute_outcomes(signals: pd.DataFrame, ohlc: pd.DataFrame) -> pd.DataFrame:
    """Vectorized outcomes keyed by signal date T on the ETF trading calendar."""
    date_to_idx = {d: i for i, d in enumerate(ohlc["date"])}
    opens = ohlc["open"].to_numpy(dtype=float)
    highs = ohlc["high"].to_numpy(dtype=float)
    lows = ohlc["low"].to_numpy(dtype=float)
    closes = ohlc["close"].to_numpy(dtype=float)
    dates = ohlc["date"].to_numpy()
    n_bars = len(ohlc)

    sig_dates = pd.to_datetime(signals["date"], utc=True)
    t_idx = np.array([date_to_idx.get(d, -1) for d in sig_dates], dtype=int)
    if (t_idx < 0).any():
        missing = int((t_idx < 0).sum())
        sys.exit(f"Signal dates missing from processed OHLC: {missing}")

    entry_idx = t_idx + 1
    entry_ok = entry_idx < n_bars

    out = signals[SIGNAL_COLS].copy()
    out["signal_date"] = sig_dates.dt.strftime("%Y-%m-%dT00:00:00.000Z")

    entry_date_str = np.array([None] * len(signals), dtype=object)
    entry_open = np.full(len(signals), np.nan)
    if entry_ok.any():
        entry_date_str[entry_ok] = [
            pd.Timestamp(d).strftime("%Y-%m-%dT00:00:00.000Z") for d in dates[entry_idx[entry_ok]]
        ]
        entry_open[entry_ok] = opens[entry_idx[entry_ok]]
    out["entry_date"] = entry_date_str
    out["entry_open"] = entry_open

    for h in HORIZONS:
        exit_idx = t_idx + h
        horizon_ok = entry_ok & (exit_idx < n_bars)

        ret = np.full(len(signals), np.nan)
        mae = np.full(len(signals), np.nan)
        mfe = np.full(len(signals), np.nan)
        exit_date_str = np.array([None] * len(signals), dtype=object)

        for i in np.where(horizon_ok)[0]:
            e = int(entry_idx[i])
            x = int(exit_idx[i])
            entry = opens[e]
            ret[i] = closes[x] / entry - 1.0
            mae[i] = lows[e : x + 1].min() / entry - 1.0
            mfe[i] = highs[e : x + 1].max() / entry - 1.0
            exit_date_str[i] = pd.Timestamp(dates[x]).strftime("%Y-%m-%dT00:00:00.000Z")

        out[f"exit_date_{h}d"] = exit_date_str
        out[f"return_{h}d"] = ret
        out[f"mae_{h}d"] = mae
        out[f"mfe_{h}d"] = mfe
        out[f"horizon_{h}d_available"] = horizon_ok

    return out


def structural_validate(out: pd.DataFrame, ohlc: pd.DataFrame, ticker: str) -> list[str]:
    """Return list of failure messages (empty = PASS). Never prints return values."""
    failures: list[str] = []
    sig = pd.to_datetime(out["date"], utc=True)
    entry = pd.to_datetime(out["entry_date"], utc=True)
    has_entry = entry.notna()

    if (has_entry & ~(entry > sig)).any():
        failures.append(f"{ticker}: entry_date not strictly after signal date T")

    date_to_idx = {d: i for i, d in enumerate(ohlc["date"])}
    for h in HORIZONS:
        avail = out[f"horizon_{h}d_available"]
        exit_d = pd.to_datetime(out[f"exit_date_{h}d"], utc=True)
        if (avail & exit_d.isna()).any():
            failures.append(f"{ticker}: {h}d available but exit_date missing")
        if (~avail & exit_d.notna()).any():
            failures.append(f"{ticker}: {h}d unavailable but exit_date present")

        for i in out.index[avail]:
            t_i = date_to_idx[sig.iloc[i]]
            e_i = date_to_idx[entry.iloc[i]]
            x_i = date_to_idx[exit_d.iloc[i]]
            if e_i != t_i + 1:
                failures.append(f"{ticker}: entry not T+1 trading day")
                break
            if x_i != t_i + h:
                failures.append(f"{ticker}: exit_{h}d not T+{h} trading day")
                break

        mae = out.loc[avail, f"mae_{h}d"]
        mfe = out.loc[avail, f"mfe_{h}d"]
        if (mae > mfe + 1e-12).any():
            failures.append(f"{ticker}: MAE > MFE at {h}d")

    # Shorter horizons available whenever longer ones are (when entry exists)
    for i, row in out.iterrows():
        if not bool(row.get("horizon_1d_available", False)) and any(
            row[f"horizon_{h}d_available"] for h in HORIZONS if h > 1
        ):
            failures.append(f"{ticker}: longer horizon available without 1d")
            break
        prev = True
        for h in HORIZONS:
            cur = bool(row[f"horizon_{h}d_available"])
            if cur and not prev:
                # allow only if entry missing entirely handled above; if 3d ok, 1d must ok
                failures.append(f"{ticker}: horizon availability not nested")
                break
            prev = cur
        else:
            continue
        break

    # Signal/group columns unchanged vs source file check done in main via hash of cols
    for col in SIGNAL_COLS:
        if col not in out.columns:
            failures.append(f"{ticker}: missing signal column {col}")

    return failures


def mechanical_sample_audit(out: pd.DataFrame, ohlc: pd.DataFrame, ticker: str) -> list[str]:
    """Recompute a few deterministic rows from OHLC; report PASS/FAIL only (no values)."""
    failures: list[str] = []
    n = len(out)
    sample_idx = sorted({0, n // 2, max(0, n - 1), max(0, n - 5)})
    date_to_idx = {d: i for i, d in enumerate(ohlc["date"])}
    sig = pd.to_datetime(out["date"], utc=True)

    for i in sample_idx:
        t_i = date_to_idx[sig.iloc[i]]
        if t_i + 1 >= len(ohlc):
            # no entry — all horizons must be unavailable
            for h in HORIZONS:
                if bool(out.iloc[i][f"horizon_{h}d_available"]):
                    failures.append(f"{ticker} sample[{i}]: horizon marked available without entry")
            continue
        entry = float(ohlc.iloc[t_i + 1]["open"])
        for h in HORIZONS:
            if t_i + h >= len(ohlc):
                if bool(out.iloc[i][f"horizon_{h}d_available"]):
                    failures.append(f"{ticker} sample[{i}]: {h}d available past series end")
                continue
            window = ohlc.iloc[t_i + 1 : t_i + h + 1]
            exp_ret = float(ohlc.iloc[t_i + h]["close"]) / entry - 1.0
            exp_mae = float(window["low"].min()) / entry - 1.0
            exp_mfe = float(window["high"].max()) / entry - 1.0
            got_ret = float(out.iloc[i][f"return_{h}d"])
            got_mae = float(out.iloc[i][f"mae_{h}d"])
            got_mfe = float(out.iloc[i][f"mfe_{h}d"])
            if not np.isclose(got_ret, exp_ret, rtol=0, atol=1e-12):
                failures.append(f"{ticker} sample[{i}]: return_{h}d mismatch")
            if not np.isclose(got_mae, exp_mae, rtol=0, atol=1e-12):
                failures.append(f"{ticker} sample[{i}]: mae_{h}d mismatch")
            if not np.isclose(got_mfe, exp_mfe, rtol=0, atol=1e-12):
                failures.append(f"{ticker} sample[{i}]: mfe_{h}d mismatch")
            if got_mae > got_mfe + 1e-12:
                failures.append(f"{ticker} sample[{i}]: MAE > MFE")
    return failures


def assert_validation_untouched() -> None:
    if (VALIDATION_DIR / "outcomes").exists():
        sys.exit("validation/outcomes exists — validation must remain untouched")
    if (VALIDATION_DIR / "signals").exists():
        sys.exit("validation/signals exists — validation must remain untouched")


def main() -> None:
    if not SPEC_PATH.exists():
        sys.exit(f"Missing locked specification: {SPEC_PATH}")
    assert_validation_untouched()

    tickers = load_universe()
    OUTCOMES_DIR.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    all_failures: list[str] = []
    audit_summary: list[dict] = []

    print(f"specification: {SPEC_PATH.relative_to(ROOT)} (authority)")
    print(f"signals:  {SIGNALS_DIR.relative_to(ROOT)}")
    print(f"outcomes: {OUTCOMES_DIR.relative_to(ROOT)}")
    print("validation: not read / not written")
    print()

    for ticker in tickers:
        sig_path = SIGNALS_DIR / f"{ticker.lower()}_discovery_signals.csv"
        if not sig_path.exists():
            sys.exit(f"Missing discovery signals (run Step 28 first): {sig_path}")

        signals = pd.read_csv(sig_path)
        # Preserve signal/group columns exactly
        for col in SIGNAL_COLS:
            if col not in signals.columns:
                sys.exit(f"{ticker}: signals missing {col}")

        ohlc = load_ohlc(ticker)
        outcomes = compute_outcomes(signals, ohlc)

        # Unchanged signal columns
        for col in SIGNAL_COLS:
            if col in ("date",):
                # date string formatting may normalize; compare as timestamps
                if not (
                    pd.to_datetime(outcomes[col], utc=True)
                    == pd.to_datetime(signals[col], utc=True)
                ).all():
                    all_failures.append(f"{ticker}: signal column date altered")
            elif outcomes[col].astype(str).tolist() != signals[col].astype(str).tolist():
                # bools/floats compare via values
                if not outcomes[col].equals(signals[col]):
                    all_failures.append(f"{ticker}: signal/group column {col} altered")

        struct_fail = structural_validate(outcomes, ohlc, ticker)
        sample_fail = mechanical_sample_audit(outcomes, ohlc, ticker)
        fails = struct_fail + sample_fail
        all_failures.extend(fails)

        # Availability counts only (not performance)
        avail_counts = {
            f"horizon_{h}d_available_count": int(outcomes[f"horizon_{h}d_available"].sum())
            for h in HORIZONS
        }

        out_csv = OUTCOMES_DIR / f"{ticker.lower()}_discovery_outcomes.csv"
        outcomes.to_csv(out_csv, index=False)

        meta = {
            "experiment": "001",
            "specification": "experiments/EXPERIMENT_001.md",
            "specification_sections": [
                "§7 Signal and Execution Timing",
                "§8 Forward Observation Windows",
                "§12 End-of-Series Handling",
                "§14 MAE/MFE definition",
            ],
            "specification_status": "LOCKED",
            "specification_locked": "2026-08-21",
            "ticker": ticker,
            "research_partition": "discovery",
            "source_signals": str(sig_path.relative_to(ROOT)).replace("\\", "/"),
            "source_ohlc": f"data/processed/{ticker.lower()}_daily.csv",
            "output_csv": str(out_csv.relative_to(ROOT)).replace("\\", "/"),
            "row_count": int(len(outcomes)),
            "entry_available_count": int(outcomes["entry_open"].notna().sum()),
            **avail_counts,
            "structural_validation": "PASS" if not fails else "FAIL",
            "mechanical_sample_audit": "PASS" if not sample_fail else "FAIL",
            "explicitly_not_computed": [
                "A/B/C/D win rates",
                "mean/median returns by group",
                "D-vs-B comparisons",
                "evidence classification",
                "charts",
            ],
            "created_at_utc": created_at,
        }
        (OUTCOMES_DIR / f"{ticker.lower()}_discovery_outcomes.metadata.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )

        status = "PASS" if not fails else "FAIL"
        print(
            f"{ticker}: rows={len(outcomes)} "
            f"avail_1/3/5/10/20="
            f"{avail_counts['horizon_1d_available_count']}/"
            f"{avail_counts['horizon_3d_available_count']}/"
            f"{avail_counts['horizon_5d_available_count']}/"
            f"{avail_counts['horizon_10d_available_count']}/"
            f"{avail_counts['horizon_20d_available_count']} "
            f"structural+sample={status}"
        )
        audit_summary.append(
            {
                "ticker": ticker,
                "status": status,
                **avail_counts,
            }
        )

    assert_validation_untouched()

    run_meta = {
        "experiment": "001",
        "step": "29 — discovery outcomes calculated; no performance summary",
        "specification": "experiments/EXPERIMENT_001.md",
        "outcomes_directory": "experiments/001/discovery/outcomes",
        "validation_touched": False,
        "audit": audit_summary,
        "created_at_utc": created_at,
    }
    (OUTCOMES_DIR / "discovery_outcomes_run.metadata.json").write_text(
        json.dumps(run_meta, indent=2) + "\n", encoding="utf-8"
    )

    print()
    if all_failures:
        print(f"VALIDATION FAILED ({len(all_failures)} issue(s)):")
        for msg in all_failures[:20]:
            print(f"  - {msg}")
        if len(all_failures) > 20:
            print(f"  ... and {len(all_failures) - 20} more")
        sys.exit(1)

    print("All tickers: structural checks PASS; mechanical sample audits PASS.")
    print("No performance summaries. Validation untouched.")


if __name__ == "__main__":
    main()
