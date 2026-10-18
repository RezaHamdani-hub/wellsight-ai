"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="WellSight AI",
    description="AI-powered well production intelligence API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}
