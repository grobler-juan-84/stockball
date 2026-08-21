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
| 001 | Momentum + Market Regime | PLANNED | —        | —               | Finalize specification |

---

# Experiment 001

## Momentum + Market Regime

**Status:** PLANNED
**Evidence:** —
**Created:** 2026-08-20
**Specification:** `experiments/EXPERIMENT_001.md`

### Research Question

Does strong ETF momentum occurring during a positive broader U.S. market regime increase the historical probability of a positive subsequent return?

### Core Hypothesis

An ETF displaying strong recent momentum while the broader U.S. market is in a positive trend will have a higher probability of producing a positive subsequent return than its unconditional historical baseline.

### Primary Philosophy

Experiment 001 follows the project's priority hierarchy:

> **Capital Preservation → Probability → Return**

The primary purpose is therefore not to maximize historical return.

We first want to determine whether the conditions meaningfully improve the probability of a positive outcome without introducing unacceptable downside.

### Initial Pattern

**Market Condition**

`SPY Close > SPY 200-Day Moving Average`

AND

**ETF Condition**

`ETF 20-Trading-Day Return > +5%`

### Forward Observation Windows

Measure subsequent returns after:

`1 / 3 / 5 / 10 / 20 trading days`

### Required Comparisons

The combined pattern must be compared against:

1. ETF unconditional historical baseline.
2. Momentum condition alone.
3. Market-regime condition alone.
4. Momentum + market-regime condition.

The important question is:

> **Does stacking the signals add useful information?**

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

**Asset Type:** ETFs
**Frequency:** Daily
**Target History:** Approximately 1998–2026
**Market Benchmark:** SPY

Each ETF may only contribute observations from the date reliable historical data becomes available.

### Success Criteria

**TO BE LOCKED BEFORE EXPERIMENT EXECUTION.**

Experiment 001 must not be run until we have explicitly defined what would constitute:

* no meaningful evidence
* weak evidence
* interesting evidence
* strong candidate

These thresholds cannot be selected after viewing the results.

### Known Limitations

To be completed before experiment lock.

Potential issues already identified:

* ETF inception dates vary.
* Early ETF coverage may be limited.
* Observations may overlap.
* ETFs may produce correlated observations.
* Current ETF selection may introduce survivorship bias.
* Gross historical returns do not equal realizable returns.

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
