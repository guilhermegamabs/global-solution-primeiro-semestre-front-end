import streamlit as st
from providers.mock_alerts import fetchSatelliteAlerts
from providers.mock_weather import fetchWeatherForecast
from pipelines.alert_pipeline import processAlerts
from pipelines.enrichment import enrichWithWeather
from pipelines.risk_model import scoreAlerts


@st.cache_resource
def ensureModelScored(raw: list[dict]) -> list[dict]:
    """Cache do scoring ML — evita re-inferir a cada rerun."""
    return scoreAlerts(raw)


def initState() -> None:
    if "alerts" not in st.session_state:
        raw = list(fetchSatelliteAlerts())
        weather = fetchWeatherForecast()
        raw = enrichWithWeather(raw, weather)
        try:
            raw = ensureModelScored(raw)
        except FileNotFoundError:
            pass
        st.session_state.alerts = processAlerts(raw)

    if "alert_modifications" not in st.session_state:
        st.session_state.alert_modifications = {}


def getAllAlerts() -> list[dict]:
    return st.session_state.get("alerts", [])


def getPendingAlerts() -> list[dict]:
    return [a for a in getAllAlerts() if a.get("status") == "pending"]


def getResolvedAlerts() -> list[dict]:
    return [a for a in getAllAlerts() if a.get("status") != "pending"]


def countPending() -> int:
    return len(getPendingAlerts())


def approveAlert(alert_id: str, custom_action: str | None = None) -> None:
    for alert in st.session_state.alerts:
        if alert["id"] == alert_id:
            alert["status"] = "modified" if custom_action else "approved"
            alert["action_taken"] = custom_action or alert["recommended_action_label"]
            break


def dismissAlert(alert_id: str) -> None:
    for alert in st.session_state.alerts:
        if alert["id"] == alert_id:
            alert["status"] = "dismissed"
            alert["action_taken"] = ""
            break


def startModify(alert_id: str) -> None:
    st.session_state.alert_modifications[alert_id] = "modifying"


def cancelModify(alert_id: str) -> None:
    st.session_state.alert_modifications.pop(alert_id, None)


def isModifying(alert_id: str) -> bool:
    return st.session_state.get("alert_modifications", {}).get(alert_id) == "modifying"
