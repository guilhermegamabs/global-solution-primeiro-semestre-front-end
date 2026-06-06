"""Testes de providers — valida shape e campos obrigatórios dos mocks.

Mocks decorados com @st.cache_data — chamamos via .__wrapped__ para
evitar dependência de runtime Streamlit em CI.
"""

from providers.mock_alerts import fetchSatelliteAlerts
from providers.mock_timeseries import (
    fetchFireTimeseries,
    fetchHourlyPattern,
    fetchStateImpact,
)

REQUIRED_ALERT_FIELDS = {
    "id", "severity", "region", "state", "lat", "lon",
    "confidence", "fire_area_ha", "wind_speed", "satellite_source",
    "recommended_action", "ai_rationale", "status",
}


def call(fn):
    """Chama função possivelmente decorada com st.cache_data."""
    return fn.__wrapped__() if hasattr(fn, "__wrapped__") else fn()


def testAlertsTemCamposObrigatorios():
    alerts = call(fetchSatelliteAlerts)
    assert len(alerts) >= 3
    for a in alerts:
        missing = REQUIRED_ALERT_FIELDS - set(a.keys())
        assert not missing, f"campos faltando em {a.get('id')}: {missing}"


def testAlertsSeveridadeValida():
    alerts = call(fetchSatelliteAlerts)
    valid = {"critical", "warning", "caution", "info", "safe"}
    for a in alerts:
        assert a["severity"] in valid


def testAlertsConfiancaEntre0E1():
    alerts = call(fetchSatelliteAlerts)
    for a in alerts:
        assert 0.0 <= a["confidence"] <= 1.0


def testAlertsCoordenadasBrasil():
    alerts = call(fetchSatelliteAlerts)
    for a in alerts:
        assert -35 <= a["lat"] <= 6
        assert -75 <= a["lon"] <= -34


def testTimeseriesArraysAlinhados():
    ts = call(fetchFireTimeseries)
    n = len(ts["dates"])
    assert n == 30
    for key in ("critical", "warning", "caution", "critical_area_ha", "warning_area_ha"):
        assert len(ts[key]) == n


def testStateImpactArraysAlinhados():
    s = call(fetchStateImpact)
    n = len(s["states"])
    for key in ("critical_ha", "warning_ha", "caution_ha"):
        assert len(s[key]) == n


def testHourlyPattern24h():
    h = call(fetchHourlyPattern)
    assert h["hours"] == list(range(24))
    assert len(h["counts"]) == 24
    assert all(c >= 0 for c in h["counts"])
