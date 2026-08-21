# Stockball Stock — Experiment Registry

## Purpose

This registry is the permanent research ledger for Stockball Stock.

Every experiment receives a unique ID and remains recorded regardless of whether the result is positive, negative, boring, or inconclusive.

> **Experiments are never deleted because they failed.**

Detailed methodology belongs in each experiment's individual specification file. This registry records what we tested, what we found, and what happened next.

---

# Status Definitions

* **PLANNED** — Specification being prepared.
* **LOCKED** — Methodology frozen; ready to run.
* **RUNNING** — Experiment currently executing.
* **COMPLETED** — Results generated and recorded.
* **VALIDATION** — Promising result undergoing independent validation.
* **REJECTED** — Evidence does not support further investigation.
* **ARCHIVED** — Retained for research history but no longer active.

---

# Evidence Ratings

Results should not simply be classified as "works" or "doesn't work."

Use:

* **INCONCLUSIVE**
* **WEAK**
* **INTERESTING**
* **STRONG CANDIDATE**
* **VALIDATED**
* **FAILED VALIDATION**

A strong historical result is not automatically a validated pattern.

---

# Experiment Index

| ID  | Experiment               | Status  | Evidence | Primary Outcome | Next Step              |
| --- | ------------------------ | ------- | -------- | --------------- | ---------------------- |
| 001 | Momentum + Market Regime | LOCKED  | —        | —               | Implement / run discovery     |

---

# Experiment 001

## Momentum + Market Regime

**Status:** LOCKED  
**Evidence:** —  
**Created:** 2026-08-20  
**Locked:** 2026-08-21  
**Specification:** `experiments/EXPERIMENT_001.md`

### Research Question

Does strong ETF momentum occurring during a positive broader U.S. market regime increase the historical probability of a positive subsequent return?

### Core Hypothesis

An ETF displaying strong recent momentum while the broader U.S. market is in a positive trend will have a higher probability of producing a positive subsequent return than its unconditional historical baseline and than momentum alone, without introducing unacceptable downside deterioration.

### Primary Philosophy

Experiment 001 follows the project's priority hierarchy:

> **Capital Preservation → Probability → Return**

The primary purpose is therefore not to maximize historical return.

We first want to determine whether adding market-regime information to momentum meaningfully improves probability and/or downside characteristics.

### Initial Pattern

**Market Condition**

`SPY adjusted close > SPY 200-Day SMA` (strict `>`; SMA uses closes T-199 through T)

AND

**ETF Condition**

`ETF 20-trading-day momentum > +5%` (strict `>`; `(close_T / close_{T-20}) - 1`)

**Timing:** signal at T close; earliest entry T+1 open; horizons exit at T+1 / T+3 / T+5 / T+10 / T+20 close; return = `(exit close / T+1 open) - 1`.

### Forward Observation Windows

Measure subsequent returns over observation horizons:

`1 / 3 / 5 / 10 / 20 trading days`

These are standardized observation windows, not optimized trading exits.

### Required Comparisons

Calculate and compare A/B/C/D:

1. **A** — ETF unconditional baseline (aligned eligible period only).
2. **B** — Momentum alone.
3. **C** — Market-regime alone.
4. **D** — Momentum + market-regime.

**Primary incremental comparison:** `D vs B` (does regime earn its complexity on top of momentum?).

Also report `D vs A`, `D vs C`, `B vs A`, `C vs A` where useful.

**Reporting:** SPY individually; each non-SPY ETF individually; pooled **13 non-SPY** ETFs (SPY excluded from the pool). Pooled results must not obscure individual ETF results.

### Primary Measurements

* Observation count
* Positive outcome rate
* Negative outcome rate
* Mean return
* Median return
* Average winner
* Average loser
* Median winner
* Median loser
* Bottom 10% outcome
* Bottom 5% outcome
* Worst historical outcome
* Maximum Adverse Excursion (MAE)
* Maximum Favorable Excursion (MFE)

### Dataset

**Asset Type:** ETFs from `config/research_universe.json`  
**Frequency:** Daily  
**Processed prices:** adjusted OHLCV  
**Market Benchmark:** SPY  

Each ETF may only contribute observations from the date reliable historical data becomes available. A/B/C/D share the same eligible period per ETF (momentum + SPY 200DMA computable). Horizons evaluated independently when forward closes exist.

**Discovery / validation:** 80% / 20% chronological per ETF eligible history. Validation remains hidden until discovery is assessed against predefined criteria. No parameter changes after lock based on discovery outcomes.

### Success Criteria

Documented in full in `experiments/EXPERIMENT_001.md`. Summary of the predefined evidence framework (must not be chosen after seeing results):

