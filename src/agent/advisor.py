"""Production Advisor Agent — domain-aware recommendations."""

import json
from pathlib import Path

import pandas as pd

DATA_FEATURES = Path("data/features")
MODELS_DIR = Path("models")


def load_context():
    """Load all model outputs for agent context."""
    ctx = {}

    feat_path = DATA_FEATURES / "wells_features_labeled.parquet"
    if feat_path.exists():
        ctx["wells"] = pd.read_parquet(feat_path)

    for name in ["classifier_metrics", "forecaster_metrics", "optimization_results"]:
        p = MODELS_DIR / f"{name}.json"
        if p.exists():
            with open(p) as f:
                ctx[name] = json.load(f)

    return ctx


def get_well_summary(ctx: dict, well_id: int, dataset: str) -> str:
    """Get summary for a specific well."""
    df = ctx.get("wells")
    if df is None:
        return "No well data available."

    match = df[(df["well_id"] == well_id) & (df["dataset"] == dataset)]
    if match.empty:
        return f"Well {well_id} not found in {dataset}."

    w = match.iloc[0]
    lines = [
        f"## Well {well_id} ({dataset})",
        f"- Performance: {w['perf_class'].upper()}",
        f"- Avg oil rate: {w['avg_qoil']:.1f} Sm3/h",
        f"- Water cut: {w['water_cut']:.1%}",
        f"- GOR: {w['gor']:.0f} Sm3/Sm3",
        f"- Stability index: {w['stability_index']:.2f}",
        f"- Anomaly: {'YES' if w['anomaly_flag'] else 'No'}",
    ]

    if w["decline_rate"] != 0:
        lines.append(f"- Decline rate: {w['decline_rate']:.2f}")

    lines.append("")
    lines.append("### Recommendations:")

    if w["anomaly_flag"]:
        lines.append("- ALERT: Anomalous behavior detected. Inspect well conditions.")
    if w["water_cut"] > 0.6:
        lines.append("- High water cut — consider water shutoff or recompletion.")
    if w["stability_index"] > 0.8:
        lines.append("- Unstable production — evaluate choke optimization.")
    if w["perf_class"] == "low":
        lines.append("- Low performer — candidate for workover or stimulation.")
    if w["gor"] > 5000:
        lines.append("- High GOR — monitor for gas coning, consider gas lift review.")
    if w["perf_class"] == "high" and not w["anomaly_flag"]:
        lines.append("- Strong performer — maintain current operating parameters.")

    return "\n".join(lines)


def get_fleet_summary(ctx: dict) -> str:
    """Fleet-level summary with actionable insights."""
    df = ctx.get("wells")
    if df is None:
        return "No data available."

    opt = ctx.get("optimization_results", {})
    clf = ctx.get("classifier_metrics", {})
    frc = ctx.get("forecaster_metrics", {})

    lines = [
        "## Fleet Summary",
        f"- Total wells: {len(df)}",
        f"- Avg oil rate: {df['avg_qoil'].mean():.1f} Sm3/h",
        f"- Fleet water cut: {df['water_cut'].mean():.1%}",
        f"- Anomalous wells: {df['anomaly_flag'].sum()} ({df['anomaly_flag'].mean():.1%})",
        "",
        "### Performance Distribution",
    ]

    for ds in df["dataset"].unique():
        subset = df[df["dataset"] == ds]
        high = (subset["perf_class"] == "high").sum()
        low = (subset["perf_class"] == "low").sum()
        anom = subset["anomaly_flag"].sum()
        lines.append(f"- {ds}: {high} high, {low} low, {anom} anomalies")

    benefit = opt.get("closed_loop_benefit", {})
    if benefit:
        lines.extend(
            [
                "",
                "### Control Strategy Insight",
                f"- Closed-loop vs open-loop oil gain: +{benefit.get('avg_qoil', 0):.1f}%",
                f"- Stability improvement: {benefit.get('stability_index', 0):.1f}%",
                "- Recommendation: Prioritize closed-loop control for new completions.",
            ]
        )

    if clf:
        lines.extend(
            [
                "",
                "### Model Performance",
                f"- Classifier accuracy: {clf.get('accuracy', 0):.1%}",
                f"- Forecaster R2: {frc.get('r2', 0):.4f}, MAE: {frc.get('mae', 0)} Sm3/h",
            ]
        )

    return "\n".join(lines)


def get_top_concerns(ctx: dict, n: int = 5) -> str:
    """List top wells needing attention."""
    df = ctx.get("wells")
    if df is None:
        return "No data available."

    anomalies = df[df["anomaly_flag"]].nlargest(n, "stability_index")

    lines = [f"## Top {n} Wells Requiring Attention", ""]
    for _, w in anomalies.iterrows():
        reasons = []
        if w["stability_index"] > 0.8:
            reasons.append("unstable")
        if w["water_cut"] > 0.6:
            reasons.append("high water cut")
        if w["gor"] > 5000:
            reasons.append("high GOR")
        reason_str = ", ".join(reasons) if reasons else "anomalous pattern"
        lines.append(
            f"- Well {int(w['well_id'])} ({w['dataset']}): "
            f"QOIL={w['avg_qoil']:.1f}, WC={w['water_cut']:.1%}, "
            f"Stability={w['stability_index']:.2f} [{reason_str}]"
        )

    return "\n".join(lines)


def ask_advisor(query: str) -> str:
    """Route a natural language query to the right analysis."""
    ctx = load_context()
    q = query.lower().strip()

    # Well-specific query
    if "well" in q and any(c.isdigit() for c in q):
        import re

        nums = re.findall(r"\d+", q)
        well_id = int(nums[0]) if nums else 0
        dataset = "sol-1"
        for ds in ["nscl-1", "nsol-1", "sol-1"]:
            if ds in q:
                dataset = ds
                break
        return get_well_summary(ctx, well_id, dataset)

    if any(w in q for w in ["fleet", "overview", "summary", "total"]):
        return get_fleet_summary(ctx)

    if any(w in q for w in ["concern", "attention", "worst", "problem", "alert"]):
        return get_top_concerns(ctx)

    if any(w in q for w in ["closed", "open", "control", "optimize", "strategy"]):
        opt = ctx.get("optimization_results", {})
        benefit = opt.get("closed_loop_benefit", {})
        return (
            "## Control Strategy Analysis\n"
            f"- Oil rate gain (closed vs open loop): +{benefit.get('avg_qoil', 0):.1f}%\n"
            f"- Stability improvement: {benefit.get('stability_index', 0):.1f}%\n"
            f"- Water cut change: {benefit.get('water_cut', 0):.1f}%\n"
            "\nRecommendation: Closed-loop control delivers higher oil "
            "recovery with better stability. Deploy on underperforming wells first."
        )

    return get_fleet_summary(ctx)


if __name__ == "__main__":
    print("=== Fleet Summary ===")
    print(ask_advisor("fleet summary"))
    print()
    print("=== Well Query ===")
    print(ask_advisor("how is well 42 in sol-1?"))
    print()
    print("=== Top Concerns ===")
    print(ask_advisor("which wells need attention?"))
    print()
    print("=== Strategy ===")
    print(ask_advisor("should we use closed loop control?"))
