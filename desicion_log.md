# Stockball Stock — Decision Log

## Purpose

This file records important project decisions so they are not lost between conversations.

Keep entries short. Record **what was decided and why**. Do not rewrite old decisions; if a decision changes, add a new entry.

---

## 2026-08-21 — Initial Research Universe

### Equity Markets

* `SPY` — broad US market
* `QQQ` — Nasdaq / growth
* `IWM` — small caps
* All 11 major SPDR sector ETFs
* `QQQ` and `IWM` may be studied both as assets and market-context indicators.

### Other Markets

* **Gold** — underlying market data; research asset + context variable.
* **US Dollar / DXY** — underlying index data; research market + context variable.
* **Crude Oil** — research asset + context variable.

### Macro Context

* US Treasury yields: **3-month, 2-year, 10-year**
* **VIX**
* **CPI**

These are initially context variables rather than tradeable assets.

### Historical Data

Use the **maximum reliable historical data available for each variable**.

Do not fabricate history to make datasets equal in length. Different eras may themselves be useful for studying changing market relationships.

### Phase 1 Data Storage

Use **CSV files** for simplicity, transparency, and inspectability.

Initial data structure:

`data/raw/`

`data/processed/`

`experiments/`

`results/`

Raw data must remain separate from transformed data.
