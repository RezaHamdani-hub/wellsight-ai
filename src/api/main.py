"""WellSight AI — FastAPI endpoints."""

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODELS_DIR = Path("models")
DATA_FEATURES = Path("data/features")

app = FastAPI(
    title="WellSight AI",
    description="AI-powered well production intelligence API",
    version="0.1.0",
)


def load_pickle(name):
    p = MODELS_DIR / name
    if not p.exists():
        return None
    with open(p, "rb") as f:
        return pickle.load(f)


classifier = load_pickle("classifier.pkl")
label_encoder = load_pickle("label_encoder.pkl")
forecaster = load_pickle("forecaster.pkl")


class PredictRequest(BaseModel):
    CHK: float
    PBH: float
    PWH: float
    PDC: float
    TBH: float
    TWH: float
    WGL: float = 0.0
    FGAS: float
    FOIL: float
    FWAT: float
    WEEKS: float = 0.0


class ClassifyRequest(BaseModel):
    avg_qoil: float
    avg_qgas: float
    avg_qwat: float
    avg_qliq: float
    avg_pbh: float
    avg_pwh: float
    avg_chk: float
    gor: float
    water_cut: float
    stability_index: float
    decline_rate: float = 0.0
    choked_fraction: float = 0.5


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "models": {
            "classifier": classifier is not None,
            "forecaster": forecaster is not None,
        },
    }


@app.post("/predict")
def predict_production(req: PredictRequest):
    if forecaster is None:
        raise HTTPException(503, "Forecaster model not loaded")
    features = np.array(
        [
            [
                req.CHK,
                req.PBH,
                req.PWH,
                req.PDC,
                req.TBH,
                req.TWH,
                req.WGL,
                req.FGAS,
                req.FOIL,
                req.FWAT,
                req.WEEKS,
            ]
        ]
    )
    pred = forecaster.predict(features)[0]
    return {"predicted_qoil": round(float(pred), 2), "unit": "Sm3/h"}


@app.post("/classify")
def classify_well(req: ClassifyRequest):
    if classifier is None or label_encoder is None:
        raise HTTPException(503, "Classifier model not loaded")
    features = np.array(
        [
            [
                req.avg_qoil,
                req.avg_qgas,
                req.avg_qwat,
                req.avg_qliq,
                req.avg_pbh,
                req.avg_pwh,
                req.avg_chk,
                req.gor,
                req.water_cut,
                req.stability_index,
                req.decline_rate,
                req.choked_fraction,
            ]
        ]
    )
    pred = classifier.predict(features)[0]
    label = label_encoder.inverse_transform([pred])[0]
    proba = classifier.predict_proba(features)[0]
    return {
        "performance_class": label,
        "probabilities": {
            c: round(float(p), 3) for c, p in zip(label_encoder.classes_, proba)
        },
    }


@app.get("/optimize")
def get_optimization():
    p = MODELS_DIR / "optimization_results.json"
    if not p.exists():
        raise HTTPException(503, "Optimization results not found")
    with open(p) as f:
        return json.load(f)


@app.get("/fleet")
def get_fleet_summary():
    p = DATA_FEATURES / "wells_features_labeled.parquet"
    if not p.exists():
        raise HTTPException(503, "Feature data not found")
    df = pd.read_parquet(p)
    return {
        "total_wells": len(df),
        "datasets": df["dataset"].unique().tolist(),
        "avg_oil_rate": round(float(df["avg_qoil"].mean()), 2),
        "avg_water_cut": round(float(df["water_cut"].mean()), 4),
        "anomaly_count": int(df["anomaly_flag"].sum()),
        "performance_distribution": (df["perf_class"].value_counts().to_dict()),
    }
