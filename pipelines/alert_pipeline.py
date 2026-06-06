_SEVERITY_ORDER = {"critical": 0, "warning": 1, "caution": 2, "info": 3, "safe": 4}


def applyFilters(
    alerts,
    states,
    severities,
    min_confidence,
    show,
    ):

    result = alerts
    if states:
        result = [a for a in result if a.get("state") in states]
    if severities:
        result = [a for a in result if a.get("severity") in severities]
    if min_confidence > 0:
        result = [a for a in result if a.get("confidence", 0) >= min_confidence]
    if show == "pending":
        result = [a for a in result if a.get("status") == "pending"]
    elif show == "resolved":
        result = [a for a in result if a.get("status") != "pending"]
    return result


def processAlerts(raw_alerts):
    return sorted(
        raw_alerts,
        key=lambda a: (
            _SEVERITY_ORDER.get(a.get("severity", "info"), 99),
            -a.get("confidence", 0.0),
        ),
    )

def filterBySeverity(alerts, levels):
    return [a for a in alerts if a.get("severity") in levels]


def filterPending(alerts):
    return [a for a in alerts if a.get("status") == "pending"]


def filterResolved(alerts):
    return [a for a in alerts if a.get("status") != "pending"]
