"""API tests."""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_fleet():
    r = client.get("/fleet")
    assert r.status_code == 200
    assert r.json()["total_wells"] == 6000


def test_optimize():
    r = client.get("/optimize")
    assert r.status_code == 200
    assert "anova" in r.json()


def test_classify():
    r = client.post(
        "/classify",
        json={
            "avg_qoil": 35.0,
            "avg_qgas": 25000.0,
            "avg_qwat": 15.0,
            "avg_qliq": 50.0,
            "avg_pbh": 260.0,
            "avg_pwh": 70.0,
            "avg_chk": 0.5,
            "gor": 714.0,
            "water_cut": 0.3,
            "stability_index": 0.26,
            "decline_rate": 0.0,
            "choked_fraction": 0.5,
        },
    )
    assert r.status_code == 200
    assert r.json()["performance_class"] in ["high", "medium", "low"]


def test_predict():
    r = client.post(
        "/predict",
        json={
            "CHK": 0.5,
            "PBH": 260.0,
            "PWH": 70.0,
            "PDC": 35.0,
            "TBH": 380.0,
            "TWH": 350.0,
            "WGL": 0.0,
            "FGAS": 0.3,
            "FOIL": 0.45,
            "FWAT": 0.25,
        },
    )
    assert r.status_code == 200
    assert "predicted_qoil" in r.json()
