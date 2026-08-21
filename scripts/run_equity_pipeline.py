"""Orchestrate Acquire → Validate → Process for the equity research universe.

Reads config/research_universe.json and calls the existing ticker scripts.
Does not duplicate download/validate/process logic. Does not repair data.

Failure behavior (default):
  - If Acquire fails for a ticker: report, skip Validate and Process, continue.
  - If Validate fails for a ticker: report, skip Process, continue.
  - If Process fails for a ticker: report, continue.
  - After all tickers: print a summary and exit 1 if any stage failed.

Use --stop-on-error to halt at the first failed stage instead.

Examples:
  .venv\\Scripts\\python.exe scripts\\run_equity_pipeline.py --dry-run
  .venv\\Scripts\\python.exe scripts\\run_equity_pipeline.py --tickers SPY,QQQ
  .venv\\Scripts\\python.exe scripts\\run_equity_pipeline.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = ROOT / "config" / "research_universe.json"
SCRIPTS = ROOT / "scripts"

STAGES = (
    ("acquire", "download_tiingo_daily.py"),
    ("validate", "validate_tiingo_daily.py"),
    ("process", "process_tiingo_daily.py"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Acquire → Validate → Process for equity universe tickers."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned ticker/stage sequence without running anything.",
    )
    parser.add_argument(
        "--tickers",
        help="Optional comma-separated subset, e.g. SPY,QQQ (default: full universe).",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop at the first failed stage instead of continuing to the next ticker.",
    )
    return parser.parse_args()


def load_universe_tickers() -> list[str]:
    if not UNIVERSE_PATH.exists():
        sys.exit(f"Missing universe file: {UNIVERSE_PATH}")
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    tickers = data.get("equity_etfs")
    if not isinstance(tickers, list) or not tickers:
        sys.exit(f"equity_etfs missing or empty in {UNIVERSE_PATH}")
    return [str(t).strip().upper() for t in tickers]


def select_tickers(universe: list[str], subset: str | None) -> list[str]:
    if not subset:
        return universe
    requested = [t.strip().upper() for t in subset.split(",") if t.strip()]
    unknown = [t for t in requested if t not in universe]
    if unknown:
        sys.exit(f"Tickers not in research universe: {', '.join(unknown)}")
    return requested


def run_stage(script_name: str, ticker: str) -> int:
    script = SCRIPTS / script_name
    if not script.exists():
        print(f"  MISSING SCRIPT: {script}")
        return 1
    result = subprocess.run(
        [sys.executable, str(script), ticker],
        cwd=ROOT,
    )
    return int(result.returncode)


args = parse_args()
universe = load_universe_tickers()
tickers = select_tickers(universe, args.tickers)

print(f"universe file: {UNIVERSE_PATH}")
print(f"tickers ({len(tickers)}): {', '.join(tickers)}")
print(
    "failure mode: "
    + ("stop on first error" if args.stop_on_error else "continue after errors; exit 1 if any failed")
)
print()

if args.dry_run:
    for ticker in tickers:
        print(f"{ticker}")
        for stage_name, script_name in STAGES:
            print(f"  -> {stage_name}: {script_name} {ticker}")
    print()
    print("Dry run only. No Acquire / Validate / Process executed.")
    sys.exit(0)

failures: list[str] = []

for ticker in tickers:
    print("=" * 60)
    print(f"TICKER {ticker}")
    print("=" * 60)
    skip_remaining = False
    for stage_name, script_name in STAGES:
        if skip_remaining:
            reason = "prior stage failed; raw data not repaired"
            print(f"[{ticker}] SKIP {stage_name} ({reason})")
            continue

        print(f"[{ticker}] START {stage_name}")
        code = run_stage(script_name, ticker)
        if code != 0:
            failures.append(f"{ticker}:{stage_name}")
            print(f"[{ticker}] FAIL {stage_name} (exit {code})")
            skip_remaining = True
            if args.stop_on_error:
                print()
                print("Stopping early because --stop-on-error was set.")
                print(f"Failures so far: {failures}")
                sys.exit(1)
        else:
            print(f"[{ticker}] OK {stage_name}")
    print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"tickers attempted: {len(tickers)}")
print(f"failures: {len(failures)}")
if failures:
    for item in failures:
        print(f"  - {item}")
    print()
    print("One or more stages failed. No silent repairs were applied.")
    sys.exit(1)

print("All tickers completed Acquire → Validate → Process.")
sys.exit(0)
