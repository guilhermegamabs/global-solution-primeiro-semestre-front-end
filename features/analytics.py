import datetime as dt

import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st

from providers.mock_timeseries import (
    fetch_fire_timeseries,
    fetch_state_impact,
    fetch_hourly_pattern,
)
from ui.components import render_severity_badge

_SEVERITY_HEX = {
    "critical": "#cc2418",
    "warning":  "#d97020",
    "caution":  "#c8b800",
}

_FILL = {
    "caution":  "rgba(200,184,  0,0.55)",
    "warning":  "rgba(217,112, 32,0.62)",
    "critical": "rgba(204, 36, 24,0.72)",
}

_SOURCE_SHARE = {"GOES-16": 0.60, "VIIRS": 0.25, "MODIS": 0.15}
_ALL_SOURCES = list(_SOURCE_SHARE)

_CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#161616",
    margin=dict(l=8, r=8, t=12, b=8),
    height=390,
    hoverlabel=dict(
        bgcolor="#282828",
        bordercolor="#c43055",
        font=dict(
            family="'JetBrains Mono','Courier New',monospace",
            size=12,
            color="#ededed",
        ),
    ),
    legend=dict(
        bgcolor="#1e1e1e",
        bordercolor="#333333",
        borderwidth=1,
        font=dict(
            family="'JetBrains Mono','Courier New',monospace",
            size=11,
            color="#ededed",
        ),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
)

_AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="#262626",
    gridwidth=1,
    tickfont=dict(
        family="'JetBrains Mono','Courier New',monospace",
        size=10,
        color="#777777",
    ),
)

_PLOTLY_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["select2d", "lasso2d"],
    "displaylogo": False,
}


def render_analytics() -> None:
    ts_raw = fetch_fire_timeseries()
    dates_all = ts_raw["dates"]
    d_min = dates_all[0].date()
    d_max = dates_all[-1].date()

    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2.6, 1.8, 1.8])

    with fc1:
        date_range = st.date_input(
            "Date range",
            value=(d_min, d_max),
            min_value=d_min,
            max_value=d_max,
            key="analytics_dates",
        )
    with fc2:
        sel_severities = st.multiselect(
            "Severity",
            options=["critical", "warning", "caution"],
            format_func=str.upper,
            default=[],
            placeholder="All levels",
            key="analytics_severities",
        )
    with fc3:
        sel_sources = st.multiselect(
            "Satellite source",
            options=_ALL_SOURCES,
            default=[],
            placeholder="All sources",
            key="analytics_sources",
        )

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        d_start, d_end = date_range
    else:
        d_start = d_end = (
            date_range if not isinstance(date_range, (list, tuple)) else date_range[0]
        )

    active_sevs = sel_severities or ["critical", "warning", "caution"]
    source_factor = (
        sum(_SOURCE_SHARE.get(s, 0) for s in sel_sources) if sel_sources else 1.0
    )

    mask = [d_start <= d.date() <= d_end for d in dates_all]
    filtered_dates = [d for d, m in zip(dates_all, mask) if m]
    filtered_ts: dict[str, list[int]] = {
        sev: [round(v * source_factor) for v, m in zip(ts_raw[sev], mask) if m]
        for sev in ("critical", "warning", "caution")
    }

    tab1, tab2, tab3 = st.tabs(["Fire activity", "Area impact", "Hourly pattern"])

    with tab1:
        _render_timeline(filtered_dates, filtered_ts, active_sevs)

    with tab2:
        _render_area_impact(active_sevs, source_factor)

    with tab3:
        _render_hourly(sel_sources)


