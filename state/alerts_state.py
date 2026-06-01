import streamlit as st
from providers.mock_alerts import fetch_satellite_alerts
from pipelines.alert_pipeline import process_alerts


def init_state() -> None:
    if "alerts" not in st.session_state:
        raw = fetch_satellite_alerts()
        st.session_state.alerts = process_alerts(raw)

    if "alert_modifications" not in st.session_state:
        st.session_state.alert_modifications = {}


def get_all_alerts() -> list[dict]:
    return st.session_state.get("alerts", [])


def get_pending_alerts() -> list[dict]:
    return [a for a in get_all_alerts() if a.get("status") == "pending"]


def get_resolved_alerts() -> list[dict]:
    return [a for a in get_all_alerts() if a.get("status") != "pending"]


def count_pending() -> int:
    return len(get_pending_alerts())


def approve_alert(alert_id: str, custom_action: str | None = None) -> None:
    for alert in st.session_state.alerts:
        if alert["id"] == alert_id:
            alert["status"] = "modified" if custom_action else "approved"
            alert["action_taken"] = custom_action or alert["recommended_action_label"]
            break


def dismiss_alert(alert_id: str) -> None:
    for alert in st.session_state.alerts:
        if alert["id"] == alert_id:
            alert["status"] = "dismissed"
            alert["action_taken"] = ""
            break


def start_modify(alert_id: str) -> None:
    st.session_state.alert_modifications[alert_id] = "modifying"


def cancel_modify(alert_id: str) -> None:
    st.session_state.alert_modifications.pop(alert_id, None)


def is_modifying(alert_id: str) -> bool:
    return st.session_state.get("alert_modifications", {}).get(alert_id) == "modifying"
