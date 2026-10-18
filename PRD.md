Noted — dashboard design akan di-refine saat POC. Sekarang saya tulis PRD lengkapnya.

---

# WellSight AI — Product Requirements Document

**Version:** 1.0
**Author:** Reza Fadli Hamdani
**Date:** 2026-10-18
**Status:** Draft — preparation phase

---

## 1. Project overview

**Project name:** WellSight AI
**Tagline:** AI-powered well production intelligence platform
**Repository:** `wellsight-ai`

**Objective:** Membangun end-to-end AI platform untuk monitoring, klasifikasi, dan optimisasi produksi sumur minyak multifasa — dari raw simulation data hingga operational dashboard dengan AI agent advisory. Project ini berfungsi sebagai portfolio yang mendemonstrasikan hybrid capability di persimpangan domain O&G dan modern AI/MLOps.

**Target audience:**
- Recruiter dan hiring manager di perusahaan energi (TotalEnergies, SLB, Halliburton, Capgemini Energy, Technip)
- Technical interviewer yang mengevaluasi kemampuan data engineering + ML
- Hiring manager yang mencari profil "digital transformation" di industri

**Success criteria:**
- Pipeline end-to-end berjalan dari data ingestion hingga agent response
- Dashboard menampilkan insight actionable dengan KPI domain O&G
- MLOps stack deployable via `docker-compose up`
- Slide deck executive-ready untuk presentasi portfolio
- Codebase bersih, terdokumentasi, dan public di GitHub

---

## 2. Problem statement

**Gap di portfolio:**
Pengalaman O&G upstream sudah ada (BP Berau — KPI dashboards, Pertamina EP — waterflood/EOR monitoring), tapi belum ada project visible yang menghubungkan domain knowledge ini dengan AI/ML modern dan production-grade engineering.

**Market context:**
- 62% perusahaan O&G sudah deploy AI (Gartner 2026)
- Demand untuk digital oilfield specialists naik 25-30%
- Hybrid profile (domain O&G + AI engineering) mendapat salary premium signifikan
- Gartner prediksi 70% perusahaan O&G akan adopt agentic AI dalam 2 tahun
- Capgemini dan BP sudah deploy Production Optimization Digital Twin secara operasional

**Kesempatan:**
Project ini membuktikan bahwa pengalaman BP Berau dan Pertamina EP bukan hanya historical — tapi bisa ditranslasikan ke solusi AI modern yang dicari pasar saat ini.

---

## 3. Scope

**In scope:**
- Data ingestion dan ETL dari 3 dataset ManyWells (HuggingFace)
- Feature engineering dengan domain KPI O&G
- 3 ML models: production forecasting, well classification/anomaly detection, control strategy optimization
- MLOps infrastructure: Docker, MLflow, Airflow, GitHub Actions CI/CD
- Operational dashboard Streamlit (1 halaman, 3 sheets)
- Production Advisor Agent (LLM-powered, query via natural language)
- FastAPI model serving endpoint
- Executive slide deck
- Technical documentation

**Out of scope:**
- Real-time streaming data / live well connection
- Cloud deployment (AWS/GCP production) — lokal Docker compose saja
- Mobile application
- Reservoir simulation engine (kita pakai hasil simulasi, bukan simulatornya)
- Multi-user authentication di dashboard

---

## 4. Dataset specification

**Source:** Solution Seeker AS via HuggingFace dan GitHub

### 4.1 Three datasets

| Dataset | Boundary conditions | Control | Karakteristik |
|---|---|---|---|
| `manywells-sol-1` | Stationary | Open-loop (no feedback) | Baseline — kondisi stabil, tanpa respons otomatis |
| `manywells-nsol-1` | Non-stationary | Open-loop (no feedback) | Kondisi berubah, tapi tanpa adaptasi kontrol |
| `manywells-nscl-1` | Non-stationary | Closed-loop (with feedback) | Kondisi berubah dengan kontrol adaptif — paling realistis |

**Per dataset:**
- 2000 vertical wells
- 500 data points per well (1 data point = 1 simulasi)
- Total per dataset: 1.000.000 rows
- Total keseluruhan: 3.006.000 rows

