import streamlit as st
from state.alerts_state import (
    get_pending_alerts,
    get_resolved_alerts,
    approve_alert,
    dismiss_alert,
    start_modify,
    cancel_modify,
    is_modifying,
)
from ui.components import render_severity_badge, render_confidence_bar

_SEVERITY_ROW_BG = {
    "critical": "oklch(0.13 0.018 22)",
    "warning":  "oklch(0.13 0.012 42)",
    "caution":  "oklch(0.13 0.007 75)",
    "info":     "oklch(0.13 0.007 230)",
}

_SEVERITY_BORDER_HUE = {
    "critical": "22",
    "warning":  "42",
    "caution":  "75",
    "info":     "230",
}


def render_alert_panel() -> None:
    pending = get_pending_alerts()
    resolved = get_resolved_alerts()
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
        f'<span style="font-size:13px;color:oklch(0.58 0.008 353);'
        f"font-family:'JetBrains Mono','Courier New',monospace;\">{status_text}</span>"
        f"</div>",
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
            _render_pending_alert(alert)

    if resolved:
        st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
        label = f"Resolved — {len(resolved)} action{'s' if len(resolved) != 1 else ''} taken"
        with st.expander(label, expanded=False):
            for alert in resolved:
                _render_resolved_alert(alert)


def _render_pending_alert(alert: dict) -> None:
    alert_id = alert["id"]
    severity = alert["severity"]
    row_bg = _SEVERITY_ROW_BG.get(severity, "oklch(0.13 0.000 0)")
    border_hue = _SEVERITY_BORDER_HUE.get(severity, "353")
    border_color = f"oklch(0.26 0.010 {border_hue})"

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
    time_ago = _format_time_ago(alert["detected_at_minutes"])

    badge_html = render_severity_badge(severity)
    confidence_html = render_confidence_bar(alert["confidence"], severity)

    st.markdown(
        f'<div style="'
        f"background:{row_bg};"
        f"border-radius:6px;"
        f"padding:16px 20px 14px;"
        f"margin-bottom:4px;"
        f"border:1px solid {border_color};"
        f'">'
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f"{badge_html}"
        f'<span style="font-size:15px;font-weight:600;color:oklch(0.93 0.005 353);'
        f"font-family:'Inter',system-ui,sans-serif;\">{region}</span>"
        f'<span style="font-size:14px;font-weight:400;color:oklch(0.65 0.008 353);'
        f"font-family:'Inter',system-ui,sans-serif;\">{state}</span>"
        f'<span style="margin-left:auto;display:flex;align-items:center;gap:14px;flex-wrap:wrap;">'
        f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:11px;color:oklch(0.48 0.006 353);">{sat}</span>'
        f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:11px;color:oklch(0.48 0.006 353);">{time_ago}</span>'
        f"{confidence_html}"
        f"</span>"
        f"</div>"
        f'<div style="margin-top:10px;font-size:13px;color:oklch(0.58 0.008 353);'
        f"font-family:'Inter',system-ui,sans-serif;\">"
        f'AI recommends: <strong style="color:oklch(0.88 0.005 353);">{rec_label}</strong>'
        f"</div>"
        f'<div style="margin-top:7px;font-size:12px;color:oklch(0.52 0.007 353);'
        f"font-family:'Inter',system-ui,sans-serif;line-height:1.65;max-width:80ch;"
        f'text-wrap:pretty;">{rationale}</div>'
        f'<div style="margin-top:13px;display:flex;gap:28px;flex-wrap:wrap;">'
        f"{_condition_block('Affected area', f'{fire_ha:,.0f} ha' if fire_ha else 'Risk zone')}"
        f"{_condition_block('Wind', f'{wind_speed} km/h {wind_dir}')}"
        f"{_condition_block('Coordinates', f'{lat:.3f}°, {lon:.3f}°')}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if is_modifying(alert_id):
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
                approve_alert(alert_id, custom_action=modified_action)
                cancel_modify(alert_id)
                st.rerun()
        with c_cancel:
            if st.button("Cancel", key=f"cancel_modify_{alert_id}", use_container_width=True):
                cancel_modify(alert_id)
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
                approve_alert(alert_id)
                st.rerun()
        with c_modify:
            if st.button(
                "Modify and approve",
                key=f"modify_{alert_id}",
                use_container_width=True,
            ):
                start_modify(alert_id)
                st.rerun()
        with c_dismiss:
            if st.button(
                "Dismiss alert",
                key=f"dismiss_{alert_id}",
                use_container_width=True,
            ):
                dismiss_alert(alert_id)
                st.rerun()

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)


