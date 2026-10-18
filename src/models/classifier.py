"""Well performance classification and anomaly detection."""

import json
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_FEATURES = Path("data/features")
MODELS_DIR = Path("models")


def label_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Label wells as high/medium/low based on cum oil."""
    df = df.copy()
    for dataset in df["dataset"].unique():
        mask = df["dataset"] == dataset
        subset = df.loc[mask, "cum_qoil"]
        q33 = subset.quantile(0.33)
        q66 = subset.quantile(0.66)
        df.loc[mask & (subset <= q33), "perf_class"] = "low"
        df.loc[
            mask & (subset > q33) & (subset <= q66),
            "perf_class",
        ] = "medium"
        df.loc[mask & (subset > q66), "perf_class"] = "high"
    return df


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Flag wells with extreme stability or GOR."""
    df = df.copy()
    for dataset in df["dataset"].unique():
        mask = df["dataset"] == dataset
        stab = df.loc[mask, "stability_index"]
        gor = df.loc[mask, "gor"]
        stab_thresh = stab.mean() + 2 * stab.std()
        gor_thresh = gor.mean() + 2 * gor.std()
        df.loc[mask, "anomaly_flag"] = (stab > stab_thresh) | (gor > gor_thresh)
    df["anomaly_flag"] = df["anomaly_flag"].astype(bool)
    return df


FEATURE_COLS = [
    "avg_qoil",
    "avg_qgas",
    "avg_qwat",
    "avg_qliq",
    "avg_pbh",
    "avg_pwh",
    "avg_chk",
    "gor",
    "water_cut",
    "stability_index",
    "decline_rate",
    "choked_fraction",
]


def train_classifier():
    """Train well performance classifier."""
    print("Loading features...")
    df = pd.read_parquet(DATA_FEATURES / "wells_features.parquet")
    df = label_performance(df)
    df = detect_anomalies(df)

    le = LabelEncoder()
    df["perf_label"] = le.fit_transform(df["perf_class"])

    X = df[FEATURE_COLS].fillna(0)
    y = df["perf_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Random Forest...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(
        y_test,
        y_pred,
        target_names=le.classes_,
        output_dict=True,
    )

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Feature importance
    imp = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(
        ascending=False
    )
    print("\n=== Feature Importance ===")
    print(imp.round(4).to_string())

    # Anomaly stats
    n_anom = df["anomaly_flag"].sum()
    print(f"\n=== Anomalies: {n_anom}/{len(df)} wells ===")
    print(df.groupby("dataset")["anomaly_flag"].sum().to_string())

    # Save
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    import pickle

    with open(MODELS_DIR / "classifier.pkl", "wb") as f:
        pickle.dump(model, f)
    with open(MODELS_DIR / "label_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    metrics = {
        "accuracy": report["accuracy"],
        "f1_macro": report["macro avg"]["f1-score"],
        "classes": le.classes_.tolist(),
    }
    with open(MODELS_DIR / "classifier_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # Save enriched features
    df.to_parquet(DATA_FEATURES / "wells_features_labeled.parquet")
    print(f"\nModel saved to {MODELS_DIR}/")
    print(f"Labeled features -> {DATA_FEATURES}/")


if __name__ == "__main__":
    train_classifier()
