import streamlit as st


@st.cache_data
def fetch_satellite_alerts() -> list[dict]:
    return [
        {
            "id": "IGN-2024-001",
            "severity": "critical",
            "region": "Serra da Canastra",
            "municipality": "Vargem Bonita",
            "state": "MG",
            "lat": -20.322,
            "lon": -46.851,
            "detected_at_minutes": 125,
            "confidence": 0.94,
            "fire_area_ha": 847.0,
            "wind_speed": 45,
            "wind_direction": "SE",
            "satellite_source": "GOES-16",
            "recommended_action": "issue_evacuation",
            "recommended_action_label": "Issue evacuation order for Vargem Bonita and Delfinópolis",
            "ai_rationale": (
                "Fire front advancing at 380 m/h toward residential zone in Vargem Bonita. "
                "Wind SE at 45 km/h will push flames toward 3 populated sectors within 4 hours. "
                "Fuel moisture index: critical (8%). No natural firebreak between current "
                "perimeter and municipality."
            ),
            "status": "pending",
            "action_taken": None,
        },
        {
            "id": "IGN-2024-002",
            "severity": "critical",
            "region": "Parque Nacional do Araguaia",
            "municipality": "Luciara",
            "state": "MT",
            "lat": -11.217,
            "lon": -50.682,
            "detected_at_minutes": 48,
            "confidence": 0.91,
            "fire_area_ha": 2340.0,
            "wind_speed": 38,
            "wind_direction": "NW",
            "satellite_source": "VIIRS",
            "recommended_action": "dispatch_air",
            "recommended_action_label": "Dispatch aerial support and ground rapid-response teams",
            "ai_rationale": (
                "Multi-front fire across 2,340 ha with active canopy burn in the protected Araguaia "
                "corridor. Ground access compromised — BR-158 intersection at risk of being cut off. "
                "Aerial water-bomber deployment within 90 minutes is the viable containment window."
            ),
            "status": "pending",
            "action_taken": None,
        },
        {
            "id": "IGN-2024-003",
            "severity": "warning",
            "region": "Chapada Diamantina",
            "municipality": "Ibicoara",
            "state": "BA",
            "lat": -13.398,
            "lon": -41.283,
            "detected_at_minutes": 247,
            "confidence": 0.82,
            "fire_area_ha": 312.0,
            "wind_speed": 22,
            "wind_direction": "NE",
            "satellite_source": "MODIS",
            "recommended_action": "dispatch_ground",
            "recommended_action_label": "Dispatch ground teams and close access roads",
            "ai_rationale": (
                "Active hotspot cluster near tourist infrastructure in Chapada Diamantina National Park. "
                "Low wind speed reduces spread risk, but terrain complexity will impede suppression if "
                "delayed beyond 6 hours. Ground teams reach perimeter from Mucugê base in under 3 hours."
            ),
            "status": "pending",
            "action_taken": None,
        },
        {
            "id": "IGN-2024-004",
            "severity": "caution",
            "region": "Pantanal Sul",
            "municipality": "Corumbá",
            "state": "MS",
            "lat": -19.124,
            "lon": -57.583,
            "detected_at_minutes": 63,
            "confidence": 0.67,
            "fire_area_ha": 0.0,
            "wind_speed": 28,
            "wind_direction": "SW",
            "satellite_source": "GOES-16",
            "recommended_action": "increase_surveillance",
            "recommended_action_label": "Increase surveillance to 15-minute intervals",
            "ai_rationale": (
                "No active combustion detected, but thermal anomaly pattern matches pre-ignition "
                "conditions. Area recorded zero rainfall in 42 days. NDVI index at seasonal minimum. "
                "Wind shift to SW expected at 17:00 local — opens risk window."
            ),
            "status": "pending",
            "action_taken": None,
        },
        {
            "id": "IGN-2024-005",
            "severity": "warning",
            "region": "Cerrado Norte",
            "municipality": "Niquelândia",
            "state": "GO",
            "lat": -14.929,
            "lon": -48.216,
            "detected_at_minutes": 180,
            "confidence": 0.76,
            "fire_area_ha": 158.0,
            "wind_speed": 31,
            "wind_direction": "E",
            "satellite_source": "VIIRS",
            "recommended_action": "dispatch_ground",
            "recommended_action_label": "Dispatch ground teams for verification and containment",
            "ai_rationale": (
                "VIIRS detection in a known agricultural transition zone — fire origin may be a controlled "
                "burn. Area is adjacent to private reserve boundary. Ground verification confirms whether "
                "containment is already in progress or emergency response is required."
            ),
            "status": "pending",
            "action_taken": None,
        },
    ]