**Identifiers:** Kolom "ID" unik hanya dalam satu dataset. Well 1 di sol-1 ≠ well 1 di nsol-1.

**Configuration files:** `[dataset-name]_config.zip` — dictionary dengan well ID sebagai key, berisi parameter simulasi per sumur.

### 4.2 Domain KPI yang diturunkan

| KPI | Formula / Definisi | Kegunaan bisnis |
|---|---|---|
| **GOR** (Gas-Oil Ratio) | Gas rate / Oil rate | Indikator reservoir drive mechanism |
| **Water Cut** | Water rate / (Water rate + Oil rate) | Indikator maturitas reservoir, kebutuhan water handling |
| **Decline Rate** | Rate of change produksi over time | Prediksi umur sumur, kebutuhan workover |
| **Cumulative Production** | Sum produksi over time per fase | Total value extracted |
| **Production Stability Index** | Std deviation of production rate / mean | Variabilitas — closed-loop harusnya lebih stabil |

### 4.3 Data privacy

Dataset tidak mengandung informasi pribadi, sensitif, atau private. Seluruh data berasal dari simulasi.

---

## 5. System architecture

### 5.1 Layer overview

```
Layer 1: Data source (HuggingFace + GitHub configs)
    ↓
Layer 2: ETL & feature engineering (Python, Airflow, Great Expectations)
    ↓
Layer 3: ML models (Forecasting, Classification, Optimization)
    ↓
Layer 4: MLOps (Docker, MLflow, Airflow, GitHub Actions, FastAPI)
    ↓
Layer 5: Operational dashboard (Streamlit — 3 sheets)
    ↓
Layer 6: Production Advisor Agent (LLM + model outputs)
```

### 5.2 Tech stack per layer

| Layer | Technology | Justifikasi |
|---|---|---|
| Data ingestion | `datasets` (HuggingFace lib), `requests` | Native HF integration |
| Storage | Parquet (DuckDB untuk query) | Columnar, efisien untuk time series, kompatibel ARM M2 |
| ETL orchestration | Airflow (lightweight) | Industry standard, ada di CV |
| Data quality | Great Expectations | Automated validation, generates docs |
| ML training | Scikit-learn, XGBoost, Prophet/LSTM | Coverage dari classical ML hingga time series |
| Experiment tracking | MLflow | Industry standard, local-friendly |
| Model serving | FastAPI | Lightweight, async, Python-native |
| Containerization | Docker + Docker Compose | Sudah ada pengalaman (Waste Detection project) |
| CI/CD | GitHub Actions | Free tier, standard |
| Dashboard | Streamlit | Rapid prototyping, Python-native, good for data apps |
| AI Agent | LangChain + OpenAI/Anthropic API | Tool-calling agent, integrasi dengan model outputs |
| Visualization | Plotly | Interactive charts, O&G industry standard |

---

## 6. Feature requirements

### 6.1 Layer 2 — ETL & feature engineering

| Requirement | Acceptance criteria |
|---|---|
| Download 3 datasets dari HuggingFace | Script reproducible, idempotent |
| Parse config files per dataset | Config linked ke well ID, accessible as DataFrame |
| Clean & validate data | No nulls in critical columns, data types correct |
| Compute domain KPIs | GOR, Water Cut, Decline Rate, Cumulative Production, Stability Index per well |
| Output feature store | Parquet files, partitioned by dataset |
| Data quality report | Great Expectations suite passes, HTML report generated |

### 6.2 Layer 3 — ML models

**Model A — Production forecasting (Regression)**

| Requirement | Acceptance criteria |
|---|---|
| Predict oil/gas/water rate per well | MAE/RMSE reported per fase |
| Time series approach | Prophet atau LSTM, benchmark vs XGBoost |
| Per-well dan fleet-level prediction | Both granularities supported |

**Model B — Well classification & anomaly detection**

| Requirement | Acceptance criteria |
|---|---|
| Classify wells: high/medium/low performer | Accuracy, F1-score reported |
| Detect production anomalies | Precision/recall on flagged anomalies |
| Explainability | Feature importance ranked, SHAP values |

