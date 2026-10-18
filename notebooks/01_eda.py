"""EDA script for ManyWells datasets. Run with: python notebooks/01_eda.py"""

from pathlib import Path

import pandas as pd

DATA_RAW = Path("data/raw")

# --- Load datasets ---
print("Loading datasets...")
sol = pd.read_parquet(DATA_RAW / "manywells-sol-1.parquet")
nsol = pd.read_parquet(DATA_RAW / "manywells-nsol-1.parquet")
nscl = pd.read_parquet(DATA_RAW / "manywells-nscl-1.parquet")

sol["dataset"] = "sol-1"
nsol["dataset"] = "nsol-1"
nscl["dataset"] = "nscl-1"

print(f"sol-1:  {sol.shape}")
print(f"nsol-1: {nsol.shape}")
print(f"nscl-1: {nscl.shape}")

# --- Basic info ---
print("\n=== COLUMNS ===")
print(sol.columns.tolist())

print("\n=== DTYPES ===")
print(sol.dtypes)

print("\n=== NULL COUNTS (sol-1) ===")
print(sol.isnull().sum())

print("\n=== DESCRIBE (sol-1) ===")
print(sol.describe().round(2).to_string())

# --- Wells per dataset ---
print("\n=== UNIQUE WELLS ===")
for name, df in [("sol-1", sol), ("nsol-1", nsol), ("nscl-1", nscl)]:
    n_wells = df["ID"].nunique()
    rows_per = len(df) // n_wells
    print(f"{name}: {n_wells} wells, {len(df)} rows, {rows_per} rows/well")

# --- WEEKS column check ---
print("\n=== WEEKS COLUMN ===")
print(f"sol-1 has WEEKS:  {'WEEKS' in sol.columns}")
print(f"nsol-1 has WEEKS: {'WEEKS' in nsol.columns}")
print(f"nscl-1 has WEEKS: {'WEEKS' in nscl.columns}")

if "WEEKS" in nsol.columns:
    print(f"nsol-1 WEEKS range: {nsol['WEEKS'].min()} - {nsol['WEEKS'].max()}")
if "WEEKS" in nscl.columns:
    print(f"nscl-1 WEEKS range: {nscl['WEEKS'].min()} - {nscl['WEEKS'].max()}")

# --- Key production columns stats ---
print("\n=== PRODUCTION STATS PER DATASET ===")
prod_cols = ["QOIL", "QGAS", "QWAT", "QLIQ"]
all_data = pd.concat([sol, nsol, nscl])
print(all_data.groupby("dataset")[prod_cols].mean().round(2).to_string())

# --- Flow regime distribution ---
print("\n=== FLOW REGIME (FRBH) ===")
print(all_data.groupby("dataset")["FRBH"].value_counts().to_string())

print("\n=== FLOW REGIME (FRWH) ===")
print(all_data.groupby("dataset")["FRWH"].value_counts().to_string())

# --- Choke stats ---
print("\n=== CHOKE (CHK) STATS ===")
print(all_data.groupby("dataset")["CHK"].describe().round(3).to_string())

print("\n[EDA DONE]")
