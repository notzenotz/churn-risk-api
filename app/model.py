"""Loads the churn model once and turns raw customer data into a risk score."""
import json
from pathlib import Path

import numpy as np
import xgboost as xgb

MODEL_DIR = Path(__file__).resolve().parent.parent / "model"


class ChurnModel:
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.features = json.loads((model_dir / "features.json").read_text())
        self.booster = xgb.Booster()
        self.booster.load_model(str(model_dir / "churn_model.json"))

    def to_features(self, c: dict) -> dict:
        """Same feature engineering as the training notebook."""
        return {
            "CreditScore": c["credit_score"],
            "Age": c["age"],
            "Tenure": c["tenure"],
            "Balance": c["balance"],
            "NumOfProducts": c["num_of_products"],
            "HasCrCard": int(c["has_cr_card"]),
            "IsActiveMember": int(c["is_active_member"]),
            "EstimatedSalary": c["estimated_salary"],
            "SaldoNol": int(c["balance"] == 0),
            "IsFemale": int(c["gender"] == "Female"),
            "Geography_Germany": int(c["geography"] == "Germany"),
            "Geography_Spain": int(c["geography"] == "Spain"),
        }

    def predict(self, customer: dict) -> float:
        row = self.to_features(customer)
        x = np.array([[row[f] for f in self.features]], dtype=float)
        dm = xgb.DMatrix(x, feature_names=self.features)
        return float(self.booster.predict(dm)[0])
