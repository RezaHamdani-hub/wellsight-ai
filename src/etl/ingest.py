"""Download ManyWells datasets from HuggingFace."""

from pathlib import Path

from datasets import load_dataset

DATA_RAW = Path("data/raw")

SUBSETS = [
    "manywells-sol-1",
    "manywells-nsol-1",
    "manywells-nscl-1",
]


def download_datasets(output_dir: Path = DATA_RAW) -> None:
    """Download all three ManyWells subsets and save as parquet."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for name in SUBSETS:
        out_file = output_dir / f"{name}.parquet"
        if out_file.exists():
            print(f"[SKIP] {name} already exists at {out_file}")
            continue

        print(f"[DOWNLOAD] {name}...")
        ds = load_dataset("solution-seeker-as/manywells", name=name)
        df = ds["train"].to_pandas()
        df.to_parquet(out_file)
        print(f"  -> {out_file} ({len(df):,} rows)")

    print("[DONE] All datasets downloaded.")


if __name__ == "__main__":
    download_datasets()
