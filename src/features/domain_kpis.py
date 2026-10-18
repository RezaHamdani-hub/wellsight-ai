"""Compute domain KPIs per well."""

from pathlib import Path

import pandas as pd

DATA_RAW = Path("data/raw")
DATA_FEATURES = Path("data/features")

DATASETS = {
    "sol-1": "manywells-sol-1.parquet",
    "nsol-1": "manywells-nsol-1.parquet",
    "nscl-1": "manywells-nscl-1.parquet",
}


def compute_well_features(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Aggregate per-well features and domain KPIs."""
    g = df.groupby("ID")

    f = pd.DataFrame()
    f["well_id"] = g["ID"].first().values
    f["dataset"] = dataset_name
    f["n_rows"] = g.size().values

    for col in ["QOIL", "QGAS", "QWAT", "QLIQ", "QTOT"]:
        f[f"avg_{col.lower()}"] = g[col].mean().values

    for col in ["QOIL", "QGAS", "QWAT"]:
        f[f"cum_{col.lower()}"] = g[col].sum().values

    f["avg_pbh"] = g["PBH"].mean().values
    f["avg_pwh"] = g["PWH"].mean().values
    f["avg_chk"] = g["CHK"].mean().values

    oil = g["QOIL"].mean().values
    gas = g["QGAS"].mean().values
    wat = g["QWAT"].mean().values

    f["gor"] = gas / oil.clip(min=1e-6)
    f["water_cut"] = wat / (wat + oil).clip(min=1e-6)

    oil_std = g["QOIL"].std().values
    f["stability_index"] = oil_std / oil.clip(min=1e-6)

    if "WEEKS" in df.columns:
        declines = []
        for _, wdf in g:
            ws = wdf.sort_values("WEEKS")
            h1 = ws["QOIL"].iloc[: len(ws) // 2].mean()
            h2 = ws["QOIL"].iloc[len(ws) // 2 :].mean()
            declines.append((h1 - h2) / h1 if h1 > 1e-6 else 0.0)
        f["decline_rate"] = declines
    else:
        f["decline_rate"] = 0.0

    f["dominant_frbh"] = g["FRBH"].agg(lambda x: x.mode().iloc[0]).values
    f["dominant_frwh"] = g["FRWH"].agg(lambda x: x.mode().iloc[0]).values
    f["choked_fraction"] = g["CHOKED"].mean().values

    return f


if __name__ == "__main__":
    DATA_FEATURES.mkdir(parents=True, exist_ok=True)

    all_features = []
    for name, filename in DATASETS.items():
        print(f"Processing {name}...")
        df = pd.read_parquet(DATA_RAW / filename)
        features = compute_well_features(df, name)
        all_features.append(features)
        print(f"  -> {len(features)} wells")

    combined = pd.concat(all_features, ignore_index=True)
    out = DATA_FEATURES / "wells_features.parquet"
    combined.to_parquet(out)
    print(f"\n[DONE] {len(combined)} wells -> {out}")
    print(combined.describe().round(2).to_string())
