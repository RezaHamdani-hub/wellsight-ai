# WellSight AI

End-to-end ML platform for monitoring and optimizing multiphase oil well production. Takes raw simulation data, builds predictive models, and serves results through an operational dashboard with a built-in advisory agent.

Built on [ManyWells](https://huggingface.co/datasets/solution-seeker-as/manywells) (3M+ rows, 6,000 wells across three control strategies).

## Results

| Model | Metric | Result |
|---|---|---|
| Well Classifier | Accuracy | 97.8% |
| Production Forecaster | R² | 0.9197 |
| Control Strategy (ANOVA) | All metrics | p < 0.001 |
| Anomaly Detection | Wells flagged | 369 / 6,000 (6.2%) |
| Closed-loop vs Open-loop | Oil rate gain | +15.8% |

## What it does

- Forecasts oil/gas/water production rates per well (RandomForest, R²=0.92)
- Classifies wells into performance tiers and flags anomalies
- Compares open-loop vs closed-loop control strategies with statistical testing
- Provides an advisory agent that answers natural language questions about well performance
- Serves everything through a 3-page Streamlit dashboard and a FastAPI backend

## Tech Stack

| Layer | Tools |
|---|---|
| Data | Pandas, PyArrow, HuggingFace Datasets |
| ML | Scikit-learn, SciPy |
| API | FastAPI (5 endpoints) |
| Dashboard | Streamlit, Plotly |
| Infra | Docker, GitHub Actions |

## Getting Started

```bash
git clone https://github.com/RezaHamdani-hub/wellsight-ai.git
cd wellsight-ai
make setup
source .venv/bin/activate

# Download data (~565 MB)
python -m src.etl.ingest

# Build features + train models
python -m src.features.domain_kpis
python -m src.models.classifier
python -m src.models.forecaster
python -m src.models.optimizer

# Run
streamlit run src/dashboard/app.py     # Dashboard on :8501
uvicorn src.api.main:app --port 8000   # API on :8000
python -m pytest -v                    # Tests
```

## API

| Endpoint | Method | What it returns |
|---|---|---|
| `/health` | GET | Service status |
| `/fleet` | GET | Fleet-wide production stats |
| `/predict` | POST | Predicted oil rate for given well parameters |
| `/classify` | POST | Performance class (high/medium/low) with probabilities |
| `/optimize` | GET | ANOVA results comparing control strategies |

## Project Layout
src/
etl/ Data download from HuggingFace
features/ Domain KPIs (GOR, water cut, decline rate, stability)
models/ Classifier, forecaster, optimizer
api/ FastAPI endpoints
dashboard/ Streamlit app (3 pages)
agent/ Production advisor
mlops/docker/ Dockerfiles
tests/ API tests
docs/ PRD, architecture notes, O&G glossary

## Dataset

[ManyWells](https://huggingface.co/datasets/solution-seeker-as/manywells) by Solution Seeker AS. Three simulation scenarios:

- **sol-1** (1M rows) - stationary conditions, open-loop control
- **nsol-1** (1M rows) - non-stationary, open-loop
- **nscl-1** (1M rows) - non-stationary, closed-loop (adaptive choke control)

All data is synthetic (simulation output). No personal or proprietary information.

## Docs

- [Product Requirements](docs/PRD.md)
- [Architecture](docs/architecture.md)
- [O&G Domain Glossary](docs/domain-glossary.md)

## License

MIT (code), CC BY-NC 4.0 (dataset)
