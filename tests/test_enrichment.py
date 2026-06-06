"""Testes do pipeline de enriquecimento (2ª fonte: weather)."""

import pytest

from pipelines.enrichment import aggregateByState, enrichWithWeather


@pytest.fixture
def alerts():
    return [
        {"id": "A1", "state": "MG", "severity": "critical", "fire_area_ha": 100},
        {"id": "A2", "state": "MG", "severity": "warning",  "fire_area_ha": 50},
        {"id": "A3", "state": "AM", "severity": "caution",  "fire_area_ha": 10},
    ]


@pytest.fixture
def weather():
    return {
        "MG": {"wind_kmh": 50, "humidity_pct": 25, "rain_mm_24h": 0.0, "risk_index": 0.9},
        "AM": {"wind_kmh": 10, "humidity_pct": 85, "rain_mm_24h": 18.0, "risk_index": 0.15},
    }


def testEnrichAnexaWeather(alerts, weather):
    out = enrichWithWeather(alerts, weather)
    assert out[0]["weather"]["wind_kmh"] == 50
    assert out[2]["weather"]["wind_kmh"] == 10


def testEnrichSpreadAltoEmEstadoSecoVentoso(alerts, weather):
    out = enrichWithWeather(alerts, weather)
    mg = next(a for a in out if a["state"] == "MG")
    am = next(a for a in out if a["state"] == "AM")
    assert mg["spread_risk_24h"] > am["spread_risk_24h"]
    assert mg["spread_risk_24h"] >= 0.5
    assert am["spread_risk_24h"] <= 0.3


def testEnrichSpreadDentroDe01(alerts, weather):
    out = enrichWithWeather(alerts, weather)
    for a in out:
        assert 0.0 <= a["spread_risk_24h"] <= 1.0


def testEnrichEstadoSemForecastUsaFallback(alerts):
    out = enrichWithWeather(alerts, {})
    for a in out:
        assert a["weather"] == {}
        assert 0.0 <= a["spread_risk_24h"] <= 1.0


def testAggregateByStateContaESeveridadeMax(alerts):
    agg = aggregateByState(alerts)
    assert agg["MG"]["count"] == 2
    assert agg["MG"]["max_sev"] == "critical"
    assert agg["MG"]["total_area_ha"] == 150
    assert agg["AM"]["count"] == 1
    assert agg["AM"]["max_sev"] == "caution"


def testAggregateListaVazia():
    assert aggregateByState([]) == {}
