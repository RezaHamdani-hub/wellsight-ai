"""Control strategy comparison: sol vs nsol vs nscl."""

import json
from pathlib import Path

import pandas as pd
from scipy import stats

DATA_FEATURES = Path("data/features")
MODELS_DIR = Path("models")


def run_optimization_analysis():
    """Compare open-loop vs closed-loop control."""
    print("Loading features...")
    df = pd.read_parquet(DATA_FEATURES / "wells_features_labeled.parquet")

    sol = df[df["dataset"] == "sol-1"]
    nsol = df[df["dataset"] == "nsol-1"]
    nscl = df[df["dataset"] == "nscl-1"]

    # --- ANOVA on key metrics ---
    metrics = [
        "avg_qoil",
        "avg_qgas",
        "water_cut",
        "stability_index",
        "gor",
    ]

    print("\n=== ANOVA Results ===")
    anova_results = {}
    for m in metrics:
        f_stat, p_val = stats.f_oneway(sol[m], nsol[m], nscl[m])
        sig = (
            "***"
            if p_val < 0.001
            else ("**" if p_val < 0.01 else ("*" if p_val < 0.05 else "ns"))
        )
        print(f"{m:20s}: F={f_stat:10.2f}, p={p_val:.2e} {sig}")
        anova_results[m] = {
            "f_statistic": round(f_stat, 2),
            "p_value": float(p_val),
            "significant": p_val < 0.05,
        }

    # --- Dataset comparison ---
    print("\n=== Mean Comparison ===")
    compare_cols = [
        "avg_qoil",
        "avg_qgas",
        "water_cut",
        "stability_index",
    ]
    comparison = df.groupby("dataset")[compare_cols].mean().round(2)
    print(comparison.to_string())

    # --- Closed-loop benefit ---
    print("\n=== Closed-Loop Benefit (nscl vs nsol) ===")
    for col in compare_cols:
        nsol_mean = nsol[col].mean()
        nscl_mean = nscl[col].mean()
        if nsol_mean > 1e-6:
            delta_pct = (nscl_mean - nsol_mean) / nsol_mean * 100
        else:
            delta_pct = 0
        direction = (
            "better"
            if (
                (col == "stability_index" and delta_pct < 0)
                or (col != "stability_index" and delta_pct > 0)
            )
            else "worse"
        )
        print(f"  {col}: {delta_pct:+.1f}% ({direction})")

    # --- Performance class distribution ---
    print("\n=== Performance Class Distribution ===")
    dist = pd.crosstab(
        df["dataset"],
        df["perf_class"],
        normalize="index",
    )
    print((dist * 100).round(1).to_string())

    # --- Save results ---
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "anova": anova_results,
        "means": comparison.to_dict(),
        "closed_loop_benefit": {
            col: round(
                (nscl[col].mean() - nsol[col].mean())
                / max(nsol[col].mean(), 1e-6)
                * 100,
                2,
            )
            for col in compare_cols
        },
    }
    with open(MODELS_DIR / "optimization_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {MODELS_DIR}/")


if __name__ == "__main__":
    run_optimization_analysis()
