import streamlit as st


@st.cache_data
def fetchWeatherForecast():
    return {
        "MG": {"wind_kmh": 42, "humidity_pct": 28, "rain_mm_24h": 0.0, "risk_index": 0.88},
        "MT": {"wind_kmh": 35, "humidity_pct": 32, "rain_mm_24h": 0.0, "risk_index": 0.82},
        "BA": {"wind_kmh": 24, "humidity_pct": 41, "rain_mm_24h": 1.2, "risk_index": 0.61},
        "MS": {"wind_kmh": 29, "humidity_pct": 38, "rain_mm_24h": 0.5, "risk_index": 0.71},
        "GO": {"wind_kmh": 31, "humidity_pct": 35, "rain_mm_24h": 0.0, "risk_index": 0.74},
        "PA": {"wind_kmh": 18, "humidity_pct": 62, "rain_mm_24h": 8.5, "risk_index": 0.35},
        "TO": {"wind_kmh": 26, "humidity_pct": 44, "rain_mm_24h": 2.0, "risk_index": 0.58},
        "AM": {"wind_kmh": 14, "humidity_pct": 78, "rain_mm_24h": 14.0, "risk_index": 0.22},
        "RO": {"wind_kmh": 22, "humidity_pct": 55, "rain_mm_24h": 4.2, "risk_index": 0.48},
        "MA": {"wind_kmh": 27, "humidity_pct": 47, "rain_mm_24h": 1.8, "risk_index": 0.55},
    }

@st.cache_data
def getStateWeather(state):
    return fetchWeatherForecast().get(
        state,
        {"wind_kmh": 0, "humidity_pct": 50, "rain_mm_24h": 0.0, "risk_index": 0.5},
    )
