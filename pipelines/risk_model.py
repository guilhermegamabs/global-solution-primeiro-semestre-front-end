from __future__ import annotations

import os
from typing import Iterable

import joblib
import numpy as np

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "risk_model.joblib")

_SEVERITY_ORDINAL = {"critical": 3, "warning": 2, "caution": 1, "info": 0, "safe": 0}

def featuresFromAlert(alert: dict) -> list[float]:
    return [
        float(alert.get("fire_area_ha", 0.0)),
        float(alert.get("wind_speed", 0.0)),
        float(alert.get("confidence", 0.0)),
        float(alert.get("detected_at_minutes", 0)) / 60.0,
        float(_SEVERITY_ORDINAL.get(alert.get("severity", "info"), 0)),
    ]


def loadModel():
    if not os.path.exists(_MODEL_PATH):
        raise FileNotFoundError(
            f"Modelo não encontrado em {_MODEL_PATH}. "
            "Rode: python -m pipelines.train_risk_model"
        )
    return joblib.load(_MODEL_PATH)

def scoreAlerts(alerts: list[dict]) -> list[dict]:
    if not alerts:
        return alerts
    model = loadModel()
    X = np.array([featuresFromAlert(a) for a in alerts])
    probs = model.predict_proba(X)[:, 1]
    for alert, p in zip(alerts, probs):
        alert["ml_risk_score"] = float(p)
    return alerts

def predictSingle(alert: dict) -> float:
    model = loadModel()
    X = np.array([featuresFromAlert(alert)])
    return float(model.predict_proba(X)[0, 1])
