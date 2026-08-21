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
