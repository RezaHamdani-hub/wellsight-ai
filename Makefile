.PHONY: setup install test lint format run-api run-dashboard docker-up docker-down

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -e ".[dev]"
	. .venv/bin/activate && pre-commit install

install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

test:
	pytest -v

run-api:
	uvicorn src.api.main:app --reload --port 8000

run-dashboard:
	streamlit run src/dashboard/app.py

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

download-data:
	python -m src.etl.ingest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
