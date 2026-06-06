import streamlit as st

from pipelines.enrichment import aggregateByState
from state.alerts_state import getAllAlerts, getPendingAlerts
from ui.components import renderSeverityBadge


def renderBriefing() -> None:
    alerts = getAllAlerts()
    pending = getPendingAlerts()

    st.markdown(
        '<div class="ignis-header">'
        '<span class="ignis-wordmark">IGNIS</span>'
        '<span class="ignis-header__caption">Operational briefing</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="ignis-section-label">National picture — last 24h</div>',
        unsafe_allow_html=True,
    )

    total = len(alerts)
    n_pending = len(pending)
    n_critical = sum(1 for a in alerts if a.get("severity") == "critical")
    total_ha = sum(a.get("fire_area_ha", 0) for a in alerts)
    avg_ml = (
        sum(a.get("ml_risk_score", 0) for a in pending) / max(len(pending), 1)
        if pending else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Total events", str(total))
    kpi(c2, "Pending", str(n_pending), critical=n_pending > 0)
    kpi(c3, "Critical", str(n_critical), critical=n_critical > 0)
    kpi(c4, "Burning area", f"{total_ha:,.0f} ha")
    kpi(c5, "Mean ML risk", f"{avg_ml*100:.0f}%")

    st.markdown('<div class="ignis-spacer-lg"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="ignis-section-label">By state — fire load × weather forecast</div>',
        unsafe_allow_html=True,
    )

    by_state = aggregateByState(alerts)

    rows = []
    for state, agg in by_state.items():
        st_alerts = [a for a in alerts if a.get("state") == state]
        spread = (
            sum(a.get("spread_risk_24h", 0) for a in st_alerts) / max(len(st_alerts), 1)
            if st_alerts else 0
        )
        wx = st_alerts[0].get("weather", {}) if st_alerts else {}
        rows.append((state, agg, spread, wx))
    rows.sort(key=lambda r: -r[2])

    for state, agg, spread, wx in rows:
        stateRow(state, agg, spread, wx)

    st.markdown('<div class="ignis-spacer-xl"></div>', unsafe_allow_html=True)

    if n_pending > 0:
        st.markdown(
            f'<div class="ignis-next-action">'
            f'<div class="ignis-next-action__title">Next action</div>'
            f'<div class="ignis-next-action__body">'
            f"<strong>{n_pending}</strong> event{'s' if n_pending != 1 else ''} "
            f"awaiting decision. Mean ML urgency: "
            f"<strong>{avg_ml*100:.0f}%</strong>. "
            f"Open <strong>Alert queue</strong> to triage."
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.success("All events resolved. National picture stable.")

def kpi(col, label: str, value: str, critical: bool = False) -> None:
    value_cls = "ignis-kpi__value ignis-kpi__value--critical" if critical else "ignis-kpi__value"
    col.markdown(
        f'<div class="ignis-kpi">'
        f'<div class="ignis-kpi__label">{label}</div>'
        f'<div class="{value_cls}">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def stateRow(state: str, agg: dict, spread: float, wx: dict) -> None:
    badge = renderSeverityBadge(agg["max_sev"])
    wind = wx.get("wind_kmh", 0)
    hum = wx.get("humidity_pct", 0)
    rain = wx.get("rain_mm_24h", 0)
    if spread >= 0.65:
        chip_var = "var(--ignis-critical-strong)"
    elif spread >= 0.40:
        chip_var = "var(--ignis-warning)"
    else:
        chip_var = "var(--ignis-safe)"
    st.markdown(
        f'<div class="ignis-state-row">'
        f'<span class="ignis-state-row__code">{state}</span>'
        f'{badge}'
        f'<span class="ignis-state-row__meta">{agg["count"]} event(s) · {agg["total_area_ha"]:,.0f} ha</span>'
        f'<span class="ignis-state-row__right">'
        f'<span class="ignis-state-row__weather">wind {wind} km/h · hum {hum}% · rain {rain:.1f} mm</span>'
        f'<span class="ignis-chip" style="--chip-color:{chip_var};">spread {spread*100:.0f}%</span>'
        f'</span></div>',
        unsafe_allow_html=True,
    )
