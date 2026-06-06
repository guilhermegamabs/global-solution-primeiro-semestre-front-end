import random
import streamlit as st
from datetime import datetime, timedelta

@st.cache_data
def fetchFireTimeseries() -> dict:
    rng = random.Random(20260501)

    base = datetime(2026, 5, 2)
    dates = [base + timedelta(days=i) for i in range(30)]

    def dayFactor(i: int) -> float:
        if i < 10:
            return 1.0 + (i / 10) * 0.4
        elif i < 22:
            return 1.4 + (i - 10) / 12 * 0.9
        else:
            return 2.3 + (i - 22) / 8 * 2.2

    critical_counts: list[int] = []
    warning_counts: list[int] = []
    caution_counts: list[int] = []
    critical_area_ha: list[int] = []
    warning_area_ha: list[int] = []

    for i, d in enumerate(dates):
        f = dayFactor(i)
        wf = 0.82 if d.weekday() in (5, 6) else 1.0

        c  = max(0, round(rng.gauss(0.6 * f, 0.35) * wf))
        w  = max(0, round(rng.gauss(1.6 * f, 0.55) * wf))
        ca = max(0, round(rng.gauss(2.8 * f, 0.85) * wf))

        critical_counts.append(c)
        warning_counts.append(w)
        caution_counts.append(ca)
        critical_area_ha.append(c * rng.randint(250, 1600))
        warning_area_ha.append(w * rng.randint(60, 420))

    return {
        "dates": dates,
        "critical": critical_counts,
        "warning": warning_counts,
        "caution": caution_counts,
        "critical_area_ha": critical_area_ha,
        "warning_area_ha": warning_area_ha,
    }


@st.cache_data
def fetchStateImpact() -> dict:
    return {
        "states": ["MT", "PA", "MG", "GO", "BA", "MS", "TO", "AM", "RO", "MA"],
        "critical_ha": [4200, 2800, 1900,  800,  600,  200, 1100, 3200, 1500,  900],
        "warning_ha": [1800,  900,  700, 1200,  400,  300,  600, 1400,  800,  500],
        "caution_ha": [ 600,  400,  300,  500,  200,  150,  300,  600,  400,  250],
    }


@st.cache_data
def fetchHourlyPattern() -> dict:
    rng = random.Random(42)
    base = [4, 3, 5, 6, 3, 2, 3, 5, 6, 7, 9, 10, 11, 18, 20, 16, 12, 9, 7, 6, 5, 4, 4, 3]
    return {
        "hours": list(range(24)),
        "counts": [max(0, b + rng.randint(-1, 2)) for b in base],
    }
