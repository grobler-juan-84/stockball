# Experiment 001 — Discovery Report

**Partition:** discovery only (validation not revealed)
**Specification:** `experiments/EXPERIMENT_001.md` (LOCKED 2026-08-21)
**Generated (UTC):** 2026-08-21T07:40:15.849107+00:00

This report is the predefined locked discovery output. No thresholds were altered after seeing results.

---

## Evidence classification (pooled 13 non-SPY ETFs)

**Discovery rating: `WEAK`**

Primary incremental comparison: **D vs B** (positive-outcome rate), per §16.

| Check | Value |
| --- | --- |
| min pooled n_D across horizons | 8848 |
| horizons with D>B (directional) | 2/5 |
| horizons with lift ≥ 3pp | 0/5 |
| horizons with lift ≥ 5pp | 0/5 |
| non-SPY ETFs with D>B on ≥3/5 horizons | 6/13 |
| max D-observation share | 12.6% (XLE) |
| material multi-metric downside vs B | False (0/5 horizons majority-worse) |

### Reasons

- Some D>B improvement (directional horizons=2/5, ETF support=6/13) but below INTERESTING thresholds and/or robustness/downside/concentration constraints.
- lift>=3pp only on 0/5 horizons (need 3).
- Only 6/13 ETFs show D>B on >=3/5 horizons (need 7).

### Finding

On discovery data, D shows some improvement versus B, but the effect does not meet the locked INTERESTING thresholds for sample, effect size, cross-ETF/horizon robustness, and/or downside/concentration constraints.

### Limitation

- Observations overlap and ETFs are correlated; counts are not independent trials.
- No transaction costs or fill model beyond T+1 open.
- Discovery/validation cutoffs differ by ETF.
- Validation remains hidden; this rating is discovery-only.
- Downside gate is multi-metric and partly qualitative by lock design.

### Follow-up hypothesis

Any change to thresholds, horizons, universe, or dependence-aware inference is a **new experiment**, not a modification of 001. Validation reveal (if warranted) must use the frozen rules without parameter changes.

---

## D vs B by horizon — pooled non-SPY

| Horizon | n_B | n_D | Pos B | Pos D | Lift (pp) | Med ret B | Med ret D | Med MAE B | Med MAE D |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1d | 11675 | 8848 | 49.47% | 49.92% | 0.45 | 0.0000 | 0.0000 | -0.0065 | -0.0057 |
| 3d | 11675 | 8848 | 51.94% | 52.25% | 0.31 | 0.0010 | 0.0010 | -0.0118 | -0.0105 |
| 5d | 11675 | 8848 | 53.04% | 53.00% | -0.05 | 0.0017 | 0.0015 | -0.0156 | -0.0137 |
| 10d | 11675 | 8848 | 56.64% | 56.14% | -0.51 | 0.0052 | 0.0043 | -0.0215 | -0.0193 |
| 20d | 11675 | 8848 | 59.75% | 58.70% | -1.05 | 0.0103 | 0.0086 | -0.0302 | -0.0282 |

---

## D vs B by horizon — SPY (separate)

| Horizon | n_B | n_D | Pos B | Pos D | Lift (pp) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1d | 748 | 584 | 50.94% | 51.88% | 0.95 |
| 3d | 748 | 584 | 53.48% | 54.97% | 1.49 |
| 5d | 748 | 584 | 56.28% | 56.68% | 0.39 |
| 10d | 748 | 584 | 59.63% | 59.93% | 0.31 |
| 20d | 748 | 584 | 64.97% | 65.75% | 0.78 |

---

## Per-ETF D vs B directional support (≥3/5 horizons with D>B)

| Ticker | Horizons D>B | Supports INTERESTING rule |
| --- | ---: | --- |
| QQQ | 4/5 | yes |
| IWM | 2/5 | no |
| XLB | 1/5 | no |
| XLC | 0/5 | no |
| XLE | 3/5 | yes |
| XLF | 1/5 | no |
| XLI | 1/5 | no |
| XLK | 3/5 | yes |
| XLP | 5/5 | yes |
| XLRE | 2/5 | no |
| XLU | 4/5 | yes |
| XLV | 4/5 | yes |
| XLY | 2/5 | no |

---

## Full metrics

Complete A/B/C/D × horizon metrics for each ETF and pooled non-SPY are in `discovery_metrics.csv` (observation count, positive/negative rates, mean/median return, winner/loser stats, bottom 10%/5%, worst, median/mean MAE & MFE).

SPY is excluded from the pooled 13-ETF bucket.

