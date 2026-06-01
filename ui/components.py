from collections import Counter
from typing import Literal

SeverityLevel = Literal["critical", "warning", "caution", "safe", "info"]

_SEVERITY_CONFIG: dict[str, dict] = {
    "critical": {
        "bg": "oklch(0.55 0.230 22)",
        "text": "oklch(0.97 0.000 0)",
        "label": "CRITICAL",
    },
    "warning": {
        "bg": "oklch(0.67 0.210 42)",
        "text": "oklch(0.97 0.000 0)",
        "label": "WARNING",
    },
    "caution": {
        "bg": "oklch(0.75 0.170 75)",
        "text": "oklch(0.10 0.000 0)",
        "label": "CAUTION",
    },
    "safe": {
        "bg": "oklch(0.70 0.180 145)",
        "text": "oklch(0.10 0.000 0)",
        "label": "CLEAR",
    },
    "info": {
        "bg": "oklch(0.65 0.140 230)",
        "text": "oklch(0.97 0.000 0)",
        "label": "INFO",
    },
}


def render_severity_badge(level: SeverityLevel, label: str | None = None) -> str:
    cfg = _SEVERITY_CONFIG.get(level, _SEVERITY_CONFIG["info"])
    display = label or cfg["label"]
    bg = cfg["bg"]
    color = cfg["text"]
    return (
        f'<span style="'
        f"display:inline-block;"
        f"padding:2px 9px;"
        f"border-radius:4px;"
        f"background:{bg};"
        f"color:{color};"
        f"font-size:10px;"
        f"font-weight:700;"
        f"letter-spacing:0.07em;"
        f"font-family:'JetBrains Mono','Courier New',monospace;"
        f"text-transform:uppercase;"
        f'white-space:nowrap;"'
        f">{display}</span>"
    )


def render_confidence_bar(confidence: float, severity: SeverityLevel) -> str:
    cfg = _SEVERITY_CONFIG.get(severity, _SEVERITY_CONFIG["info"])
    pct = round(confidence * 100)
    fill_color = cfg["bg"]
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;vertical-align:middle;">'
        f'<span style="width:44px;height:3px;background:oklch(0.25 0.003 353);'
        f'border-radius:2px;display:inline-block;overflow:hidden;">'
        f'<span style="display:block;height:100%;width:{pct}%;background:{fill_color};border-radius:2px;"></span>'
        f'</span>'
        f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
        f'font-size:11px;color:oklch(0.80 0.005 353);font-weight:500;">{pct}%</span>'
        f'</span>'
    )


def render_sidebar_alert_summary(pending_alerts: list[dict]) -> str:
    if not pending_alerts:
        return (
            '<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
            'font-size:12px;color:oklch(0.55 0.008 353);">No active alerts</span>'
        )

    counts = Counter(a["severity"] for a in pending_alerts)
    parts: list[str] = []
    for level in ("critical", "warning", "caution", "info"):
        n = counts.get(level, 0)
        if n:
            badge = render_severity_badge(level)
            parts.append(
                f'<span style="display:inline-flex;align-items:center;gap:7px;margin-bottom:6px;">'
                f'{badge}'
                f'<span style="font-family:\'JetBrains Mono\',\'Courier New\',monospace;'
                f'font-size:14px;color:oklch(0.85 0.005 353);font-weight:600;">{n}</span>'
                f'</span>'
            )

    return '<div style="display:flex;flex-direction:column;">' + "".join(parts) + "</div>"
