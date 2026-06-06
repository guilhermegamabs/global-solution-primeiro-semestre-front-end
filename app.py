import streamlit as st
from ui.styles import injectStyles
from state.alerts_state import initState, getPendingAlerts, countPending
from features.briefing import renderBriefing
from features.alerts import renderAlertPanel
from features.map_view import renderMapView
from features.analytics import renderAnalytics
from ui.components import renderSidebarAlertSummary

st.set_page_config(
    page_title="IGNIS — Wildfire Command",
    layout="wide",
    initial_sidebar_state="expanded",
)

injectStyles()

if "initialized" not in st.session_state:
    with st.spinner("Synchronizing satellite feeds..."):
        initState()
    st.session_state.initialized = True
else:
    initState()

with st.sidebar:
    st.markdown(
        '<div class="ignis-wordmark ignis-wordmark--block">IGNIS</div>',
        unsafe_allow_html=True,
    )

    pending_alerts = getPendingAlerts()
    n_pending = countPending()

    st.markdown(
        '<p class="ignis-sidebar-label">Active alerts</p>',
        unsafe_allow_html=True,
    )
    st.markdown(renderSidebarAlertSummary(pending_alerts), unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(
        '<p class="ignis-sidebar-label ignis-sidebar-label--nav">Navigation</p>',
        unsafe_allow_html=True,
    )
    page = st.radio(
        "page",
        options=["Briefing", "Alert queue", "Map view", "Analytics"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown(
        '<p class="ignis-sidebar-footer">'
        "Last sync: 2 min ago<br>"
        "Sources: GOES-16 · VIIRS · MODIS<br>"
        "Coverage: Brazil<br>"
        f"Pending: <strong>{n_pending}</strong>"
        "</p>",
        unsafe_allow_html=True,
    )

if page == "Briefing":
    renderBriefing()
elif page == "Alert queue":
    renderAlertPanel()
elif page == "Map view":
    renderMapView()
elif page == "Analytics":
    renderAnalytics()
