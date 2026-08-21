# Stockball — Project Steps

Running log of work done in this project, one entry per prompt/session step.
Agents must append the next numbered step after every prompt (see `.cursor/rules/project-steps.mdc`).

---

## Step 1 — Rename Moneyball to Stockball (manifesto)

Updated all "Moneyball" references in `docs/project_manifesto.md` to "Stockball".

## Step 2 — Rename Moneyball to Stockball (rules)

Updated all "Moneyball" references in `docs/project_rules.md` to "Stockball".

## Step 3 — Rename Moneyball to Stockball (registry)

Updated all "Moneyball" references in `docs/project_registry` / `docs/project_registry.md` to "Stockball".

## Step 4 — Initial research environment setup

Installed Python 3.12.10, created `.venv`, installed pandas/numpy/requests/python-dotenv/matplotlib, added `.gitignore`, `.env.example`, `requirements.txt`, data directory `.gitkeep` files, initialized Git on `main`, and created initial commit `598fbb8` (no Tiingo calls; `.env.local` kept private).

## Step 5 — Connect local Git to GitHub

Added `origin` → `https://github.com/grobler-juan-84/stockball.git`, pushed `main` with upstream tracking. Commit `598fbb8` on remote; `.env.local` remained untracked.

## Step 6 — Tiingo SPY connectivity smoke test

Added `scripts/test_tiingo_spy.py` and confirmed `.env.local → Python → Tiingo → SPY` works. Printed 13 fields and a ~10-day sample; nothing saved to `data/raw/`.

## Step 7 — Download SPY maximum daily history (raw)

Added `scripts/download_spy_tiingo_daily.py`, fetched SPY daily from 1993-01-29 through today, wrote `data/raw/spy_tiingo_daily.csv` (8,447 rows, 13 fields) and `data/raw/spy_tiingo_daily.metadata.json` with no transforms.

## Step 8 — Validate raw SPY download

Added `scripts/validate_spy_tiingo_daily.py` (Acquire → Validate). All structural/sanity checks passed; noted 135 dividend rows and 0 split rows. No repairs; no `data/processed/` output.

## Step 9 — Project steps log and Cursor rule

Created this `project_steps.md` file and `.cursor/rules/project-steps.mdc` so every subsequent prompt appends the next numbered step with a short summary.

## Step 10 — Create processed SPY adjusted-price base

Added `scripts/process_spy_daily.py` and wrote `data/processed/spy_daily.csv` plus `data/processed/spy_daily.metadata.json`. Selected/renamed Tiingo `adjOpen`/`adjHigh`/`adjLow`/`adjClose`/`adjVolume` to `open`/`high`/`low`/`close`/`volume` (with `date`); no rows dropped, no values altered, no indicators or returns calculated.

## Step 11 — Commit and push research scripts to GitHub

Committed Tiingo smoke/download/validate/process scripts, `project_steps.md`, the project-steps Cursor rule, and `communication_protocol.md`; pushed `main` to `origin`. Raw/processed CSVs and `.env.local` remained untracked.

## Step 12 — Generalize Tiingo daily download by ticker

Added `scripts/download_tiingo_daily.py` so any ticker can be downloaded with the same raw-data rules (`python scripts/download_tiingo_daily.py SPY` / `QQQ`). Turned `download_spy_tiingo_daily.py` into a thin SPY wrapper. Did not download QQQ yet; validate/process remain SPY-specific for now.

## Step 13 — Download QQQ maximum daily history (raw)

Ran `scripts/download_tiingo_daily.py QQQ` and wrote `data/raw/qqq_tiingo_daily.csv` plus metadata (6,905 rows, 13 Tiingo fields, 1999-03-10 through 2026-08-20). No validation, processing, or indicators.

## Step 14 — Generalize raw validation and validate QQQ

