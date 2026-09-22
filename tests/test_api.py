"""Run with: pytest -v"""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

LOW_RISK = {  # young, active, 2 products, France
    "credit_score": 700, "geography": "France", "gender": "Male", "age": 30, "tenure": 5,
    "balance": 0.0, "num_of_products": 2, "has_cr_card": True, "is_active_member": True,
    "estimated_salary": 90000.0,
}
HIGH_RISK = {  # 58 years old, inactive, 4 products, Germany
    "credit_score": 650, "geography": "Germany", "gender": "Female", "age": 58, "tenure": 2,
    "balance": 130000.0, "num_of_products": 4, "has_cr_card": True, "is_active_member": False,
    "estimated_salary": 30000.0,
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_predict_returns_a_score_between_0_and_1():
    r = client.post("/predict", json=LOW_RISK)
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["churn_risk"] <= 1
    assert body["at_risk"] == (body["churn_risk"] >= body["threshold"])


def test_high_risk_profile_scores_higher_than_low_risk():
    low = client.post("/predict", json=LOW_RISK).json()["churn_risk"]
    high = client.post("/predict", json=HIGH_RISK).json()["churn_risk"]
    assert high > low


def test_unknown_country_is_rejected():
    r = client.post("/predict", json={**LOW_RISK, "geography": "Indonesia"})
    assert r.status_code == 422


def test_missing_field_is_rejected():
    customer = dict(LOW_RISK)
    del customer["age"]
    assert client.post("/predict", json=customer).status_code == 422


def test_model_expects_the_training_features_in_order():
    features = json.loads((Path(__file__).parent.parent / "model" / "features.json").read_text())
    assert features == [
        "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "HasCrCard",
        "IsActiveMember", "EstimatedSalary", "SaldoNol", "IsFemale",
        "Geography_Germany", "Geography_Spain",
    ]



def test_risk_level_labels():
    from app.main import risk_level
    assert risk_level(0.10) == "low"
    assert risk_level(0.30) == "medium"
    assert risk_level(0.69) == "medium"
    assert risk_level(0.70) == "high"