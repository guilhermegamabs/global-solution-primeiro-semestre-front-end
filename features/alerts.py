import streamlit as st
from state.alerts_state import (
    getPendingAlerts,
    getResolvedAlerts,
    approveAlert,
    dismissAlert,
    startModify,
    cancelModify,
    isModifying,
)
from ui.components import renderSeverityBadge, renderConfidenceBar

_ALERT_VARIANT = {
    "critical": "ignis-alert--critical",
    "warning":  "ignis-alert--warning",
    "caution":  "ignis-alert--caution",
    "info":     "ignis-alert--info",
}

_STATUS_CHIP = {
    "approved":  ("Approved",  "var(--ignis-safe)"),
    "modified":  ("Modified",  "var(--ignis-warning)"),
    "dismissed": ("Dismissed", "var(--ignis-muted-4)"),
}


def renderAlertPanel():
    pending = getPendingAlerts()
    resolved = getResolvedAlerts()
    has_pending = len(pending) > 0

    dot_class = "ignis-status-dot--alert" if has_pending else "ignis-status-dot"
    n = len(pending)
    status_text = (
        f"{n} alert{'s' if n != 1 else ''} pending action"
        if has_pending
        else "Queue clear"
    )
    st.markdown(
        f'<div class="ignis-header">'
        f'<span class="ignis-wordmark">IGNIS</span>'
        f'<span class="{dot_class}"></span>'
        f'<span class="ignis-header__caption">{status_text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ignis-section-label">Pending — requires action</div>',
        unsafe_allow_html=True,
    )

    if not pending:
        st.markdown(
            '<div class="ignis-empty">'
            '<div class="ignis-empty-icon">✓</div>'
            '<div class="ignis-empty-title">Queue clear</div>'
            '<div class="ignis-empty-body">'
            "No alerts require action. Satellite feeds refresh every 15 minutes."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        for alert in pending:
            renderPendingAlert(alert)

    if resolved:
        st.markdown('<div class="ignis-spacer-2xl"></div>', unsafe_allow_html=True)
        label = f"Resolved — {len(resolved)} action{'s' if len(resolved) != 1 else ''} taken"
        with st.expander(label, expanded=False):
            for alert in resolved:
                renderResolvedAlert(alert)


def renderPendingAlert(alert):
    alert_id = alert["id"]
    severity = alert["severity"]
    variant = _ALERT_VARIANT.get(severity, "ignis-alert--info")

    region = alert["region"]
    state = alert["state"]
    sat = alert["satellite_source"]
    rationale = alert["ai_rationale"]
    rec_label = alert["recommended_action_label"]
    fire_ha = alert["fire_area_ha"]
    wind_speed = alert["wind_speed"]
    wind_dir = alert["wind_direction"]
    lat = alert["lat"]
    lon = alert["lon"]
    time_ago = formatTimeAgo(alert["detected_at_minutes"])

    badge_html = renderSeverityBadge(severity)
    confidence_html = renderConfidenceBar(alert["confidence"], severity)
    ml_score = alert.get("ml_risk_score")

    if ml_score is not None:
        if ml_score >= 0.75:
            ml_var = "var(--ignis-critical-strong)"
        elif ml_score >= 0.50:
            ml_var = "var(--ignis-warning)"
        elif ml_score >= 0.25:
            ml_var = "var(--ignis-caution-soft)"
        else:
            ml_var = "var(--ignis-safe)"
        ml_badge_html = (
            f'<span class="ignis-chip" title="Probabilidade ML de ação urgente" '
            f'style="--chip-color:{ml_var};">ML risk {ml_score*100:.0f}%</span>'
        )
    else:
        ml_badge_html = ""

    st.markdown(
        f'<div class="ignis-alert {variant}">'
        f'<div class="ignis-alert__head">'
        f'{badge_html}'
        f'<span class="ignis-alert__region">{region}</span>'
        f'<span class="ignis-alert__state">{state}</span>'
        f'<span class="ignis-alert__meta">'
        f'<span class="ignis-alert__metaitem">{sat}</span>'
        f'<span class="ignis-alert__metaitem">{time_ago}</span>'
        f'{confidence_html}'
        f'{ml_badge_html}'
        f'</span></div>'
        f'<div class="ignis-alert__rec">AI recommends: <strong>{rec_label}</strong></div>'
        f'<div class="ignis-alert__rationale">{rationale}</div>'
        f'<div class="ignis-alert__conds">'
        f"{conditionBlock('Affected area', f'{fire_ha:,.0f} ha' if fire_ha else 'Risk zone')}"
        f"{conditionBlock('Wind', f'{wind_speed} km/h {wind_dir}')}"
        f"{conditionBlock('Coordinates', f'{lat:.3f}°, {lon:.3f}°')}"
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if isModifying(alert_id):
        modified_action = st.text_area(
            "Describe the modified action",
            value=rec_label,
            height=75,
            key=f"modify_text_{alert_id}",
            help="Edit the AI recommendation before approving.",
        )
        c_confirm, c_cancel, _ = st.columns([1.6, 1.2, 4])
        with c_confirm:
            if st.button(
                "Confirm modified action",
                key=f"confirm_modify_{alert_id}",
                type="primary",
                use_container_width=True,
            ):
                approveAlert(alert_id, custom_action=modified_action)
                cancelModify(alert_id)
                st.rerun()
        with c_cancel:
            if st.button("Cancel", key=f"cancel_modify_{alert_id}", use_container_width=True):
                cancelModify(alert_id)
                st.rerun()
    else:
        _, c_approve, c_modify, c_dismiss = st.columns([0.5, 2, 2, 1.6])
        with c_approve:
            if st.button(
                "Approve action",
                key=f"approve_{alert_id}",
                type="primary",
                use_container_width=True,
            ):
                approveAlert(alert_id)
                st.rerun()
        with c_modify:
            if st.button(
                "Modify and approve",
                key=f"modify_{alert_id}",
                use_container_width=True,
            ):
                startModify(alert_id)
                st.rerun()
        with c_dismiss:
            if st.button(
                "Dismiss alert",
                key=f"dismiss_{alert_id}",
                use_container_width=True,
            ):
                dismissAlert(alert_id)
                st.rerun()

    st.markdown('<div class="ignis-spacer-md"></div>', unsafe_allow_html=True)


def renderResolvedAlert(alert: dict) -> None:
    severity = alert["severity"]
    region = alert["region"]
    state = alert["state"]
    status = alert.get("status", "pending")
    action_taken = alert.get("action_taken") or ""
    time_ago = formatTimeAgo(alert["detected_at_minutes"])

    badge_html = renderSeverityBadge(severity)
    label, chip_var = _STATUS_CHIP.get(status, ("Dismissed", "var(--ignis-muted-4)"))
    status_html = f'<span class="ignis-chip" style="--chip-color:{chip_var};">{label}</span>'

    action_line = (
        f'<div class="ignis-alert__action">Action recorded: {action_taken}</div>'
        if action_taken else ""
    )

    st.markdown(
        f'<div class="ignis-alert--resolved">'
        f'<div class="ignis-alert__head">'
        f'{badge_html}'
        f'<span class="ignis-alert__region-line">{region}, {state}</span>'
        f'{status_html}'
        f'<span class="ignis-alert__when">{time_ago}</span>'
        f'</div>'
        f'{action_line}'
        f'</div>',
        unsafe_allow_html=True,
    )


def formatTimeAgo(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    if minutes < 1440:
        return f"{minutes // 60}h ago"
    return f"{minutes // 1440}d ago"


def conditionBlock(label: str, value: str) -> str:
    return (
        f'<div class="ignis-cond">'
        f'<span class="ignis-cond__label">{label}</span>'
        f'<span class="ignis-cond__value">{value}</span>'
        f'</div>'
    )