def _render_resolved_alert(alert: dict) -> None:
    severity = alert["severity"]
    region = alert["region"]
    state = alert["state"]
    status = alert.get("status", "pending")
    action_taken = alert.get("action_taken") or ""
    time_ago = _format_time_ago(alert["detected_at_minutes"])

    badge_html = render_severity_badge(severity)

    if status == "approved":
        status_html = (
            '<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
            "font-size:10px;padding:2px 8px;border-radius:4px;"
            "background:oklch(0.70 0.180 145 / 0.12);"
            "color:oklch(0.70 0.180 145);"
            'border:1px solid oklch(0.70 0.180 145 / 0.30);'
            'text-transform:uppercase;letter-spacing:0.06em;">Approved</span>'
        )
    elif status == "modified":
        status_html = (
            '<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
            "font-size:10px;padding:2px 8px;border-radius:4px;"
            "background:oklch(0.67 0.210 42 / 0.12);"
            "color:oklch(0.67 0.210 42);"
            'border:1px solid oklch(0.67 0.210 42 / 0.30);'
            'text-transform:uppercase;letter-spacing:0.06em;">Modified</span>'
        )
    else:
        status_html = (
            '<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
            "font-size:10px;padding:2px 8px;border-radius:4px;"
            "background:oklch(0.40 0.005 353 / 0.12);"
            "color:oklch(0.55 0.007 353);"
            'border:1px solid oklch(0.40 0.005 353 / 0.30);'
            'text-transform:uppercase;letter-spacing:0.06em;">Dismissed</span>'
        )

    action_line = (
        f'<div style="margin-top:7px;font-size:12px;color:oklch(0.48 0.006 353);'
        f"font-family:'Inter',system-ui,sans-serif;\">Action recorded: {action_taken}</div>"
        if action_taken
        else ""
    )

    st.markdown(
        f'<div style="'
        f"background:oklch(0.11 0.000 0);"
        f"border-radius:6px;"
        f"padding:11px 18px;"
        f"margin-bottom:6px;"
        f"opacity:0.60;"
        f'border:1px solid oklch(0.20 0.003 353);">'
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
        f"{badge_html}"
        f'<span style="font-size:14px;font-weight:500;color:oklch(0.72 0.005 353);'
        f"font-family:'Inter',system-ui,sans-serif;\">{region}, {state}</span>"
        f"{status_html}"
        f'<span style="margin-left:auto;font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:11px;color:oklch(0.42 0.005 353);">{time_ago}</span>'
        f"</div>"
        f"{action_line}"
        f"</div>",
        unsafe_allow_html=True,
    )


def _format_time_ago(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    if minutes < 1440:
        return f"{minutes // 60}h ago"
    return f"{minutes // 1440}d ago"


def _condition_block(label: str, value: str) -> str:
    return (
        f'<div style="display:flex;flex-direction:column;gap:2px;">'
        f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:9px;text-transform:uppercase;letter-spacing:0.09em;'
        f'color:oklch(0.38 0.004 353);">{label}</span>'
        f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:13px;font-weight:500;color:oklch(0.90 0.005 353);">{value}</span>'
        f"</div>"
    )
