"""Generate Experiment 001 discovery metrics and evidence classification.

Authority: experiments/EXPERIMENT_001.md (LOCKED 2026-08-21).
Implements the predefined discovery report only — no validation reveal,
no threshold changes, no ad hoc exploration.

Reads:  experiments/001/discovery/outcomes/
Writes: experiments/001/discovery/results/discovery_metrics.csv
        experiments/001/discovery/results/discovery_report.md

Usage:
  .venv\\Scripts\\python.exe scripts\\report_experiment_001_discovery.py
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
OUTCOMES_DIR = ROOT / "experiments" / "001" / "discovery" / "outcomes"
RESULTS_DIR = ROOT / "experiments" / "001" / "discovery" / "results"
VALIDATION_DIR = ROOT / "experiments" / "001" / "validation"

HORIZONS = (1, 3, 5, 10, 20)
GROUPS = ("A", "B", "C", "D")


def load_universe() -> list[str]:
    data = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    return [str(t).strip().upper() for t in data["equity_etfs"]]


def assert_validation_untouched() -> None:
    if (VALIDATION_DIR / "outcomes").exists() or (VALIDATION_DIR / "results").exists():
        sys.exit("Validation outcomes/results present — abort to preserve blind holdout")


def group_metrics(df: pd.DataFrame, group: str, horizon: int) -> dict:
    mask = df[f"group_{group}"].astype(bool) & df[f"horizon_{horizon}d_available"].astype(bool)
    sub = df.loc[mask]
    ret = sub[f"return_{horizon}d"].astype(float)
    mae = sub[f"mae_{horizon}d"].astype(float)
    mfe = sub[f"mfe_{horizon}d"].astype(float)
    n = int(len(ret))
    if n == 0:
        return {
            "group": group,
            "horizon_days": horizon,
            "n": 0,
            "positive_rate": np.nan,
            "negative_rate": np.nan,
            "mean_return": np.nan,
            "median_return": np.nan,
            "avg_winner": np.nan,
            "avg_loser": np.nan,
            "median_winner": np.nan,
            "median_loser": np.nan,
            "bottom_10pct": np.nan,
            "bottom_5pct": np.nan,
            "worst_return": np.nan,
            "median_mae": np.nan,
            "median_mfe": np.nan,
            "mean_mae": np.nan,
            "mean_mfe": np.nan,
        }
    winners = ret[ret > 0]
    losers = ret[ret <= 0]
    return {
        "group": group,
        "horizon_days": horizon,
        "n": n,
        "positive_rate": float((ret > 0).mean()),
        "negative_rate": float((ret <= 0).mean()),
        "mean_return": float(ret.mean()),
        "median_return": float(ret.median()),
        "avg_winner": float(winners.mean()) if len(winners) else np.nan,
        "avg_loser": float(losers.mean()) if len(losers) else np.nan,
        "median_winner": float(winners.median()) if len(winners) else np.nan,
        "median_loser": float(losers.median()) if len(losers) else np.nan,
        "bottom_10pct": float(ret.quantile(0.10)),
        "bottom_5pct": float(ret.quantile(0.05)),
        "worst_return": float(ret.min()),
        "median_mae": float(mae.median()),
        "median_mfe": float(mfe.median()),
        "mean_mae": float(mae.mean()),
        "mean_mfe": float(mfe.mean()),
    }


def metrics_for_frame(df: pd.DataFrame, label: str, bucket: str) -> list[dict]:
    rows = []
    for g in GROUPS:
        for h in HORIZONS:
            m = group_metrics(df, g, h)
            m["universe_label"] = label
            m["bucket"] = bucket
            rows.append(m)
    return rows


def d_vs_b_rows(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (label, bucket), sub in metrics.groupby(["universe_label", "bucket"], sort=False):
        for h in HORIZONS:
            b = sub[(sub["group"] == "B") & (sub["horizon_days"] == h)].iloc[0]
            d = sub[(sub["group"] == "D") & (sub["horizon_days"] == h)].iloc[0]
            lift = d["positive_rate"] - b["positive_rate"]
            rows.append(
                {
                    "universe_label": label,
                    "bucket": bucket,
                    "horizon_days": h,
                    "n_B": int(b["n"]),
                    "n_D": int(d["n"]),
                    "positive_rate_B": b["positive_rate"],
                    "positive_rate_D": d["positive_rate"],
                    "lift_pp": lift * 100.0 if pd.notna(lift) else np.nan,
                    "mean_return_B": b["mean_return"],
                    "mean_return_D": d["mean_return"],
                    "median_return_B": b["median_return"],
                    "median_return_D": d["median_return"],
                    "avg_loser_B": b["avg_loser"],
                    "avg_loser_D": d["avg_loser"],
                    "median_loser_B": b["median_loser"],
                    "median_loser_D": d["median_loser"],
                    "bottom_10pct_B": b["bottom_10pct"],
                    "bottom_10pct_D": d["bottom_10pct"],
                    "bottom_5pct_B": b["bottom_5pct"],
                    "bottom_5pct_D": d["bottom_5pct"],
                    "worst_B": b["worst_return"],
                    "worst_D": d["worst_return"],
                    "median_mae_B": b["median_mae"],
                    "median_mae_D": d["median_mae"],
                    "directional_D_gt_B": bool(
                        pd.notna(lift) and d["positive_rate"] > b["positive_rate"]
                    ),
                    "lift_ge_3pp": bool(pd.notna(lift) and lift >= 0.03),
                    "lift_ge_5pp": bool(pd.notna(lift) and lift >= 0.05),
                }
            )
    return pd.DataFrame(rows)


def downside_worse(d_row: pd.Series, b_row: pd.Series) -> dict[str, bool]:
    """True if D is worse than B on that metric (more adverse)."""
    return {
        "avg_loser": bool(pd.notna(d_row["avg_loser"]) and pd.notna(b_row["avg_loser"]) and d_row["avg_loser"] < b_row["avg_loser"]),
        "median_loser": bool(pd.notna(d_row["median_loser"]) and pd.notna(b_row["median_loser"]) and d_row["median_loser"] < b_row["median_loser"]),
        "bottom_10pct": bool(pd.notna(d_row["bottom_10pct"]) and pd.notna(b_row["bottom_10pct"]) and d_row["bottom_10pct"] < b_row["bottom_10pct"]),
        "bottom_5pct": bool(pd.notna(d_row["bottom_5pct"]) and pd.notna(b_row["bottom_5pct"]) and d_row["bottom_5pct"] < b_row["bottom_5pct"]),
        "worst": bool(pd.notna(d_row["worst_return"]) and pd.notna(b_row["worst_return"]) and d_row["worst_return"] < b_row["worst_return"]),
        "median_mae": bool(pd.notna(d_row["median_mae"]) and pd.notna(b_row["median_mae"]) and d_row["median_mae"] < b_row["median_mae"]),
    }


def classify_pooled_discovery(metrics: pd.DataFrame, non_spy_tickers: list[str]) -> dict:
    """Apply locked §16 criteria to pooled non-SPY discovery (descriptive)."""
    pooled = metrics[metrics["universe_label"] == "POOLED_NON_SPY"]
    dvb = d_vs_b_rows(pooled)

    n_d_by_h = {int(r.horizon_days): int(r.n_D) for r in dvb.itertuples()}
    min_n_d = min(n_d_by_h.values()) if n_d_by_h else 0
    max_n_d = max(n_d_by_h.values()) if n_d_by_h else 0

    horizons_dir = int(dvb["directional_D_gt_B"].sum())
    horizons_3pp = int(dvb["lift_ge_3pp"].sum())
    horizons_5pp = int(dvb["lift_ge_5pp"].sum())

    # Per-ETF support: >=3/5 horizons with D>B
    etf_support = 0
    etf_d_counts = []
    for t in non_spy_tickers:
        t_metrics = metrics[metrics["universe_label"] == t]
        t_dvb = d_vs_b_rows(t_metrics)
        if int(t_dvb["directional_D_gt_B"].sum()) >= 3:
            etf_support += 1
        # D observation share proxy: mean n_D across horizons
        etf_d_counts.append((t, float(t_dvb["n_D"].mean())))

    total_d = sum(c for _, c in etf_d_counts) or 1.0
    max_share = max(c / total_d for _, c in etf_d_counts)
    max_share_ticker = max(etf_d_counts, key=lambda x: x[1])[0]
    concentrated = max_share > 0.40

    # Downside multi-metric gate across horizons
    worse_horizons = 0
    for h in HORIZONS:
        b = pooled[(pooled["group"] == "B") & (pooled["horizon_days"] == h)].iloc[0]
        d = pooled[(pooled["group"] == "D") & (pooled["horizon_days"] == h)].iloc[0]
        worse = downside_worse(d, b)
        if sum(worse.values()) >= 4:  # majority of 6 metrics worse
            worse_horizons += 1
    material_downside = worse_horizons >= 3  # broadly consistent across horizons

    reasons: list[str] = []
    rating = "INCONCLUSIVE"

    if min_n_d < 500:
        reasons.append(f"Pooled D sample below INTERESTING minimum (min n_D={min_n_d}, need >=500).")
        if horizons_dir == 0:
            rating = "INCONCLUSIVE"
        else:
            rating = "WEAK" if horizons_dir >= 1 else "INCONCLUSIVE"
            if horizons_dir >= 1:
                reasons.append("Some D>B directional lift exists but sample is small.")
    else:
        if horizons_dir == 0:
            rating = "INCONCLUSIVE"
            reasons.append("No consistent D-versus-B positive-rate improvement across horizons.")
        elif (
            min_n_d >= 1000
            and horizons_5pp >= 4
            and etf_support >= 9
            and not material_downside
            and not concentrated
        ):
            rating = "STRONG CANDIDATE"
            reasons.append(
                f"min n_D={min_n_d}; lift>=5pp on {horizons_5pp}/5 horizons; "
                f"ETF support {etf_support}/13; downside not materially worse."
            )
        elif (
            horizons_3pp >= 3
            and etf_support >= 7
            and not material_downside
            and not concentrated
        ):
            rating = "INTERESTING"
            reasons.append(
                f"min n_D={min_n_d}; lift>=3pp on {horizons_3pp}/5 horizons; "
                f"ETF support {etf_support}/13; downside gate passed (qualitative)."
            )
        elif horizons_dir >= 1:
            rating = "WEAK"
            reasons.append(
                f"Some D>B improvement (directional horizons={horizons_dir}/5, "
                f"ETF support={etf_support}/13) but below INTERESTING thresholds "
                f"and/or robustness/downside/concentration constraints."
            )
            if material_downside:
                reasons.append("Multi-metric downside appears materially worse for D vs B.")
            if concentrated:
                reasons.append(
                    f"D observations concentrated (max share {max_share:.0%} in {max_share_ticker})."
                )
            if horizons_3pp < 3:
                reasons.append(f"lift>=3pp only on {horizons_3pp}/5 horizons (need 3).")
            if etf_support < 7:
                reasons.append(f"Only {etf_support}/13 ETFs show D>B on >=3/5 horizons (need 7).")
        else:
            rating = "INCONCLUSIVE"
            reasons.append("Mixed/insufficient D-versus-B improvement.")

    # Cap strong/interesting if concentration or downside fails
    if rating == "STRONG CANDIDATE" and (material_downside or concentrated):
        rating = "WEAK"
        reasons.append("Capped below STRONG CANDIDATE due to downside/concentration.")
    if rating == "INTERESTING" and (material_downside or concentrated):
        rating = "WEAK"
        reasons.append("Capped below INTERESTING due to downside/concentration.")

    return {
        "rating": rating,
        "min_n_D": min_n_d,
        "max_n_D": max_n_d,
        "horizons_directional": horizons_dir,
        "horizons_lift_ge_3pp": horizons_3pp,
        "horizons_lift_ge_5pp": horizons_5pp,
        "etf_support_ge_3_of_5_horizons": etf_support,
        "max_d_share": max_share,
        "max_d_share_ticker": max_share_ticker,
        "material_downside_vs_B": material_downside,
        "downside_worse_horizon_count": worse_horizons,
        "reasons": reasons,
        "dvb_table": dvb,
    }


def fmt_pct(x: float | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    return f"{100.0 * x:.{digits}f}%"


def fmt_num(x: float | None, digits: int = 4) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    return f"{x:.{digits}f}"


def write_report(
    metrics: pd.DataFrame,
    assessment: dict,
    non_spy: list[str],
    path: Path,
) -> None:
    dvb_pooled = assessment["dvb_table"]
    lines: list[str] = []
    lines.append("# Experiment 001 — Discovery Report")
    lines.append("")
    lines.append("**Partition:** discovery only (validation not revealed)")
    lines.append("**Specification:** `experiments/EXPERIMENT_001.md` (LOCKED 2026-08-21)")
    lines.append(f"**Generated (UTC):** {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("This report is the predefined locked discovery output. No thresholds were altered after seeing results.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Evidence classification (pooled 13 non-SPY ETFs)")
    lines.append("")
    lines.append(f"**Discovery rating: `{assessment['rating']}`**")
    lines.append("")
    lines.append("Primary incremental comparison: **D vs B** (positive-outcome rate), per §16.")
    lines.append("")
    lines.append("| Check | Value |")
    lines.append("| --- | --- |")
    lines.append(f"| min pooled n_D across horizons | {assessment['min_n_D']} |")
    lines.append(f"| horizons with D>B (directional) | {assessment['horizons_directional']}/5 |")
    lines.append(f"| horizons with lift ≥ 3pp | {assessment['horizons_lift_ge_3pp']}/5 |")
    lines.append(f"| horizons with lift ≥ 5pp | {assessment['horizons_lift_ge_5pp']}/5 |")
    lines.append(
        f"| non-SPY ETFs with D>B on ≥3/5 horizons | {assessment['etf_support_ge_3_of_5_horizons']}/13 |"
    )
    lines.append(
        f"| max D-observation share | {assessment['max_d_share']:.1%} ({assessment['max_d_share_ticker']}) |"
    )
    lines.append(
        f"| material multi-metric downside vs B | {assessment['material_downside_vs_B']} "
        f"({assessment['downside_worse_horizon_count']}/5 horizons majority-worse) |"
    )
    lines.append("")
    lines.append("### Reasons")
    lines.append("")
    for r in assessment["reasons"]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("### Finding")
    lines.append("")
    if assessment["rating"] in {"INTERESTING", "STRONG CANDIDATE"}:
        lines.append(
            "On discovery data, stacking the SPY>200DMA regime onto ETF 20-day momentum >5% "
            "(group D) shows a predefined-threshold improvement over momentum alone (group B) "
            f"sufficient for a discovery rating of **{assessment['rating']}**, subject to the "
            "limitations below and pending any later validation reveal."
        )
    elif assessment["rating"] == "WEAK":
        lines.append(
            "On discovery data, D shows some improvement versus B, but the effect does not meet "
            "the locked INTERESTING thresholds for sample, effect size, cross-ETF/horizon "
            "robustness, and/or downside/concentration constraints."
        )
    else:
        lines.append(
            "On discovery data, the evidence for incremental value of D over B is insufficient "
            "or inconsistent under the locked criteria (INCONCLUSIVE)."
        )
    lines.append("")
    lines.append("### Limitation")
    lines.append("")
    lines.append(
        "- Observations overlap and ETFs are correlated; counts are not independent trials.\n"
        "- No transaction costs or fill model beyond T+1 open.\n"
        "- Discovery/validation cutoffs differ by ETF.\n"
        "- Validation remains hidden; this rating is discovery-only.\n"
        "- Downside gate is multi-metric and partly qualitative by lock design."
    )
    lines.append("")
    lines.append("### Follow-up hypothesis")
    lines.append("")
    lines.append(
        "Any change to thresholds, horizons, universe, or dependence-aware inference is a "
        "**new experiment**, not a modification of 001. Validation reveal (if warranted) must "
        "use the frozen rules without parameter changes."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## D vs B by horizon — pooled non-SPY")
    lines.append("")
    lines.append(
        "| Horizon | n_B | n_D | Pos B | Pos D | Lift (pp) | Med ret B | Med ret D | Med MAE B | Med MAE D |"
    )
    lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in dvb_pooled.sort_values("horizon_days").itertuples():
        lines.append(
            f"| {r.horizon_days}d | {r.n_B} | {r.n_D} | {fmt_pct(r.positive_rate_B)} | "
            f"{fmt_pct(r.positive_rate_D)} | {r.lift_pp:.2f} | {fmt_num(r.median_return_B)} | "
            f"{fmt_num(r.median_return_D)} | {fmt_num(r.median_mae_B)} | {fmt_num(r.median_mae_D)} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## D vs B by horizon — SPY (separate)")
    lines.append("")
    spy_dvb = d_vs_b_rows(metrics[metrics["universe_label"] == "SPY"])
    lines.append(
        "| Horizon | n_B | n_D | Pos B | Pos D | Lift (pp) |"
    )
    lines.append("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in spy_dvb.sort_values("horizon_days").itertuples():
        lines.append(
            f"| {r.horizon_days}d | {r.n_B} | {r.n_D} | {fmt_pct(r.positive_rate_B)} | "
            f"{fmt_pct(r.positive_rate_D)} | {r.lift_pp:.2f} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Per-ETF D vs B directional support (≥3/5 horizons with D>B)")
    lines.append("")
    lines.append("| Ticker | Horizons D>B | Supports INTERESTING rule |")
    lines.append("| --- | ---: | --- |")
    for t in non_spy:
        t_dvb = d_vs_b_rows(metrics[metrics["universe_label"] == t])
        n_dir = int(t_dvb["directional_D_gt_B"].sum())
        lines.append(f"| {t} | {n_dir}/5 | {'yes' if n_dir >= 3 else 'no'} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Full metrics")
    lines.append("")
    lines.append(
        "Complete A/B/C/D × horizon metrics for each ETF and pooled non-SPY are in "
        "`discovery_metrics.csv` (observation count, positive/negative rates, mean/median "
        "return, winner/loser stats, bottom 10%/5%, worst, median/mean MAE & MFE)."
    )
    lines.append("")
    lines.append("SPY is excluded from the pooled 13-ETF bucket.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not SPEC_PATH.exists():
        sys.exit(f"Missing specification: {SPEC_PATH}")
    assert_validation_untouched()

    tickers = load_universe()
    non_spy = [t for t in tickers if t != "SPY"]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    frames: list[pd.DataFrame] = []
    metric_rows: list[dict] = []

    for t in tickers:
        path = OUTCOMES_DIR / f"{t.lower()}_discovery_outcomes.csv"
        if not path.exists():
            sys.exit(f"Missing outcomes (run Step 29 first): {path}")
        df = pd.read_csv(path)
        frames.append(df)
        bucket = "spy" if t == "SPY" else "non_spy_etf"
        metric_rows.extend(metrics_for_frame(df, t, bucket))

    pooled = pd.concat([f for f, t in zip(frames, tickers) if t != "SPY"], ignore_index=True)
    metric_rows.extend(metrics_for_frame(pooled, "POOLED_NON_SPY", "pooled_non_spy"))

    metrics = pd.DataFrame(metric_rows)
    metrics_csv = RESULTS_DIR / "discovery_metrics.csv"
    metrics.to_csv(metrics_csv, index=False)

    assessment = classify_pooled_discovery(metrics, non_spy)
    report_path = RESULTS_DIR / "discovery_report.md"
    write_report(metrics, assessment, non_spy, report_path)

    # Save assessment JSON (rating only + checklist; includes lifts already in report)
    assess_out = {
        "experiment": "001",
        "partition": "discovery",
        "specification": "experiments/EXPERIMENT_001.md",
        "rating": assessment["rating"],
        "min_n_D": assessment["min_n_D"],
        "horizons_directional": assessment["horizons_directional"],
        "horizons_lift_ge_3pp": assessment["horizons_lift_ge_3pp"],
        "horizons_lift_ge_5pp": assessment["horizons_lift_ge_5pp"],
        "etf_support_ge_3_of_5_horizons": assessment["etf_support_ge_3_of_5_horizons"],
        "max_d_share": assessment["max_d_share"],
        "max_d_share_ticker": assessment["max_d_share_ticker"],
        "material_downside_vs_B": assessment["material_downside_vs_B"],
        "reasons": assessment["reasons"],
        "validation_revealed": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (RESULTS_DIR / "discovery_evidence_assessment.json").write_text(
        json.dumps(assess_out, indent=2) + "\n", encoding="utf-8"
    )

    print(f"metrics: {metrics_csv.relative_to(ROOT)}")
    print(f"report:  {report_path.relative_to(ROOT)}")
    print(f"pooled non-SPY discovery rating: {assessment['rating']}")
    print("Validation not revealed.")


if __name__ == "__main__":
    main()
