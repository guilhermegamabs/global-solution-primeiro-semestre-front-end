"""Testes do modelo de IA (pipelines/risk_model.py).

Treina modelo se ainda não existe (idempotente).
"""

import os

import pytest

from pipelines import risk_model
from pipelines.train_risk_model import main as train_main


@pytest.fixture(scope="module", autouse=True)
def ensureModelTrained():
    if not os.path.exists(risk_model._MODEL_PATH):
        train_main()
    assert os.path.exists(risk_model._MODEL_PATH)


def alert(area, wind, conf, hours, sev):
    return {
        "id": "T",
        "fire_area_ha": area,
        "wind_speed": wind,
        "confidence": conf,
        "detected_at_minutes": int(hours * 60),
        "severity": sev,
    }


def testScoreAlertsAnexaCampo():
    alerts = [alert(800, 40, 0.92, 2, "critical")]
    out = risk_model.scoreAlerts(alerts)
    assert "ml_risk_score" in out[0]
    assert 0.0 <= out[0]["ml_risk_score"] <= 1.0


def testAlertaCriticoTemScoreMaiorQueBaixo():
    high = alert(3000, 55, 0.95, 1, "critical")
    low = alert(5, 5, 0.20, 30, "caution")
    p_high = risk_model.predictSingle(high)
    p_low = risk_model.predictSingle(low)
    assert p_high > p_low
    assert p_high > 0.6
    assert p_low < 0.4


def testScoreAlertsListaVazia():
    assert risk_model.scoreAlerts([]) == []


def testFeaturesFromAlertDimensoes():
    feats = risk_model.featuresFromAlert(alert(100, 20, 0.5, 1, "warning"))
    assert len(feats) == 5
    assert all(isinstance(x, float) for x in feats)


def testSeveridadeDesconhecidaViraZero():
    feats = risk_model.featuresFromAlert(
        {"fire_area_ha": 0, "wind_speed": 0, "confidence": 0,
         "detected_at_minutes": 0, "severity": "xyz"}
    )
    assert feats[-1] == 0.0


def testScoreAlertsPreservaOrdem():
    a = [
        alert(100, 10, 0.5, 1, "warning"),
        alert(2000, 50, 0.9, 0, "critical"),
        alert(0, 0, 0.1, 24, "caution"),
    ]
    out = risk_model.scoreAlerts(a)
    assert [x["id"] for x in out] == ["T", "T", "T"]
    assert len(out) == 3
