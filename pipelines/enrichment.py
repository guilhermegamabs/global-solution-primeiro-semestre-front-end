from __future__ import annotations

def enrichWithWeather(alerts: list[dict], weather: dict) -> list[dict]:
    for a in alerts:
        wx = weather.get(a.get("state"), {})
        a["weather"] = wx

        wind = wx.get("wind_kmh", 0)
        hum = wx.get("humidity_pct", 50)
        rain = wx.get("rain_mm_24h", 0)
        score = (
            min(wind / 60.0, 1.0) * 0.45
            + (1.0 - min(hum / 100.0, 1.0)) * 0.35
            - min(rain / 20.0, 1.0) * 0.30
        )
        a["spread_risk_24h"] = max(0.0, min(1.0, score))
    return alerts


def aggregateByState(alerts: list[dict]) -> dict[str, dict]:
    sev_order = {"critical": 3, "warning": 2, "caution": 1, "info": 0}
    by_state: dict[str, dict] = {}
    for a in alerts:
        s = a.get("state", "??")
        cur = by_state.setdefault(
            s, {"count": 0, "max_sev": "info", "total_area_ha": 0.0}
        )
        cur["count"] += 1
        cur["total_area_ha"] += float(a.get("fire_area_ha", 0.0))
        if sev_order.get(a.get("severity", "info"), 0) > sev_order.get(cur["max_sev"], 0):
            cur["max_sev"] = a["severity"]
    return by_state
