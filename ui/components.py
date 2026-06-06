from collections import Counter
from typing import Literal

SeverityLevel = Literal["critical", "warning", "caution", "safe", "info"]

_SEVERITY_LABELS = {
    "critical": "CRITICAL",
    "warning":  "WARNING",
    "caution":  "CAUTION",
    "safe":     "CLEAR",
    "info":     "INFO",
}

_SEVERITY_VAR = {
    "critical": "var(--ignis-critical)",
    "warning":  "var(--ignis-warning)",
    "caution":  "var(--ignis-caution)",
    "safe":     "var(--ignis-safe)",
    "info":     "var(--ignis-brand)",
}


def renderSeverityBadge(level: SeverityLevel, label: str | None = None) -> str:
    display = label or _SEVERITY_LABELS.get(level, "INFO")
    cls = level if level in _SEVERITY_LABELS else "info"
    return f'<span class="ignis-badge ignis-badge--{cls}">{display}</span>'


def renderConfidenceBar(confidence: float, severity: SeverityLevel) -> str:
    pct = round(confidence * 100)
    color = _SEVERITY_VAR.get(severity, _SEVERITY_VAR["info"])
    return (
        f'<span class="ignis-conf" style="--conf-color:{color};">'
        f'<span class="ignis-conf__track">'
        f'<span class="ignis-conf__fill" style="width:{pct}%;"></span>'
        f'</span>'
        f'<span class="ignis-conf__pct">{pct}%</span>'
        f'</span>'
    )


def renderSidebarAlertSummary(pending_alerts: list[dict]) -> str:
    if not pending_alerts:
        return '<span class="ignis-sidebar-summary__empty">No active alerts</span>'

    counts = Counter(a["severity"] for a in pending_alerts)
    parts: list[str] = []
    for level in ("critical", "warning", "caution", "info"):
        n = counts.get(level, 0)
        if not n:
            continue
        badge = renderSeverityBadge(level)
        parts.append(
            f'<span class="ignis-sidebar-summary__row">{badge}'
            f'<span class="ignis-sidebar-summary__count">{n}</span></span>'
        )
    return f'<div class="ignis-sidebar-summary">{"".join(parts)}</div>'
