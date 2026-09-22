"""Churn Risk API: send one customer, get back how likely they are to leave the bank."""
import os
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.model import ChurnModel

VERSION = "1.1.0"
THRESHOLD = float(os.getenv("CHURN_THRESHOLD", "0.5"))

app = FastAPI(
    title="Churn Risk API",
    description="Scores how likely a bank customer is to leave, using an XGBoost model "
                "trained on the Churn Modelling dataset.",
    version=VERSION,
)
model = ChurnModel()


class Customer(BaseModel):
    credit_score: int = Field(ge=300, le=900, examples=[619])
    geography: Literal["France", "Germany", "Spain"] = Field(examples=["Germany"])
    gender: Literal["Female", "Male"] = Field(examples=["Female"])
    age: int = Field(ge=18, le=100, examples=[42])
    tenure: int = Field(ge=0, le=10, description="Years as a customer", examples=[2])
    balance: float = Field(ge=0, examples=[125510.82])
    num_of_products: int = Field(ge=1, le=4, examples=[1])
    has_cr_card: bool = Field(examples=[True])
    is_active_member: bool = Field(examples=[False])
    estimated_salary: float = Field(ge=0, examples=[79084.10])


class Prediction(BaseModel):
    churn_risk: float = Field(description="Risk score between 0 and 1")
    at_risk: bool = Field(description="True when churn_risk is at or above the threshold")
    risk_level: Literal["low", "medium", "high"] = Field(description="low < 0.3 <= medium < 0.7 <= high")
    threshold: float
    model_version: str


@app.get("/")
def home():
    return {"service": "Churn Risk API", "version": VERSION, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


def risk_level(risk: float) -> str:
    if risk < 0.3:
        return "low"
    if risk < 0.7:
        return "medium"
    return "high"


@app.post("/predict", response_model=Prediction)
def predict(customer: Customer):
    risk = model.predict(customer.model_dump())
    return Prediction(churn_risk=round(risk, 4), at_risk=risk >= THRESHOLD,
                      risk_level=risk_level(risk), threshold=THRESHOLD, model_version=VERSION)