def _render_timeline(
    dates: list,
    ts: dict[str, list[int]],
    active_sevs: list[str],
) -> None:
    if not dates:
        st.markdown(
            '<div class="ignis-empty">'
            '<div class="ignis-empty-icon">◎</div>'
            '<div class="ignis-empty-title">No data in range</div>'
            '<div class="ignis-empty-body">Adjust the date range to show fire activity.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    fig = go.Figure()

    for sev in ("caution", "warning", "critical"):
        if sev not in active_sevs:
            continue
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=ts[sev],
                name=sev.upper(),
                stackgroup="one",
                fillcolor=_FILL[sev],
                line=dict(color=_SEVERITY_HEX[sev], width=1.5),
                mode="lines",
                hovertemplate=(
                    f"<b>%{{x|%b %d}}</b><br>{sev.upper()}: %{{y}}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **_CHART_LAYOUT,
        xaxis=dict(
            **_AXIS_STYLE,
            tickformat="%b %d",
            tickangle=-35,
        ),
        yaxis=dict(
            **_AXIS_STYLE,
            title=dict(
                text="Detections / day",
                font=dict(size=11, color="#555555"),
            ),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CONFIG)

    total = sum(sum(ts[s]) for s in active_sevs if s in ts)
    st.markdown(
        f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'color:oklch(0.42 0.005 353);margin-top:2px;">'
        f'{total} detections in selected period'
        f'</p>',
        unsafe_allow_html=True,
    )


def _render_area_impact(active_sevs: list[str], source_factor: float) -> None:
    sd = fetch_state_impact()
    states = sd["states"]

    fig = go.Figure()

    for sev, key in (("caution", "caution_ha"), ("warning", "warning_ha"), ("critical", "critical_ha")):
        if sev not in active_sevs:
            continue
        values = [round(v * source_factor) for v in sd[key]]
        fig.add_trace(
            go.Bar(
                x=states,
                y=values,
                name=sev.upper(),
                marker_color=_FILL[sev],
                marker_line=dict(color=_SEVERITY_HEX[sev], width=1),
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{sev.upper()}: %{{y:,}} ha<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **_CHART_LAYOUT,
        barmode="stack",
        xaxis=dict(
            showgrid=False,
            tickfont=dict(
                family="'JetBrains Mono','Courier New',monospace",
                size=11,
                color="#777777",
            ),
        ),
        yaxis=dict(
            **_AXIS_STYLE,
            ticksuffix=" ha",
            title=dict(
                text="Area affected",
                font=dict(size=11, color="#555555"),
            ),
        ),
    )

    st.plotly_chart(fig, use_container_width=True, config=_PLOTLY_CONFIG)

    total_ha = sum(
        sum(round(v * source_factor) for v in sd[k])
        for sev, k in (("critical", "critical_ha"), ("warning", "warning_ha"), ("caution", "caution_ha"))
        if sev in active_sevs
    )
    st.markdown(
        f'<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'color:oklch(0.42 0.005 353);margin-top:2px;">'
        f'{total_ha:,} ha total across {len(sd["states"])} states in selected severity levels'
        f'</p>',
        unsafe_allow_html=True,
    )


def _render_hourly(sel_sources: list[str]) -> None:
    hourly = fetch_hourly_pattern()
    hours = hourly["hours"]
    counts = list(hourly["counts"])

    if sel_sources:
        factor = sum(_SOURCE_SHARE.get(s, 0) for s in sel_sources)
        counts = [max(0, round(c * factor)) for c in counts]

    fig, ax = plt.subplots(figsize=(10, 3.4))
    fig.patch.set_facecolor("#1a1a1a")
    ax.set_facecolor("#161616")

    bar_colors = [
        "#d97020" if (13 <= h <= 15 or 1 <= h <= 3) else "#3a3a3a"
        for h in hours
    ]
    ax.bar(hours, counts, color=bar_colors, alpha=0.90, width=0.75, zorder=3)

    ax.axvspan(12.5, 15.5, alpha=0.06, color="#d97020", zorder=1)
    ax.axvspan(0.5,  3.5,  alpha=0.06, color="#d97020", zorder=1)

    for spine in ax.spines.values():
        spine.set_color("#2a2a2a")
    ax.tick_params(colors="#555555", labelsize=8.5)
    ax.set_xticks(hours)
    ax.set_xticklabels([f"{h:02d}h" for h in hours], color="#555555", fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
    ax.set_xlabel("Hour (UTC)", color="#444444", fontsize=10, labelpad=6)
    ax.set_ylabel("Detections", color="#444444", fontsize=10, labelpad=6)
    ax.grid(axis="y", color="#242424", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    sources_label = ", ".join(sel_sources) if sel_sources else "All sources"
    ax.set_title(
        f"Detection frequency by hour of day (UTC) — {sources_label}",
        color="#666666",
        fontsize=10,
        pad=8,
    )

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        'color:oklch(0.40 0.005 353);margin-top:4px;line-height:1.6;">'
        'Peaks at 13-15 UTC and 01-03 UTC: VIIRS/MODIS polar overpass windows. '
        'GOES-16 provides continuous coverage across all hours.'
        '</p>',
        unsafe_allow_html=True,
    )