**Model C — Control strategy optimization**

| Requirement | Acceptance criteria |
|---|---|
| Compare sol vs nsol vs nscl performance | Statistical test (ANOVA) with p-values |
| Quantify benefit of closed-loop control | Delta production, delta stability |
| Recommend optimal strategy per well type | Rule-based + model-informed recommendation |

### 6.3 Layer 4 — MLOps

| Requirement | Acceptance criteria |
|---|---|
| Dockerized full stack | `docker-compose up` runs entire pipeline |
| MLflow tracking | Experiments logged: params, metrics, artifacts |
| Airflow DAGs | ETL + training + scoring DAGs defined |
| FastAPI endpoint | `/predict`, `/classify`, `/health` endpoints working |
| CI/CD | GitHub Actions: lint, test, build on push |

### 6.4 Layer 5 — Dashboard (initial design, akan di-refine saat POC)

**Sheet 1 — Fleet overview**

| Komponen | Detail |
|---|---|
| KPI cards | Total wells, avg daily production, fleet water cut, fleet GOR |
| Scatter plot | Wells: cumulative oil vs decline rate, colored by class |
| Table | Well ranking by performance score, sortable/filterable |

**Sheet 2 — Well health & anomaly**

| Komponen | Detail |
|---|---|
| Alert banner | Count wells flagged, severity breakdown |
| Time series chart | Select well → production trend + anomaly markers |
| Table | Anomaly list: well ID, type, severity, predicted trend |

**Sheet 3 — Optimization & advisor**

| Komponen | Detail |
|---|---|
| Comparison chart | Open-loop vs closed-loop performance side-by-side |
| Statistical summary | ANOVA results, significance |
| Agent chat panel | Natural language query → actionable recommendation |

### 6.5 Layer 6 — Production Advisor Agent

| Requirement | Acceptance criteria |
|---|---|
| Natural language query | User bisa tanya dalam bahasa natural tentang performa well |
| Model-informed response | Agent menggunakan output dari 3 model untuk menjawab |
| Domain-aware language | Response menggunakan terminologi O&G (GOR, water cut, etc.) |
| Actionable recommendation | Setiap response mengandung rekomendasi spesifik |

---

## 7. Data architecture

### 7.1 Data flow

```
HuggingFace (raw CSV/Parquet)
    ↓ download script
data/raw/
    ├── manywells-sol-1/
    ├── manywells-nsol-1/
    ├── manywells-nscl-1/
    └── configs/
    ↓ ETL pipeline
data/processed/
    ├── wells_features.parquet      # per-well aggregated features
    ├── timeseries_clean.parquet    # cleaned time series semua wells
    └── quality_report.html         # Great Expectations output
    ↓ feature engineering
data/features/
    ├── training_set.parquet        # features + labels untuk training
    ├── scoring_set.parquet         # features untuk inference
    └── feature_metadata.json       # column descriptions, types
    ↓ model training
models/
    ├── forecaster/                 # Prophet/LSTM artifacts
    ├── classifier/                 # XGBoost/RF artifacts
    └── optimizer/                  # ANOVA results + recommendation engine
    ↓ serving
API (FastAPI) → Dashboard (Streamlit) → Agent (LangChain)
```

### 7.2 File format decisions

| Data | Format | Alasan |
|---|---|---|
| Raw data | CSV/Parquet (as downloaded) | Preservasi original |
| Processed data | Parquet | Columnar, compression, fast reads, ARM-compatible |
| Feature store | Parquet | Konsistensi dengan processed |
| Model artifacts | MLflow format (pickle + metadata) | Versioned, reproducible |
| Config metadata | JSON | Human-readable, easy to parse |
| Quality reports | HTML | Self-contained, viewable di browser |

### 7.3 Schema design — wells_features.parquet

