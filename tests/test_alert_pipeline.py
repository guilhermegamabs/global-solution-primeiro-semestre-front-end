"""Testes da camada pipelines/alert_pipeline.py — pura, sem Streamlit."""

import pytest

from pipelines.alert_pipeline import (
    applyFilters,
    filterBySeverity,
    filterPending,
    filterResolved,
    processAlerts,
)


@pytest.fixture
def sampleAlerts() -> list[dict]:
    return [
        {"id": "A1", "severity": "warning",  "state": "MG", "confidence": 0.80, "status": "pending"},
        {"id": "A2", "severity": "critical", "state": "BA", "confidence": 0.95, "status": "pending"},
        {"id": "A3", "severity": "critical", "state": "MG", "confidence": 0.70, "status": "approved"},
        {"id": "A4", "severity": "caution",  "state": "MS", "confidence": 0.60, "status": "pending"},
        {"id": "A5", "severity": "info",     "state": "GO", "confidence": 0.50, "status": "dismissed"},
    ]


def testProcessAlertsOrdenaPorSeveridadeEConfianca(sampleAlerts):
    out = processAlerts(sampleAlerts)
    ids = [a["id"] for a in out]
    # critical (maior conf primeiro), depois warning, caution, info
    assert ids[0] == "A2"
    assert ids[1] == "A3"
    assert ids[2] == "A1"
    assert ids[3] == "A4"
    assert ids[4] == "A5"


def testApplyFiltersEstado(sampleAlerts):
    out = applyFilters(sampleAlerts, states=["MG"], severities=[],
                        min_confidence=0.0, show="all")
    assert {a["id"] for a in out} == {"A1", "A3"}


def testApplyFiltersSeveridade(sampleAlerts):
    out = applyFilters(sampleAlerts, states=[], severities=["critical"],
                        min_confidence=0.0, show="all")
    assert {a["id"] for a in out} == {"A2", "A3"}


def testApplyFiltersConfiancaMinima(sampleAlerts):
    out = applyFilters(sampleAlerts, states=[], severities=[],
                        min_confidence=0.80, show="all")
    assert {a["id"] for a in out} == {"A1", "A2"}


def testApplyFiltersPendentes(sampleAlerts):
    out = applyFilters(sampleAlerts, states=[], severities=[],
                        min_confidence=0.0, show="pending")
    assert {a["id"] for a in out} == {"A1", "A2", "A4"}


def testApplyFiltersResolvidos(sampleAlerts):
    out = applyFilters(sampleAlerts, states=[], severities=[],
                        min_confidence=0.0, show="resolved")
    assert {a["id"] for a in out} == {"A3", "A5"}


def testApplyFiltersComposto(sampleAlerts):
    out = applyFilters(
        sampleAlerts,
        states=["MG", "BA"],
        severities=["critical", "warning"],
        min_confidence=0.75,
        show="pending",
    )
    assert {a["id"] for a in out} == {"A1", "A2"}


def testFilterBySeverity(sampleAlerts):
    out = filterBySeverity(sampleAlerts, ["warning", "caution"])
    assert {a["id"] for a in out} == {"A1", "A4"}


def testFilterPendingVsResolved(sampleAlerts):
    assert {a["id"] for a in filterPending(sampleAlerts)} == {"A1", "A2", "A4"}
    assert {a["id"] for a in filterResolved(sampleAlerts)} == {"A3", "A5"}


def testProcessAlertsListaVazia():
    assert processAlerts([]) == []


def testApplyFiltersSeveridadeDesconhecidaVaiParaFim():
    alerts = [
        {"id": "X", "severity": "weird", "confidence": 0.99, "status": "pending"},
        {"id": "Y", "severity": "critical", "confidence": 0.5, "status": "pending"},
    ]
    out = processAlerts(alerts)
    assert out[0]["id"] == "Y"
    assert out[1]["id"] == "X"
