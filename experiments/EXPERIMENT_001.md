# Experiment 001 — Momentum + Market Regime

**Status:** LOCKED  
**Evidence:** —  
**Created:** 2026-08-20  
**Specification formalized:** 2026-08-21  
**Locked:** 2026-08-21  
**Registry:** `docs/project_registry.md`  
**Universe:** `config/research_universe.json`

This document is the **frozen** methodology for Experiment 001. From the lock date onward, it must not be modified to improve results. Any methodological change requires a **new experiment ID**. Status is `LOCKED` (ready to implement/run); results are not yet generated.

---

## 1. Research Question

> Does strong ETF momentum occurring during a positive broader U.S. market regime increase the historical probability of a positive subsequent return?

The central comparison is whether adding the broader market regime to momentum provides useful **incremental** information.

This experiment is **not** primarily attempting to maximize historical return.

Priority hierarchy:

> **Capital Preservation → Probability → Return**

---

## 2. Core Hypothesis

> An ETF displaying strong recent momentum while the broader U.S. market is in a positive trend will have a higher probability of producing a positive subsequent return than its unconditional historical baseline and than momentum alone, without introducing unacceptable downside deterioration.

---

## 3. Research Universe

Use the machine-readable universe in `config/research_universe.json`.

Current equity ETFs (14):

```text
SPY, QQQ, IWM, XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY
```

This universe must not be changed for Experiment 001 without creating a new experiment.

Prices: processed adjusted OHLCV series in `data/processed/{ticker}_daily.csv` (Tiingo adjusted fields renamed to open/high/low/close/volume).

---

## 4. SPY Treatment

SPY has two roles:

1. Broader-market **regime benchmark**.
2. A **research asset** tested under the same pattern rules.

Because SPY participates in defining the market regime:

* Report **SPY individually**.
* Report **every other ETF individually**.
* Produce a **pooled result for the 13 non-SPY ETFs**.
* **Do not** include SPY in the pooled 13-ETF result.
* The pooled result must never replace or obscure individual ETF results.

Analysis must allow identification of whether a pooled effect is broadly distributed or driven by only a few ETFs.

---

## 5. Exact Signal Definitions

Both conditions use **strict `>`**. Equality does **not** qualify.

Signals are only definitively known **after day T closes**.

### 5.1 ETF Momentum

For ETF `X` on trading day `T`:

```text
20-day momentum =
(adjusted close at T / adjusted close at T-20) - 1
```

Momentum condition:

```text
ETF 20-day momentum > +5%
```

Exactly `+5.00%` does **not** qualify.

### 5.2 Market Regime

SPY 200-day simple moving average on day T uses the **200 adjusted closing-price observations ending on day T**:

```text
SPY_200DMA(T) =
mean(SPY adjusted closes from T-199 through T)
```

Positive market regime:

```text
SPY adjusted close at T > SPY_200DMA(T)
```

Equality does **not** qualify.

---

## 6. Observation Rule

Every ETF trading day on which the relevant arm’s conditions are satisfied counts as **one observation**.

Consecutive qualifying days remain **separate** observations.

Example: if XLK satisfies the combined signal Monday through Friday, those are **five** observations.

Experiment 001 does **not** introduce:

* cooldown periods
* episode grouping
* signal deduplication
* minimum spacing between observations

**Limitation (explicit):** consecutive observations and overlapping forward holding periods are **not** statistically independent. Observation count must **not** automatically be interpreted as independent-trial count.

Any future investigation of signal episodes, cooldown periods, or clustering must be a **separate experiment**.

---

## 7. Signal and Execution Timing

```text
Signal day = T
```

The signal is confirmed using closing information from day T.

| Concept | Rule |
| --- | --- |
| Earliest actionable entry | T+1 |
| Primary entry price | T+1 Open |

We explicitly do **not** assume entry at the T close. Overnight movement between T close and T+1 open is therefore naturally included in the result.

---

## 8. Forward Observation Windows

Standardized **observation horizons** (not optimized trading-exit rules):

```text
1, 3, 5, 10, 20 trading days
```

Exact convention:

```text
Signal:       T close
Entry:        T+1 open

1-day:        exit at T+1 close
3-day:        exit at T+3 close
5-day:        exit at T+5 close
10-day:       exit at T+10 close
20-day:       exit at T+20 close
```

