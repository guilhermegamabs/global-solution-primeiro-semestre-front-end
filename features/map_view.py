import streamlit as st
import plotly.graph_objects as go
from state.alerts_state import getAllAlerts
from pipelines.alert_pipeline import applyFilters
from ui.components import renderSeverityBadge

_SEVERITY_HEX: dict[str, str] = {
    "critical": "#cc2418",
    "warning": "#d97020",
    "caution": "#c8b800",
    "safe": "#30a850",
    "info": "#2068cc",
}

_SEVERITY_ORDER = ["critical", "warning", "caution", "safe", "info"]

_STATUS_COLOR_VAR = {
    "approved": "var(--ignis-safe)",
    "modified": "var(--ignis-warning)",
    "dismissed": "var(--ignis-muted-4)",
}

def renderMapView() -> None:
    alerts = getAllAlerts()
    all_states = sorted({a["state"] for a in alerts})

    st.markdown('<div class="ignis-spacer-sm"></div>', unsafe_allow_html=True)

    fc1, fc2, fc3, fc4 = st.columns([1.8, 1.8, 1.2, 1.0])

    with fc1:
        sel_states = st.multiselect(
            "State",
            options=all_states,
            default=[],
            placeholder="All states",
            key="map_states",
        )
    with fc2:
        sel_severities = st.multiselect(
            "Severity",
            options=_SEVERITY_ORDER,
            format_func=str.upper,
            default=[],
            placeholder="All levels",
            key="map_severities",
        )
    with fc3:
        min_conf = st.slider(
            "Min. confidence",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            format="%d%%",
            key="map_confidence",
        )
    with fc4:
        show = st.selectbox(
            "Status",
            options=["all", "pending", "resolved"],
            format_func=str.capitalize,
            key="map_show",
        )

    filtered = applyFilters(
        alerts,
        states=sel_states,
        severities=sel_severities,
        min_confidence=min_conf / 100,
        show=show,
    )

    n = len(filtered)
    n_crit = sum(1 for a in filtered if a["severity"] == "critical")
    total_ha = sum(a["fire_area_ha"] for a in filtered)
    n_pending = sum(1 for a in filtered if a.get("status") == "pending")

    crit_badge_html = renderSeverityBadge("critical", f"{n_crit}") if n_crit else ""
    sep = '<span class="ignis-stats-bar__sep">·</span>'
    crit_segment = f"{crit_badge_html} {sep} " if crit_badge_html else ""

    st.markdown(
        f'<div class="ignis-stats-bar">'
        f'<span class="ignis-stats-bar__item">'
        f'<span class="ignis-stats-bar__num">{n}</span>'
        f'&nbsp;hotspot{"s" if n != 1 else ""}</span>'
        f'{sep}{crit_segment}'
        f'<span class="ignis-stats-bar__item">'
        f'<span class="ignis-stats-bar__num--soft">{total_ha:,.0f}&nbsp;ha</span>'
        f'&nbsp;total</span>'
        f'{sep}'
        f'<span class="ignis-stats-bar__item">'
        f'<span class="ignis-stats-bar__num--soft">{n_pending}</span>'
        f'&nbsp;awaiting action</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            '<div class="ignis-empty">'
            '<div class="ignis-empty-icon">◎</div>'
            '<div class="ignis-empty-title">No hotspots match filters</div>'
            '<div class="ignis-empty-body">Adjust the filters above to show satellite detections.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    fig = buildMap(filtered)
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": True,
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage"],
            "displaylogo": False,
        },
    )

    st.markdown(
        '<div class="ignis-section-label ignis-section-label--spaced">Filtered detections</div>',
        unsafe_allow_html=True,
    )
    for alert in filtered:
        renderListRow(alert)


def buildMap(alerts: list[dict]) -> go.Figure:
    max_area = max((a["fire_area_ha"] for a in alerts), default=1) or 1
    fig = go.Figure()

    for sev in _SEVERITY_ORDER:
        sev_alerts = [a for a in alerts if a["severity"] == sev]
        if not sev_alerts:
            continue
        sizes = [
            max(12, min(44, 12 + (a["fire_area_ha"] / max_area) * 32))
            for a in sev_alerts
        ]
        fig.add_trace(
            go.Scattermapbox(
                lat=[a["lat"] for a in sev_alerts],
                lon=[a["lon"] for a in sev_alerts],
                mode="markers",
                name=sev.upper(),
                marker=dict(size=sizes, color=_SEVERITY_HEX[sev], opacity=0.90),
                text=[hoverText(a) for a in sev_alerts],
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=-14.0, lon=-52.0), zoom=3.5),
        paper_bgcolor="rgba(26,26,26,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=540,
        showlegend=True,
        legend=dict(
            bgcolor="#1e1e1e",
            bordercolor="#333333",
            borderwidth=1,
            font=dict(family="'JetBrains Mono', 'Courier New', monospace", size=11, color="#ededed"),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
        ),
        hoverlabel=dict(
            bgcolor="#282828",
            bordercolor="#c43055",
            font=dict(family="'JetBrains Mono', 'Courier New', monospace", size=12, color="#ededed"),
            align="left",
        ),
    )
    return fig


def hoverText(a: dict) -> str:
    area = f"{a['fire_area_ha']:,.0f} ha" if a["fire_area_ha"] else "Risk zone"
    return (
        f"<b>{a['region']}, {a['state']}</b><br>"
        f"Severity: <b>{a['severity'].upper()}</b><br>"
        f"Confidence: {round(a['confidence'] * 100)}%<br>"
        f"Area: {area}<br>"
        f"Source: {a['satellite_source']}<br>"
        f"Detected: {fmt(a['detected_at_minutes'])}<br>"
        f"{a['recommended_action_label']}"
    )

def renderListRow(a: dict) -> None:
    badge = renderSeverityBadge(a["severity"])
    status = a.get("status", "pending")
    area = f"{a['fire_area_ha']:,.0f} ha" if a["fire_area_ha"] else "Risk zone"
    status_var = _STATUS_COLOR_VAR.get(status, "var(--ignis-critical)")

    st.markdown(
        f'<div class="ignis-map-row">'
        f'{badge}'
        f'<span class="ignis-map-row__name">{a["region"]}, {a["state"]}</span>'
        f'<span class="ignis-map-row__meta">{round(a["confidence"] * 100)}% · {area}</span>'
        f'<span class="ignis-map-row__right">'
        f'<span class="ignis-map-row__when">{fmt(a["detected_at_minutes"])}</span>'
        f'<span class="ignis-map-row__status" style="--status-color:{status_var};">{status}</span>'
        f'</span></div>',
        unsafe_allow_html=True,
    )

def fmt(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    if minutes < 1440:
        return f"{minutes // 60}h ago"
    return f"{minutes // 1440}d ago"