| Column | Type | Source | Description |
|---|---|---|---|
| `well_id` | string | Raw | Unique ID (scoped per dataset) |
| `dataset` | string | Derived | sol-1 / nsol-1 / nscl-1 |
| `avg_oil_rate` | float | Computed | Mean oil production rate |
| `avg_gas_rate` | float | Computed | Mean gas production rate |
| `avg_water_rate` | float | Computed | Mean water production rate |
| `cumulative_oil` | float | Computed | Total oil produced |
| `gor` | float | Computed | Gas-Oil Ratio |
| `water_cut` | float | Computed | Water Cut percentage |
| `decline_rate` | float | Computed | Production decline rate |
| `stability_index` | float | Computed | Production variability |
| `performance_class` | string | Model B | high / medium / low |
| `anomaly_flag` | bool | Model B | True if anomalous |

*Schema akan di-finalize setelah EDA pada Phase 1, ketika kolom raw data sudah diinspeksi.*

---

## 8. Tech stack & development environment

### 8.1 Runtime

| Component | Version | Notes |
|---|---|---|
| Python | 3.11+ | Stable, broad library support |
| pip / uv | Latest | `uv` recommended untuk speed di M2 |
| Docker Desktop | Latest | ARM-native di M2 |
| Git | Latest | Via Xcode CLI tools |

### 8.2 Key Python libraries

```
# Data
pandas>=2.0
numpy
pyarrow          # Parquet support
duckdb           # Fast analytical queries
datasets         # HuggingFace data loading

# ML
scikit-learn
xgboost
prophet          # Time series forecasting
shap             # Model explainability

# MLOps
mlflow
fastapi
uvicorn
great-expectations

# Dashboard
streamlit
plotly

# Agent
langchain
openai           # atau anthropic

# Dev
pytest
ruff             # Linter + formatter
pre-commit
```

### 8.3 VSCode setup

**Extensions yang direkomendasikan:**

| Extension | Fungsi |
|---|---|
| **Python** (ms-python) | Core Python support |
| **Pylance** | Type checking, intellisense |
| **Ruff** | Fast linting + formatting (ganti flake8 + black) |
| **Jupyter** | Notebook support untuk EDA |
| **Docker** | Docker file support, container management |
| **GitLens** | Git history, blame |
| **YAML** | Airflow DAGs, docker-compose |
| **Markdown All in One** | Preview PRD dan docs |
| **Thunder Client** | API testing (alternative Postman) |
| **SQLite Viewer** | Inspect DuckDB jika perlu |

