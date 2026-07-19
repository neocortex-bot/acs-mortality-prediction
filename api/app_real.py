#!/usr/bin/env python3
"""FastAPI service for the real ACS in-hospital mortality model."""
from pathlib import Path
from typing import Literal

import joblib
import numpy as np
import pandas as pd
import shap
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field


ROOT = Path(__file__).resolve().parent
SAFETY_THRESHOLD = 0.069
YOUDEN_THRESHOLD = 0.279

MODEL = joblib.load(ROOT / "model_rf.pkl")
FEATURES: list[str] = joblib.load(ROOT / "features_real.pkl")
FEATURE_MAPPING: dict[str, str] = joblib.load(ROOT / "feature_mapping_real.pkl")
MEDIANS: dict[str, float] = joblib.load(ROOT / "medians_real.pkl")
EXPLAINER = shap.TreeExplainer(MODEL)

INDONESIAN_LABELS = {
    "age_when_admission": "Usia",
    "ureum_igd": "Ureum",
    "egfr_igd": "eGFR",
    "hr": "HR",
    "hb_igd": "Hb",
    "killip": "Killip",
    "sbp": "SBP",
    "rr": "RR",
    "lvef": "LVEF",
    "lvot_vti_igd": "LVOT VTI",
    "tapse_value": "TAPSE",
    "kalium_igd": "K+",
    "aptt_value": "APTT",
}

app = FastAPI(
    title="ACS Mortality Prediction API",
    description="Random Forest model from Dr Izzan's ACS mortality thesis.",
    version="1.0.0",
)


class PatientInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usia: float = Field(..., allow_inf_nan=False)
    hr: float = Field(..., allow_inf_nan=False)
    sbp: float = Field(..., allow_inf_nan=False)
    rr: float = Field(..., allow_inf_nan=False)
    hb: float = Field(..., allow_inf_nan=False)
    kalium: float = Field(..., allow_inf_nan=False)
    ureum: float = Field(..., allow_inf_nan=False)
    egfr: float = Field(..., allow_inf_nan=False)
    aptt: float = Field(..., allow_inf_nan=False)
    lvef: float = Field(..., allow_inf_nan=False)
    lvot_vti: float = Field(..., allow_inf_nan=False)
    tapse: float = Field(..., allow_inf_nan=False)
    killip: Literal[1, 2, 3]


def _positive_class_shap(frame: pd.DataFrame) -> tuple[float, np.ndarray]:
    """Extract class-1 values across old and new SHAP return conventions."""
    explanation = EXPLAINER(frame)
    values = np.asarray(explanation.values)
    base_values = np.asarray(explanation.base_values)

    if values.ndim == 3:
        # Current SHAP: (samples, features, classes).
        contributions = values[0, :, 1]
    elif values.ndim == 2:
        contributions = values[0]
    else:
        raise RuntimeError(f"Unexpected SHAP array shape: {values.shape}")

    if base_values.ndim == 2:
        base_value = float(base_values[0, 1])
    elif base_values.ndim == 1 and base_values.size > 1:
        base_value = float(base_values[1])
    else:
        base_value = float(base_values.reshape(-1)[0])
    return base_value, contributions.astype(float)


def _triage(probability: float) -> tuple[str, str, str]:
    if probability < SAFETY_THRESHOLD:
        return "LOW RISK", "Ward", "Rawat bangsal biasa, monitoring rutin"
    if probability < YOUDEN_THRESHOLD:
        return "INTERMEDIATE RISK", "HCU/ICVCU", "Rawat HCU/ICVCU, monitoring ketat"
    return "HIGH RISK", "ICU", "Rawat ICU, monitoring intensif, pertimbangkan terapi agresif"


@app.post("/predict")
def predict(patient: PatientInput) -> dict:
    supplied = patient.model_dump()
    internal = {FEATURE_MAPPING[key]: value for key, value in supplied.items()}
    frame = pd.DataFrame([[internal[name] for name in FEATURES]], columns=FEATURES)
    frame = frame.fillna(pd.Series(MEDIANS))

    probability = float(MODEL.predict_proba(frame)[0, 1])
    risk_category, triage_label, recommendation = _triage(probability)
    base_value, contributions = _positive_class_shap(frame)

    explained_features = [
        {
            "name": INDONESIAN_LABELS[name],
            "value": float(frame.iloc[0][name]),
            "shap_contribution": round(float(contribution), 6),
            "direction": "positive" if contribution >= 0 else "negative",
        }
        for name, contribution in zip(FEATURES, contributions)
    ]
    explained_features.sort(key=lambda item: abs(item["shap_contribution"]), reverse=True)

    return {
        "probability": round(probability, 6),
        "risk_category": risk_category,
        "triage": {
            "label": triage_label,
            "thresholds": "Ward <0.069, HCU 0.069-0.279, ICU >=0.279",
            "recommendation": recommendation,
        },
        "shap_values": {
            "base_value": round(base_value, 6),
            "output_space": "probability",
            "features": explained_features,
        },
        "contributors_top3": explained_features[:3],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model_loaded": MODEL is not None, "feature_count": len(FEATURES)}


@app.get("/feature_importance")
def feature_importance() -> dict:
    ranked = sorted(zip(FEATURES, MODEL.feature_importances_), key=lambda item: item[1], reverse=True)
    return {
        "features": [
            {
                "name": INDONESIAN_LABELS[name],
                "db_column": name,
                "importance": round(float(importance), 6),
            }
            for name, importance in ranked
        ]
    }


@app.get("/thresholds")
def thresholds() -> dict:
    return {
        "safety": SAFETY_THRESHOLD,
        "youden": YOUDEN_THRESHOLD,
        "tiers": [
            {"risk_category": "LOW RISK", "label": "Ward", "range": "p < 0.069"},
            {"risk_category": "INTERMEDIATE RISK", "label": "HCU/ICVCU", "range": "0.069 <= p < 0.279"},
            {"risk_category": "HIGH RISK", "label": "ICU", "range": "p >= 0.279"},
        ],
    }
