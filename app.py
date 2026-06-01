import streamlit as st
from ui.styles import inject_styles
from state.alerts_state import init_state, get_pending_alerts, count_pending
from features.alerts import render_alert_panel
from features.map_view import render_map_view
from features.analytics import render_analytics
from ui.components import render_severity_badge, render_sidebar_alert_summary

st.set_page_config(
    page_title="IGNIS — Wildfire Command",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

if "initialized" not in st.session_state:
    with st.spinner("Synchronizing satellite feeds..."):
        init_state()
    st.session_state.initialized = True
else:
    init_state()

with st.sidebar:
    st.markdown(
        '<div class="ignis-wordmark" style="margin-bottom:18px;display:block;">IGNIS</div>',
        unsafe_allow_html=True,
    )

    pending_alerts = get_pending_alerts()
    n_pending = count_pending()

    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        "font-size:9px;text-transform:uppercase;letter-spacing:0.10em;"
        'color:oklch(0.38 0.005 353);margin-bottom:8px;">Active alerts</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        render_sidebar_alert_summary(pending_alerts),
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        "font-size:9px;text-transform:uppercase;letter-spacing:0.10em;"
        'color:oklch(0.38 0.005 353);margin-bottom:4px;">Navigation</p>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "page",
        options=["Alert queue", "Map view", "Analytics"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown(
        '<p style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        "font-size:10px;color:oklch(0.35 0.005 353);line-height:1.8;"
        '">'
        "Last sync: 2 min ago<br>"
        "Sources: GOES-16 · VIIRS · MODIS<br>"
        "Coverage: Brazil<br>"
        f'Pending: <strong style="color:oklch(0.88 0.005 353);">{n_pending}</strong>'
        "</p>",
        unsafe_allow_html=True,
    )

if page == "Alert queue":
    render_alert_panel()

elif page == "Map view":
    render_map_view()

elif page == "Analytics":
    render_analytics()
