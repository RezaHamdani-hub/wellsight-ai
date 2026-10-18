# Architecture Overview

## System Layers
HuggingFace (ManyWells datasets — 3M rows)
|
v
Layer 1: ETL (src/etl/ingest.py)
- Download 3 datasets via HuggingFace datasets library
- Store as Parquet in data/raw/
|
v
Layer 2: Feature Engineering (src/features/domain_kpis.py)
- Aggregate per-well: 6,000 wells x 18 features
- Domain KPIs: GOR, Water Cut, Decline Rate, Stability Index
- Output: data/features/wells_features.parquet
|
v
Layer 3: ML Models (src/models/)
- classifier.py: RandomForest — well performance (high/med/low) + anomaly detection
- forecaster.py: RandomForest — predict QOIL from well parameters
- optimizer.py: ANOVA — compare sol-1 vs nsol-1 vs nscl-1 control strategies
- Output: models/.pkl, models/_metrics.json
|
v
Layer 4: Serving (src/api/main.py)
- FastAPI with 5 endpoints: /health, /fleet, /predict, /classify, /optimize
- Loads serialized models at startup
- Dockerized (mlops/docker/Dockerfile.api)
|
v
Layer 5: Dashboard (src/dashboard/app.py)
- Streamlit, 3 pages: Fleet Overview, Well Health, Optimization
- Interactive Plotly charts
- Reads from feature store + model outputs
|
v
Layer 6: Advisor Agent (src/agent/advisor.py)
- Rule-based + model-informed recommendations
- Natural language query routing
- Integrated into dashboard Optimization page

## Data Flow
data/raw/*.parquet (3 x 1M rows)
|
v [domain_kpis.py]
data/features/wells_features.parquet (6,000 rows x 18 cols)
|
v [classifier.py]
data/features/wells_features_labeled.parquet (+ perf_class, anomaly_flag)
|
v [FastAPI + Streamlit + Agent]
User-facing outputs

## Infrastructure

| Component | Technology | Port |
|---|---|---|
| API | FastAPI + Uvicorn | 8000 |
| Dashboard | Streamlit | 8501 |
| MLflow | MLflow Server | 5000 |
| CI | GitHub Actions | — |
| Containers | Docker Compose | — |

## Key Design Decisions

1. **Parquet over CSV** — columnar format, 3-5x compression, fast reads
2. **RandomForest over XGBoost** — no OpenMP dependency on ARM Mac, comparable performance
3. **Rule-based agent over LLM** — zero API cost, deterministic, demo-friendly
4. **Streamlit over Dash** — faster prototyping, Python-native, good for data apps
5. **Per-dataset labeling** — performance classes computed within each dataset to avoid bias