Added `scripts/validate_tiingo_daily.py` (same checks as the SPY validator, ticker argument; row count taken from each file's metadata). Turned `validate_spy_tiingo_daily.py` into a thin wrapper. Ran validation on QQQ only: **PASS** (6,905 rows; 88 dividend rows; 1 split row). No processing or indicators.

## Step 15 — Generalize adjusted-price processing and process QQQ

Added `scripts/process_tiingo_daily.py` (same adj\* → OHLCV rename as SPY) and turned `process_spy_daily.py` into a thin wrapper. Processed QQQ only → `data/processed/qqq_daily.csv` + metadata (6,905 rows; 0 dropped; close equals raw adjClose). No returns, momentum, or moving averages.

## Step 16 — Run IWM through Acquire → Validate → Process

Ran existing generic scripts only (`download_tiingo_daily.py`, `validate_tiingo_daily.py`, `process_tiingo_daily.py`) for IWM — no machinery changes. Acquire 6,597 rows (2000-05-26 → 2026-08-20); Validate **PASS** (105 dividend rows, 1 split row); Process wrote `iwm_daily.csv` with 0 rows dropped and close == raw adjClose.

## Step 17 — Create machine-readable initial equity research universe

Added `config/research_universe.json` with SPY, QQQ, IWM, and the 11 SPDR sector ETFs (14 tickers). Notes that XLC/XLRE have shorter histories and must not be backfilled for symmetry. No scripts consume this file yet; no new downloads or indicators.

## Step 18 — Commit generalized ETF data pipeline to GitHub

Committed ticker-parameterized download/validate/process scripts, SPY thin wrappers, `config/research_universe.json`, and updated `project_steps.md` (Steps 12–18); pushed `main` to `origin`. Raw/processed CSVs and `.env.local` remained untracked.

## Step 19 — Create equity-universe pipeline runner

Added `scripts/run_equity_pipeline.py` to orchestrate Acquire → Validate → Process from `config/research_universe.json` by calling existing scripts (no duplicated logic). On stage failure: skip remaining stages for that ticker, do not repair data, continue by default (optional `--stop-on-error`); exit 1 if any failed. Built and dry-run inspected only — full 14-ETF run not executed. No indicators or Experiment 001.

## Step 20 — Run full equity universe through Acquire → Validate → Process

Ran `scripts/run_equity_pipeline.py` for all 14 equity ETFs. All completed Acquire → Validate → Process with 0 failures. Shorter histories observed as expected for XLC (2018-06-19) and XLRE (2015-10-08). No indicators or Experiment 001.

## Step 21 — Commit and push equity universe milestone to GitHub

Committed the equity-universe pipeline runner and project step log through Step 21 (full 14-ETF Acquire → Validate → Process milestone); pushed `main` to `origin`. Raw/processed CSVs and `.env.local` remained untracked.

## Step 22 — Formalize Experiment 001 specification (documentation only)

Created/updated `experiments/EXPERIMENT_001.md` with the complete agreed methodology (T/T+1 timing, A/B/C/D with D-vs-B primary, aligned eligibility, 80/20 hidden validation, evidence thresholds, downside gate, SPY-separate vs pooled-13 reporting). Synchronized Success Criteria and Known Limitations in `docs/project_registry.md`. Status remains **PLANNED** (not locked, not executed). No indicators, datasets, or results generated.

## Step 23 — Resolve Experiment 001 pre-lock methodology flags

Updated `experiments/EXPERIMENT_001.md` and `docs/project_registry.md`: downside = multi-metric qualitative D-vs-B gate (no single numeric cutoff); MAE/MFE from T+1 open via min low / max high through exit day (no intraday path ordering); no formal statistical inference in 001 (descriptive evidence only). Status remains **PLANNED**.

## Step 24 — Lock Experiment 001 methodology

Final consistency check between `experiments/EXPERIMENT_001.md` and the Experiment 001 registry entry found no contradictions or unresolved methodological ambiguities. Changed status **PLANNED → LOCKED** (lock date **2026-08-21**) in the specification and registry index. No methodological edits beyond the status lock; no experiment code or results.

## Step 25 — Commit and push Experiment 001 lock to GitHub

Committed `experiments/EXPERIMENT_001.md`, updated `docs/project_registry.md`, and `project_steps.md` through Step 25 (Experiment 001 methodology LOCKED 2026-08-21); pushed `main` to `origin`. No experiment code or results included.
