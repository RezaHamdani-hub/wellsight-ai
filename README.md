# WellSight AI

AI-powered well production intelligence platform — from raw simulation data to operational dashboard with AI advisory agent.

## Overview

WellSight AI is an end-to-end ML platform for monitoring, classifying, and optimizing multiphase oil well production. Built on the [ManyWells](https://huggingface.co/datasets/solution-seeker-as/manywells) simulation datasets (3M+ rows across 6,000 wells), it demonstrates the intersection of upstream O&G domain expertise and modern AI/MLOps engineering.

### Key Results

| Model | Metric | Result |
|---|---|---|
| Well Classifier | Accuracy | **97.8%** |
| Production Forecaster | R² | **0.9197** |
| Control Strategy (ANOVA) | All metrics | **p < 0.001** |
| Anomaly Detection | Wells flagged | **369 / 6,000 (6.2%)** |
| Closed-loop vs Open-loop | Oil rate gain | **+15.8%** |

### Key Capabilities

- **Production forecasting** — predict oil/gas/water rates from well parameters (RandomForest, R²=0.92)
- **Well classification & anomaly detection** — identify high/low performers and flag production anomalies (98% accuracy)
- **Control strategy optimization** — quantify the benefit of closed-loop vs open-loop control (ANOVA, all significant)
- **Production Advisor Agent** — natural language queries for domain-aware operational recommendations
- **Operational Dashboard** — 3-page Streamlit app: Fleet Overview, Well Health, Optimization

## Tech Stack

| Layer | Technology |
|---|---|
| Data | Pandas, PyArrow, DuckDB, HuggingFace Datasets |
| ML | Scikit-learn, RandomForest, SHAP, SciPy |
| MLOps | Docker, GitHub Actions CI/CD |
| API | FastAPI (5 endpoints) |
| Dashboard | Streamlit, Plotly |
| Agent | Rule-based advisor with model-informed recommendations |

## Quick Start

```bash
# Clone and setup
git clone https://github.com/<your-username>/wellsight-ai.git
cd wellsight-ai
make setup
source .venv/bin/activate

# Download data (~565 MB from HuggingFace)
python -m src.etl.ingest

# Build features
python -m src.features.domain_kpis

# Train models
python -m src.models.classifier
python -m src.models.forecaster
python -m src.models.optimizer

# Run dashboard
streamlit run src/dashboard/app.py

# Run API
uvicorn src.api.main:app --reload --port 8000

# Run tests
python -m pytest -v
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Service health check |
| `/fleet` | GET | Fleet-level summary statistics |
| `/predict` | POST | Predict oil rate from well parameters |
| `/classify` | POST | Classify well performance (high/medium/low) |
| `/optimize` | GET | Control strategy comparison results |

## Project Structure

wellsight-ai/
├── src/
│ ├── etl/ # Data ingestion from HuggingFace
│ ├── features/ # Domain KPI computation (GOR, Water Cut, etc.)
│ ├── models/ # ML models (classifier, forecaster, optimizer)
│ ├── api/ # FastAPI serving (5 endpoints)
│ ├── dashboard/ # Streamlit operational dashboard (3 pages)
│ └── agent/ # Production advisor agent
├── mlops/
│ └── docker/ # Dockerfiles for API, dashboard, MLflow
├── notebooks/ # EDA scripts
├── tests/ # API tests
├── data/ # Raw, processed, and feature data (gitignored)
├── models/ # Serialized model artifacts (gitignored)
└── docs/ # PRD, architecture, domain glossary

## Dataset

[ManyWells](https://huggingface.co/datasets/solution-seeker-as/manywells) by Solution Seeker AS — simulations of multiphase flow in 6,000 wells across three operating conditions:

| Dataset | Boundary | Control | Wells | Rows |
|---|---|---|---|---|
| sol-1 | Stationary | Open-loop | 2,000 | 1,000,000 |
| nsol-1 | Non-stationary | Open-loop | 2,000 | 1,000,000 |
| nscl-1 | Non-stationary | Closed-loop | 2,000 | 1,000,000 |

## Domain KPIs

| KPI | Description |
|---|---|
| GOR | Gas-Oil Ratio — reservoir drive mechanism indicator |
| Water Cut | Water fraction — reservoir maturity indicator |
| Decline Rate | Production decline over time |
| Stability Index | Production variability (std/mean) |
| Cumulative Production | Total oil/gas/water extracted |

## Documentation

- [Product Requirements Document](docs/PRD.md)
- [Architecture Overview](docs/architecture.md)
- [Domain Glossary](docs/domain-glossary.md)

## Author

**Reza Fadli Hamdani** — Data & AI Engineer

## License

CC BY-NC 4.0 (dataset), MIT (code)

## Citation

If you use the ManyWells dataset, please cite:
@article{Grimstad2026,
title = {ManyWells: Simulation of multiphase flow in thousands of wells},
author = {Bjarne Grimstad and Erlend Lundby and Henrik Andersson},
journal = {Geoenergy Science and Engineering},
volume = {257},
pages = {214226},
year = {2026},
}