* Evidence prioritizes **Capital Preservation → Probability → Return**. Win rate alone is insufficient; downside is a multi-metric gate (D vs B: average/median loser, bottom 10%/5%, worst outcome, MAE).
* **Primary incremental test:** D versus B positive-outcome rate.
* **INCONCLUSIVE** — insufficient sample, mixed results, or no consistent D-vs-B improvement.
* **WEAK** — some D-vs-B improvement, but small/inconsistent or concerning downside.
* **INTERESTING** — normally D positive-outcome rate ≥ B + **~3 percentage points**, with ≥ **500** pooled non-SPY D observations, D-vs-B improvement on ≥ **7/13** non-SPY ETFs and ≥ **3/5** horizons, and no clear material multi-metric downside deterioration vs B.
* **STRONG CANDIDATE** — normally D ≥ B + **~5 percentage points**, prefer ≥ **1,000** pooled non-SPY D observations, broader consistency (target ≥ **9/13** ETFs and ≥ **4/5** horizons), and **improved or broadly comparable** downside vs B (win-rate lift cannot override obviously worse tails).
* **MAE/MFE:** `(min low / T+1 open) - 1` and `(max high / T+1 open) - 1` over T+1 through exit day; daily bars do not establish intraday path order.
* Pooled observation counts are **not** independent-trial counts. Experiment 001 is **descriptive**; no formal statistical inference / naïve p-value in 001.
* SPY reported separately from the pooled 13 non-SPY ETFs.
* Validation remains hidden until discovery evaluation is complete.

**Methodology locked 2026-08-21.** Do not alter Experiment 001 after seeing results; create a descendant experiment instead.

### Known Limitations

* ETF inception dates vary; some sector ETFs (e.g. XLC, XLRE) have substantially shorter histories.
* Current ETF selection may contain survivorship bias.
* Consecutive qualifying observations are correlated; forward holding periods overlap.
* ETFs are correlated; shared market regimes further cluster outcomes.
* SPY defines the regime and is reported separately from pooled non-SPY results.
* Gross historical returns ≠ realizable net returns (no costs/slippage/taxes/impact modeled).
* T+1 open is a standardized execution assumption, not a guaranteed historical fill.
* Discovery/validation cutoff dates differ by ETF because eligible histories differ.
* Experiment 001 uses actual ETF history only — no synthetic pre-inception ETF backfill from sector/index/spot series.
* Pooled/overlapping observations are acknowledged; Experiment 001 reports descriptive empirical evidence only (no formal dependence-aware inference or naïve p-value criterion).
* Downside “material deterioration” is a predefined multi-metric qualitative gate vs B (no single numeric cutoff).
* MAE/MFE measured from T+1 adjusted open using min adjusted low / max adjusted high through each exit day; daily OHLC does not imply intraday path ordering.

### Result

**NOT YET RUN**

### Interpretation

**NOT YET AVAILABLE**

### Follow-Up Questions

**NOT YET AVAILABLE**

Follow-up hypotheses should only be created after Experiment 001 has been completed and its original result permanently recorded.

### Experiment Lineage

```text
Experiment 001
      │
      └── Pending
```

---

# Future Experiment Queue

Ideas may be recorded here without becoming formal experiments.

Potential research directions currently include:

* Sector relative strength
* 5-day vs 20-day momentum
* Distance from 52-week high
* Relative volume
* Volatility contraction/expansion
* Drawdown/recovery behavior
* Multiple market-regime definitions
* Momentum during bear markets
* Sector leadership rotation
* VIX regime
* Interest-rate regime
* Signal stacking
* Exit behavior
* MAE/MFE relationships

These are **research ideas only**.

They must not influence Experiment 001 after its methodology has been locked.

---

# Experiment Lineage Map

As Stockball grows, experiments should form a research tree rather than an unstructured collection of backtests.

Example:

```text
001 — Momentum + Market Regime
 │
 ├── 002 — Add Sector Strength
 │    ├── 005 — Sector Strength Threshold Test
 │    └── 006 — Sector Leadership Persistence
 │
 ├── 003 — Add Relative Volume
 │    └── 007 — Volume Threshold Test
 │
 └── 004 — Bear Market Momentum
```

This allows us to see not only **what worked**, but how each hypothesis evolved.

---

# Registry Rules

1. Every executed experiment receives a permanent ID.
2. IDs are never reused.
3. Completed experiments are never silently modified.
4. Failed experiments remain recorded.
5. Changes to methodology create new experiments.
6. Experiment specifications must be locked before execution.
7. Raw results must be saved before interpretation.
8. Evidence ratings must reflect uncertainty.
9. Promising discoveries require validation.
10. The registry records history — it does not rewrite it.

---

# Current Research State

**Experiments Planned:** 1
**Experiments Completed:** 0
**Strong Candidates:** 0
**Validated Patterns:** 0
**Rejected Patterns:** 0

---

> **The purpose of this registry is not to build a list of winning strategies.**
>
> **It is to preserve an honest record of what we asked, what the evidence said, and what we learned.**
