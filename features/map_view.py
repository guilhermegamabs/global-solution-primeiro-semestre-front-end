import streamlit as st
import plotly.graph_objects as go
from state.alerts_state import get_all_alerts
from pipelines.alert_pipeline import apply_filters
from ui.components import render_severity_badge

_SEVERITY_HEX: dict[str, str] = {
    "critical": "#cc2418",
    "warning":  "#d97020",
    "caution":  "#c8b800",
    "safe":     "#30a850",
    "info":     "#2068cc",
}

_SEVERITY_ORDER = ["critical", "warning", "caution", "safe", "info"]


def render_map_view() -> None:
    alerts = get_all_alerts()
    all_states = sorted({a["state"] for a in alerts})

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

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

    filtered = apply_filters(
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

    crit_badge_html = render_severity_badge("critical", f"{n_crit}") if n_crit else ""
    sep = '<span style="color:oklch(0.26 0.004 353);">·</span>'
    crit_segment = f"{crit_badge_html} {sep} " if crit_badge_html else ""

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:14px;margin:10px 0 16px;'
        f'flex-wrap:wrap;font-family:\'JetBrains Mono\',\'Courier New\',monospace;">'
        f'<span style="font-size:13px;color:oklch(0.55 0.007 353);">'
        f'<span style="font-size:17px;font-weight:700;color:oklch(0.93 0.005 353);">{n}</span>'
        f'&nbsp;hotspot{"s" if n != 1 else ""}</span>'
        f'{sep}'
        f'{crit_segment}'
        f'<span style="font-size:13px;color:oklch(0.55 0.007 353);">'
        f'<span style="font-weight:600;color:oklch(0.90 0.005 353);">{total_ha:,.0f}&nbsp;ha</span>'
        f'&nbsp;total</span>'
        f'{sep}'
        f'<span style="font-size:13px;color:oklch(0.55 0.007 353);">'
        f'<span style="font-weight:600;color:oklch(0.90 0.005 353);">{n_pending}</span>'
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

    fig = _build_map(filtered)
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
        '<div class="ignis-section-label" style="margin-top:16px;">Filtered detections</div>',
        unsafe_allow_html=True,
    )
    for alert in filtered:
        _render_list_row(alert)


def _build_map(alerts: list[dict]) -> go.Figure:
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
                marker=dict(
                    size=sizes,
                    color=_SEVERITY_HEX[sev],
                    opacity=0.90,
                ),
                text=[_hover_text(a) for a in sev_alerts],
                hovertemplate="%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=-14.0, lon=-52.0),
            zoom=3.5,
        ),
        paper_bgcolor="rgba(26,26,26,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=540,
        showlegend=True,
        legend=dict(
            bgcolor="#1e1e1e",
            bordercolor="#333333",
            borderwidth=1,
            font=dict(
                family="'JetBrains Mono', 'Courier New', monospace",
                size=11,
                color="#ededed",
            ),
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=0.02,
        ),
        hoverlabel=dict(
            bgcolor="#282828",
            bordercolor="#c43055",
            font=dict(
                family="'JetBrains Mono', 'Courier New', monospace",
                size=12,
                color="#ededed",
            ),
            align="left",
        ),
    )

    return fig


def _hover_text(a: dict) -> str:
    area = f"{a['fire_area_ha']:,.0f} ha" if a["fire_area_ha"] else "Risk zone"
    return (
        f"<b>{a['region']}, {a['state']}</b><br>"
        f"Severity: <b>{a['severity'].upper()}</b><br>"
        f"Confidence: {round(a['confidence'] * 100)}%<br>"
        f"Area: {area}<br>"
        f"Source: {a['satellite_source']}<br>"
        f"Detected: {_fmt(a['detected_at_minutes'])}<br>"
        f"{a['recommended_action_label']}"
    )


def _render_list_row(a: dict) -> None:
    badge = render_severity_badge(a["severity"])
    status = a.get("status", "pending")
    area = f"{a['fire_area_ha']:,.0f} ha" if a["fire_area_ha"] else "Risk zone"
    status_color = {
        "approved":  "oklch(0.70 0.180 145)",
        "modified":  "oklch(0.67 0.210 42)",
        "dismissed": "oklch(0.50 0.008 353)",
    }.get(status, "oklch(0.55 0.230 22)")

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;padding:8px 14px;'
        f'margin-bottom:4px;border-radius:5px;background:oklch(0.14 0.000 0);'
        f'border:1px solid oklch(0.20 0.003 353);flex-wrap:wrap;">'
        f'{badge}'
        f'<span style="font-family:\'Inter\',system-ui,sans-serif;font-size:13px;'
        f'font-weight:500;color:oklch(0.88 0.005 353);">{a["region"]}, {a["state"]}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'color:oklch(0.45 0.006 353);">{round(a["confidence"] * 100)}% · {area}</span>'
        f'<span style="margin-left:auto;display:flex;align-items:center;gap:10px;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'color:oklch(0.38 0.005 353);">{_fmt(a["detected_at_minutes"])}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
        f'text-transform:uppercase;letter-spacing:0.05em;color:{status_color};">{status}</span>'
        f'</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _fmt(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}m ago"
    if minutes < 1440:
        return f"{minutes // 60}h ago"
    return f"{minutes // 1440}d ago"