**VSCode settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "python.analysis.typeCheckingMode": "basic",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  },
  "jupyter.notebookFileRoot": "${workspaceFolder}"
}
```

### 8.4 MacBook Air M2 considerations

| Concern | Solution |
|---|---|
| ARM Docker images | Gunakan `platform: linux/arm64` di docker-compose, atau multi-platform images |
| Prophet installation | `pip install prophet` works natively di M2 sejak 2024 |
| XGBoost | Native ARM support |
| MLflow | No issue |
| Airflow | Gunakan official ARM image: `apache/airflow:2.x` |
| Memory (8GB/16GB) | Proses per-batch jika 3 juta rows terlalu besar untuk in-memory — Parquet + DuckDB handles ini |

---

## 9. Roadmap & milestones

### Phase overview

| Phase | Nama | Estimasi | Dependency |
|---|---|---|---|
| 0 | Project setup | 1 hari | — |
| 1 | Data acquisition & EDA | 2-3 hari | Phase 0 |
| 2 | Feature engineering | 2-3 hari | Phase 1 |
| 3 | ML modeling | 4-5 hari | Phase 2 |
| 4 | MLOps infrastructure | 3-4 hari | Phase 3 |
| 5 | Dashboard POC | 3-4 hari | Phase 3 |
| 6 | Agent integration | 2-3 hari | Phase 4, 5 |
| 7 | Polish & documentation | 2 hari | Phase 6 |
| 8 | Slide deck | 1-2 hari | Phase 7 |

*Estimasi berdasarkan ~3-4 jam kerja per hari. Total: ~20-27 hari kerja.*

### Definition of done per phase

**Phase 0 — Project setup**
- [ ] Repository created, `.gitignore`, `README.md`
- [ ] Virtual environment configured
- [ ] VSCode settings + extensions
- [ ] `docker-compose.yml` skeleton
- [ ] Folder structure sesuai spec
- [ ] Pre-commit hooks (ruff lint)

**Phase 1 — Data acquisition & EDA**
- [ ] 3 datasets downloaded dan tersimpan di `data/raw/`
- [ ] Config files parsed
- [ ] EDA notebook: distribusi per fase, per dataset, per well
- [ ] Kolom raw teridentifikasi dan terdokumentasi
- [ ] Initial domain KPI computed dan validated
- [ ] Data schema finalized

**Phase 2 — Feature engineering**
- [ ] ETL pipeline script functional
- [ ] Domain KPIs computed: GOR, Water Cut, Decline Rate, Cumulative, Stability Index
- [ ] Feature store output di `data/features/`
- [ ] Great Expectations suite created dan passing
- [ ] Feature metadata documented

**Phase 3 — ML modeling**
- [ ] Model A (forecasting): trained, evaluated, metrics logged
- [ ] Model B (classification + anomaly): trained, evaluated, SHAP values
- [ ] Model C (optimization): ANOVA complete, recommendations generated
- [ ] All experiments tracked di MLflow
- [ ] Best models serialized di `models/`

**Phase 4 — MLOps infrastructure**
- [ ] Dockerfile per service (API, MLflow, Airflow)
- [ ] `docker-compose.yml` complete dan functional
- [ ] FastAPI endpoints: `/predict`, `/classify`, `/optimize`, `/health`
- [ ] Airflow DAGs: ETL, training, scoring
- [ ] GitHub Actions: lint + test on push
- [ ] `make setup`, `make run`, `make test` working

**Phase 5 — Dashboard POC**
- [ ] Streamlit app running locally
- [ ] Sheet 1 (Fleet Overview) functional
- [ ] Sheet 2 (Well Health) functional
- [ ] Sheet 3 (Optimization) functional — tanpa agent dulu
- [ ] Connected ke FastAPI endpoints
- [ ] Design di-review dan di-refine (iterasi dari POC)

**Phase 6 — Agent integration**
- [ ] LangChain agent setup
- [ ] Agent connected ke model outputs
- [ ] Natural language query → domain-aware response
- [ ] Integrated ke Sheet 3 chat panel
- [ ] 5+ test queries documented dengan expected responses

**Phase 7 — Polish & documentation**
- [ ] README.md comprehensive
- [ ] `docs/architecture.md` finalized
- [ ] `docs/domain-glossary.md` — terminologi O&G
- [ ] Code docstrings complete
- [ ] All tests passing

**Phase 8 — Slide deck**
- [ ] Problem statement slide
- [ ] Architecture overview slide
- [ ] Dashboard demo slides (screenshots)
- [ ] Business value slide
- [ ] Tech stack slide
- [ ] Agent demo slide
- [ ] "About me" closing slide

---

## 10. Repository structure

```
wellsight-ai/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Lint + test on push
├── .vscode/
│   ├── settings.json
│   └── extensions.json             # Recommended extensions
├── data/
│   ├── raw/                        # Downloaded from HuggingFace (gitignored)
│   ├── processed/                  # Cleaned parquet
│   ├── features/                   # Feature store
│   └── configs/                    # Well configurations
├── notebooks/
│   ├── 01_data_acquisition.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modeling_forecast.ipynb
│   ├── 05_modeling_classify.ipynb
│   └── 06_modeling_optimize.ipynb
├── src/
│   ├── __init__.py
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── ingest.py               # Download from HuggingFace
│   │   ├── transform.py            # Cleaning, type casting
│   │   └── validate.py             # Great Expectations
│   ├── features/
│   │   ├── __init__.py
│   │   ├── domain_kpis.py          # GOR, Water Cut, etc.
│   │   └── build_features.py       # Full feature pipeline
│   ├── models/
│   │   ├── __init__.py
│   │   ├── forecaster.py           # Production forecasting
│   │   ├── classifier.py           # Well classification
│   │   ├── optimizer.py            # Control strategy analysis
│   │   └── evaluate.py             # Metrics, SHAP
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── schemas.py              # Pydantic models
│   │   └── endpoints.py            # Route handlers
│   ├── dashboard/
│   │   ├── app.py                  # Streamlit entry point
│   │   ├── pages/
│   │   │   ├── fleet_overview.py
│   │   │   ├── well_health.py
│   │   │   └── optimization.py
│   │   └── components/
│   │       ├── kpi_cards.py
│   │       ├── charts.py
│   │       └── agent_panel.py
│   └── agent/
│       ├── __init__.py
│       ├── advisor.py              # LangChain agent
│       ├── tools.py                # Agent tools (model queries)
│       └── prompts.py              # System prompts, domain context
├── mlops/
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.dashboard
│   │   └── Dockerfile.mlflow
│   ├── airflow/
│   │   └── dags/
│   │       ├── etl_dag.py
│   │       ├── training_dag.py
│   │       └── scoring_dag.py
│   └── mlflow/
│       └── mlflow.env
├── tests/
│   ├── test_etl.py
│   ├── test_features.py
│   ├── test_models.py
│   └── test_api.py
├── docs/
│   ├── PRD.md                      # This document
│   ├── architecture.md
│   └── domain-glossary.md
├── models/                         # Serialized model artifacts (gitignored)
├── .gitignore
├── .pre-commit-config.yaml
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```

### Naming conventions

| Item | Convention | Contoh |
|---|---|---|
| Files | snake_case | `domain_kpis.py` |
| Classes | PascalCase | `WellClassifier` |
| Functions | snake_case | `compute_water_cut()` |
| Constants | UPPER_SNAKE | `DEFAULT_DECLINE_WINDOW` |
| Branches | kebab-case | `feature/well-classifier` |
| Commits | Conventional commits | `feat: add GOR computation` |

### Git workflow

- `main` — production-ready, protected
- `dev` — integration branch
- `feature/*` — feature branches dari `dev`
- PR required dari feature → dev, dev → main

---

## 11. Deliverables

| # | Deliverable | Format | Tujuan |
|---|---|---|---|
| 1 | GitHub Repository | Public repo | Technical credibility |
| 2 | Operational Dashboard | Streamlit (local) | Business value demo |
| 3 | MLOps Stack | Docker Compose | Engineering maturity |
| 4 | FastAPI Endpoints | REST API | Production-readiness |
| 5 | Executive Slide Deck | Slides (akan ditentukan) | Portfolio presentation |
| 6 | Technical Documentation | Markdown in `docs/` | Domain understanding |
| 7 | EDA Notebooks | Jupyter | Analytical thinking |

---

## 12. Risks & mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Dataset terlalu besar untuk M2 RAM | Pipeline gagal | Medium | Proses per-batch, gunakan DuckDB lazy loading |
| Prophet/LSTM overfit di simulation data | Model tidak reliable | Medium | Cross-validate, benchmark vs simpler models |
| Agent hallucination | Rekomendasi salah | High | Constraint agent ke model outputs saja, no free-form generation |
| Scope creep ke fitur dashboard | Timeline melar | High | Stick ke 3 sheets, iterasi setelah MVP |
| Docker ARM compatibility issues | Build gagal | Low | Test early di Phase 0, gunakan multi-arch images |
| API key cost (LLM untuk agent) | Budget membengkak | Medium | Gunakan caching, batch queries, set spending limit |

### Scope creep prevention

- Setiap fitur tambahan harus menjawab: "Apakah ini memperkuat narasi portfolio di market O&G?"
- Dashboard design freeze setelah POC review
- No new ML model setelah Phase 3 — focus di quality bukan quantity

---

*End of PRD v1.0*

---

Itu PRD lengkapnya. Beberapa catatan:

- **Schema di section 7.3** akan di-finalize setelah EDA — ketika kita lihat kolom raw yang sebenarnya dari dataset
- **Dashboard design** (section 6.4) marked sebagai initial design, akan di-refine saat POC
- **Estimasi waktu** di section 9 berdasarkan ~3-4 jam/hari — adjust kalau alokasi waktumu berbeda