Forward return:

```text
(exit close / T+1 open) - 1
```

A positive outcome at a horizon means that horizon’s return is `> 0`.

Do **not** interpret whichever horizon performs best as the automatically preferred trading strategy. Optimization of entry/exit/holds/stops belongs in follow-up experiments. Experiment 001 must remain unchanged after its results are seen.

---

## 9. A / B / C / D Comparison Groups

| Arm | Name | Condition on eligible day T |
| --- | --- | --- |
| **A** | Unconditional baseline | Eligible; no momentum or regime filter |
| **B** | Momentum alone | Eligible AND ETF 20-day momentum > +5% |
| **C** | Market regime alone | Eligible AND SPY close > SPY 200DMA |
| **D** | Momentum + market regime | Eligible AND momentum AND regime |

### Primary incremental comparison

**D versus B** is the most important incremental comparison.

Reason: Experiment 001 asks whether adding broader-market regime information improves an existing momentum condition. The regime signal must **earn its additional complexity**. A strong-looking D is not sufficient if B is approximately the same.

Also compare where useful:

```text
D vs A
D vs C
B vs A
C vs A
```

---

## 10. Baseline Alignment (Eligible Period)

For each ETF, A/B/C/D must use the **same eligible historical period**.

An ETF day T is eligible only when sufficient history exists to calculate:

1. the ETF’s 20-trading-day momentum; and
2. SPY’s 200-day moving average.

Do **not** allow unconditional baseline A to include earlier observations that were not eligible for the signal comparisons.

This keeps `A vs B vs C vs D` apples-to-apples.

Additionally, for a given forward horizon H, day T contributes to that horizon’s metrics only if the required exit close exists (see §12).

---

## 11. ETF Inception Dates

Use each ETF only from when reliable historical ETF data actually exists.

Do **not** fabricate earlier ETF history.  
Do **not** synthetically backfill newer ETFs for Experiment 001.

Different ETFs may have different eligible historical periods. This is intentional.

---

## 12. End-of-Series Handling

Evaluate each forward horizon independently.

Example: if an observation has only six subsequent trading days available:

```text
1-day   → INCLUDE
3-day   → INCLUDE
5-day   → INCLUDE
10-day  → EXCLUDE
20-day  → EXCLUDE
```

Do **not**:

* fill missing future prices
* extrapolate
* substitute zero
* drop valid shorter horizons merely because a longer horizon is unavailable

Observation counts may therefore legitimately differ across the five horizons.

---

## 13. Discovery / Validation Split

```text
80% discovery
20% validation
```

Chronological split based on each ETF’s **eligible** history. **Not** random.

```text
earliest eligible observations
        ↓
first 80%  → DISCOVERY
        ↓
final 20%  → VALIDATION
```

Because ETF histories differ, individual ETF discovery/validation cutoff dates may differ. Acceptable for Experiment 001.

### Validation must remain hidden

Workflow:

```text
Run discovery
      ↓
Record discovery results
      ↓
Evaluate against predefined evidence criteria
      ↓
Decide whether validation is warranted
      ↓
Only then reveal/run validation
```

Do not casually display discovery and validation together before discovery has been evaluated.

### No changes before validation (once formally locked)

After Experiment 001 is formally locked, do **not** modify thresholds, windows, arms, timing, universe, evidence criteria, split methodology, or calculations because discovery suggests another configuration might look better.

Any such change becomes a **new experiment**. Discovery may generate hypotheses; it may not rewrite Experiment 001.

---

## 14. Required Measurements

For each relevant `ETF × Group (A/B/C/D) × Forward Horizon`, report where applicable:

* observation count
* positive outcome rate
* negative outcome rate
* mean return
* median return
* average winner
* average loser
* median winner
* median loser
* bottom 10% outcome
* bottom 5% outcome
* worst historical outcome
* Maximum Adverse Excursion (MAE)
* Maximum Favorable Excursion (MFE)

Also produce the pooled 13-non-SPY ETF result. SPY remains separate.

Do not reduce the experiment to a single win-rate or average-return number.

### MAE / MFE definition (resolved)

Entry price for excursion measurement:

```text
Entry = T+1 adjusted open
```

For a given holding horizon ending on exit day `T+H`:

```text
Holding-period lows  = adjusted lows from T+1 through T+H inclusive
Holding-period highs = adjusted highs from T+1 through T+H inclusive

MAE = (minimum adjusted low during holding period / T+1 open) - 1
MFE = (maximum adjusted high during holding period / T+1 open) - 1
```

MAE is typically ≤ 0; MFE is typically ≥ 0.

**Daily-bar limitation (explicit):** we do **not** attempt to infer the intraday ordering of the high and low from daily OHLC. Excursions are those observable from daily adjusted OHLC only.

---

## 15. Evidence Philosophy

Classification prioritizes:

```text
Capital Preservation → Probability → Return
```

Primary question:

> Does stacking the market-regime signal onto momentum meaningfully improve the probability and/or downside characteristics of subsequent outcomes?

**Not:** which condition made the most money?

Mean return is secondary. Median return, probability, downside distribution, robustness, and sample size must remain visible.

---

## 16. Predefined Evidence Framework

Primary incremental probability comparison: **D versus B** (positive-outcome rate).

### 16.1 Sample-size requirements

* **INTERESTING** — normally requires at least **500 pooled D observations** across the 13 non-SPY ETFs for the relevant analysis.
* **STRONG CANDIDATE** — prefer at least **1,000 pooled D observations**.

Very small samples must never receive strong labels merely because percentages look impressive. Observation counts must always be shown beside probability statistics.

Pooled observations are correlated and overlapping; they are **not** equivalent to the same number of independent trials.

### 16.2 Cross-ETF robustness (D vs B directional improvement)

* **INTERESTING:** at least **7 of 13** non-SPY ETFs show the same directional improvement of D versus B.
* **STRONG CANDIDATE:** target at least **9 of 13** non-SPY ETFs with the same directional D-versus-B improvement.

The pooled result must not receive a strong classification if the advantage is obviously concentrated in only a small number of ETFs.

### 16.3 Cross-horizon robustness (D vs B)

* **INTERESTING:** meaningful D-versus-B improvement across at least **3 of 5** forward horizons.
* **STRONG CANDIDATE:** across at least **4 of 5** forward horizons.

Do not pick the historically best-looking horizon after seeing results and ignore the others.

### 16.4 Practical probability improvement (D vs B)

| Rating | Guidance |
| --- | --- |
| **INCONCLUSIVE** | Insufficient sample for a meaningful judgment; **or** mixed results; **or** no consistent D-versus-B improvement |
| **WEAK** | D shows some improvement over B, but improvement is small, inconsistent across horizons/assets, or accompanied by concerning downside |
| **INTERESTING** | Normally `positive_rate(D) ≥ positive_rate(B) + 3 percentage points`, plus adequate sample, cross-ETF robustness, cross-horizon robustness, and no clear multi-metric material downside deterioration vs B |
| **STRONG CANDIDATE** | Normally `positive_rate(D) ≥ positive_rate(B) + 5 percentage points`, plus strong sample support, broader cross-ETF and cross-horizon consistency, and improved or broadly comparable downside vs B (win-rate lift cannot override worse tails) |

These are practical effect-size criteria, not guarantees of economic significance.

### 16.5 Downside is a multi-metric gate (resolved)

A higher win rate alone is **not** sufficient.

For **D versus B**, examine the downside distribution using:

* average loser
* median loser
* bottom 10%
* bottom 5%
* worst outcome
* MAE

**Material deterioration** (predefined qualitative rule — **no** single arbitrary numeric cutoff such as “MAE may not worsen by more than X%”):

> D shows a **clear and broadly consistent worsening** of the downside distribution versus B across **multiple** downside measures and/or horizons.

This remains partly judgment-based, but the judgment rule is fixed **before** seeing results.

**STRONG CANDIDATE requirement:** D should show **improved or broadly comparable** downside to B. A ~+5 percentage-point win-rate improvement must **not** override obviously worse tail losses. If probability improves but downside becomes meaningfully worse under the multi-metric rule above, downgrade the evidence classification accordingly.

---

## 17. Statistical Honesty (no formal inference in 001)

Do not treat pooled observation count as equivalent to independent sample size.

The experiment contains consecutive signals, overlapping holding periods, correlated ETFs, and shared market regimes. Naïve tests assuming fully independent observations may be misleading.

