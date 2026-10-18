"""WellSight AI — Operational Dashboard."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_FEATURES = Path("data/features")
MODELS_DIR = Path("models")

st.set_page_config(page_title="WellSight AI", page_icon="oil_drum", layout="wide")


@st.cache_data
def load_data():
    return pd.read_parquet(DATA_FEATURES / "wells_features_labeled.parquet")


@st.cache_data
def load_metrics():
    metrics = {}
    for name in ["classifier_metrics", "forecaster_metrics", "optimization_results"]:
        p = MODELS_DIR / f"{name}.json"
        if p.exists():
            with open(p) as f:
                metrics[name] = json.load(f)
    return metrics


df = load_data()
metrics = load_metrics()

st.sidebar.title("WellSight AI")
st.sidebar.markdown("AI-powered production intelligence")
page = st.sidebar.radio("Navigate", ["Fleet Overview", "Well Health", "Optimization"])
dataset_filter = st.sidebar.multiselect(
    "Dataset", df["dataset"].unique().tolist(), default=df["dataset"].unique().tolist()
)
filtered = df[df["dataset"].isin(dataset_filter)]

if page == "Fleet Overview":
    st.title("Fleet Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Wells", f"{len(filtered):,}")
    c2.metric("Avg Oil Rate", f"{filtered['avg_qoil'].mean():.1f} Sm3/h")
    c3.metric("Fleet Water Cut", f"{filtered['water_cut'].mean():.1%}")
    c4.metric("Fleet GOR", f"{filtered['gor'].median():.0f} Sm3/Sm3")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cumulative Oil vs Decline Rate")
        fig = px.scatter(
            filtered,
            x="cum_qoil",
            y="decline_rate",
            color="perf_class",
            symbol="dataset",
            opacity=0.6,
            color_discrete_map={
                "high": "#2ecc71",
                "medium": "#f39c12",
                "low": "#e74c3c",
            },
            labels={"cum_qoil": "Cumulative Oil (Sm3)", "decline_rate": "Decline Rate"},
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Production Distribution")
        fig = px.box(
            filtered,
            x="dataset",
            y="avg_qoil",
            color="perf_class",
            color_discrete_map={
                "high": "#2ecc71",
                "medium": "#f39c12",
                "low": "#e74c3c",
            },
            labels={"avg_qoil": "Avg Oil Rate (Sm3/h)", "dataset": "Dataset"},
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Well Ranking")
    rank_cols = [
        "well_id",
        "dataset",
        "avg_qoil",
        "water_cut",
        "gor",
        "stability_index",
        "perf_class",
        "anomaly_flag",
    ]
    rank_df = (
        filtered[rank_cols]
        .sort_values("avg_qoil", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(rank_df, height=400, use_container_width=True)

elif page == "Well Health":
    st.title("Well Health & Anomaly Detection")
    anomalies = filtered[filtered["anomaly_flag"]]
    normal = filtered[~filtered["anomaly_flag"]]

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Flagged Wells",
        f"{len(anomalies)}",
        delta=f"{len(anomalies)/max(len(filtered),1)*100:.1f}%",
        delta_color="inverse",
    )
    c2.metric("Normal Wells", f"{len(normal)}")
    acc = metrics.get("classifier_metrics", {}).get("accuracy", 0)
    c3.metric("Classifier Accuracy", f"{acc:.1%}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Anomaly Distribution")
        anom_by_ds = filtered.groupby("dataset")["anomaly_flag"].sum().reset_index()
        anom_by_ds.columns = ["dataset", "anomalies"]
        fig = px.bar(
            anom_by_ds,
            x="dataset",
            y="anomalies",
            color="dataset",
            labels={"anomalies": "Anomalous Wells"},
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Stability vs GOR")
        fig = px.scatter(
            filtered,
            x="stability_index",
            y="gor",
            color="anomaly_flag",
            color_discrete_map={True: "#e74c3c", False: "#3498db"},
            opacity=0.5,
            labels={"stability_index": "Stability Index", "gor": "GOR"},
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Anomalous Wells Detail")
    if len(anomalies) > 0:
        detail_cols = [
            "well_id",
            "dataset",
            "avg_qoil",
            "gor",
            "stability_index",
            "water_cut",
            "perf_class",
        ]
        st.dataframe(
            anomalies[detail_cols]
            .sort_values("stability_index", ascending=False)
            .reset_index(drop=True),
            height=400,
            use_container_width=True,
        )

elif page == "Optimization":
    st.title("Control Strategy Optimization")
    opt = metrics.get("optimization_results", {})
    benefit = opt.get("closed_loop_benefit", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("Oil Rate Gain (CL vs OL)", f"+{benefit.get('avg_qoil', 0):.1f}%")
    c2.metric("Stability Improvement", f"{benefit.get('stability_index', 0):.1f}%")
    r2 = metrics.get("forecaster_metrics", {}).get("r2", 0)
    c3.metric("Forecaster R2", f"{r2:.4f}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Oil Production by Strategy")
        fig = px.violin(
            filtered,
            x="dataset",
            y="avg_qoil",
            color="dataset",
            box=True,
            labels={"avg_qoil": "Avg Oil Rate (Sm3/h)", "dataset": "Strategy"},
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Stability Comparison")
        fig = px.violin(
            filtered,
            x="dataset",
            y="stability_index",
            color="dataset",
            box=True,
            labels={"stability_index": "Stability Index", "dataset": "Strategy"},
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("ANOVA Results")
    anova = opt.get("anova", {})
    if anova:
        anova_df = pd.DataFrame(anova).T
        anova_df.index.name = "Metric"
        st.dataframe(anova_df, use_container_width=True)
