"""Production forecasting — predict QOIL from well parameters."""

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

DATA_RAW = Path("data/raw")
MODELS_DIR = Path("models")

FEATURE_COLS = [
    "CHK",
    "PBH",
    "PWH",
    "PDC",
    "TBH",
    "TWH",
    "WGL",
    "FGAS",
    "FOIL",
    "FWAT",
]


def train_forecaster():
    """Train RandomForest to predict QOIL."""
    print("Loading datasets...")
    frames = []
    for name in ["manywells-nsol-1", "manywells-nscl-1"]:
        df = pd.read_parquet(DATA_RAW / f"{name}.parquet")
        df["dataset"] = name.replace("manywells-", "")
        frames.append(df)

    sol = pd.read_parquet(DATA_RAW / "manywells-sol-1.parquet")
    sol["dataset"] = "sol-1"
    sol["WEEKS"] = 0.0
    frames.append(sol)

    data = pd.concat(frames, ignore_index=True)
    print(f"Total rows: {len(data):,}")

    feature_cols = FEATURE_COLS + ["WEEKS"]
    x = data[feature_cols].fillna(0)
    y = data["QOIL"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    print("Training RandomForest regressor...")
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = model.score(x_test, y_test)

    print("\n=== Forecaster Results ===")
    print(f"MAE:  {mae:.2f} Sm3/h")
    print(f"RMSE: {rmse:.2f} Sm3/h")
    print(f"R2:   {r2:.4f}")

    imp = pd.Series(
        model.feature_importances_,
        index=feature_cols,
    ).sort_values(ascending=False)
    print("\n=== Feature Importance ===")
    print(imp.round(4).to_string())

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODELS_DIR / "forecaster.pkl", "wb") as fp:
        pickle.dump(model, fp)

    metrics = {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "features": feature_cols,
    }
    with open(MODELS_DIR / "forecaster_metrics.json", "w") as fp:
        json.dump(metrics, fp, indent=2)

    print(f"\nModel saved to {MODELS_DIR}/")


if __name__ == "__main__":
    train_forecaster()