**Experiment 001 does not include a formal statistical inferential test** (including naïve p-values). Results are **descriptive empirical evidence**: A/B/C/D × ETFs × horizons × probability × magnitude × downside × MAE/MFE × discovery/validation, with overlapping/correlated observations explicitly acknowledged.

If 001 produces something genuinely interesting, a **later experiment** may ask whether the apparent edge remains robust when dependence and clustering are explicitly accounted for. That methodology must be chosen carefully then — not bolted onto Experiment 001.

---

## 18. Pattern-Oriented Interpretation (Post-Results)

Interpretation may examine the **shape of the evidence**, including:

* Does D improve probability immediately and then fade?
* Is improvement stronger at short or long horizons?
* Does downside improve even when average return changes little?
* Is the effect consistent across ETFs or concentrated in sectors?
* Do MAE/MFE reveal recurring early downside or timing patterns?
* Does regime help across most horizons or only one?
* Is the outcome distribution more asymmetric under D?

These are interpretation questions. Answers must **not** retrospectively alter Experiment 001. Interesting patterns become future hypotheses / new experiments.

---

## 19. Future Research Note — Underlying Sector Histories

**Not part of Experiment 001 execution.**

The fact that an ETF did not exist before a certain date does not imply that its underlying sector, industry, commodity, or economic influence did not exist. Newer sector ETFs may have short histories even though their underlying sectors affected markets earlier. Underlying/spot/index data may provide longer histories than ETF proxies.

Future experiments may investigate historically appropriate sector/industry indices, spot markets, market indices, or explicitly documented historical proxies. Such data must be clearly identified and **must not** be silently substituted into Experiment 001.

Experiment 001 uses **actual available ETF histories only**. Do not synthesize longer ETF price histories by splicing index/spot series onto ETF prices.

---

## 20. Known Limitations

* ETF inception dates vary; some sector ETFs have substantially shorter histories.
* Current ETF selection may contain survivorship bias.
* Consecutive qualifying observations are correlated.
* Forward holding periods overlap.
* ETFs themselves are correlated.
* SPY participates in defining the regime and is therefore reported separately.
* Gross historical returns ≠ realizable net returns.
* Transaction costs, spreads, slippage, taxes, and market impact are not modeled.
* T+1 open is a standardized execution assumption and does not guarantee historical fill quality.
* Discovery/validation cutoff dates differ by ETF because histories differ.
* Uses ETF history rather than reconstructed pre-inception sector history.
* Observations are overlapping and cross-ETF correlated; Experiment 001 reports descriptive empirical evidence only — no formal dependence-aware statistical inference in this experiment.
* Downside “material deterioration” is a predefined multi-metric qualitative gate (no single numeric cutoff).
* MAE/MFE use daily adjusted highs/lows vs T+1 open; daily bars do not establish intraday path ordering.

---

## 21. Execution Gate

Methodology is **LOCKED** as of **2026-08-21**.

Implementation and discovery execution may proceed **only** according to this frozen specification.

1. Implement only what this specification states.
2. Run discovery first; keep validation hidden until discovery is assessed.
3. Save raw results under `results/` before interpretation narrative is finalized.
4. Do not change thresholds, windows, arms, timing, universe, evidence criteria, or calculations after seeing discovery results — that requires a new experiment ID.

**Result:** NOT YET RUN  
**Interpretation:** NOT YET AVAILABLE

---

## 22. Lineage

```text
Experiment 001 — Momentum + Market Regime
      │
      └── Methodology LOCKED 2026-08-21; execution pending
```

---

## 23. Pre-Lock Ambiguities — Resolved Before Lock (2026-08-21)

Resolved prior to lock and now part of the frozen methodology:

1. **Downside:** multi-metric qualitative gate for D vs B (average/median loser, bottom 10%/5%, worst outcome, MAE). Material deterioration = clear, broadly consistent worsening across multiple measures and/or horizons. No single arbitrary numeric cutoff. STRONG CANDIDATE requires improved or broadly comparable downside; win-rate lift alone cannot override worse tails.
2. **MAE/MFE:** from T+1 adjusted open to min adjusted low / max adjusted high from T+1 through each exit day inclusive; no intraday high/low ordering inferred from daily bars.
3. **Statistical inference:** none in Experiment 001; descriptive evidence only. Dependence-aware inference reserved for follow-up research.

**Status: `LOCKED` as of 2026-08-21.**
