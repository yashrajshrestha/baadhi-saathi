"""Pilot places: where the household is, which river matters, and where to go.

Three pilot wards for the first version, chosen for the 2026 floods and for having well-known
higher ground. Safe places are *examples to be confirmed with the ward office*; the agent says so.
Emergency numbers: 1149 is Nepal's National Emergency Operation Center; 100 police; 102 ambulance.
"""
from __future__ import annotations

PLACES = {
    "arughat": {
        "name": "Arughat, Gorkha", "name_ne": "आरुघाट, गोरखा", "lat": 28.04, "lon": 84.82,
        "river": "Budhi Gandaki", "river_ne": "बुढी गण्डकी",
        "safe_places": ["Higher ground above the bazaar towards the health post", "Arughat school building (upper floor)"],
        "context": "Budhi Gandaki flash flood on 11 Oct 2026 from a landslide-dam breach upstream; bridges and homes lost.",
    },
    "narayanghat": {
        "name": "Narayanghat, Chitwan", "name_ne": "नारायणघाट, चितवन", "lat": 27.70, "lon": 84.43,
        "river": "Narayani", "river_ne": "नारायणी",
        "safe_places": ["Bharatpur hospital area (away from the river bank)", "Ward office and schools on the east side of the highway"],
        "context": "Low-lying settlements by the Narayani flood in most monsoons; the river rises over hours, not minutes.",
    },
    "chatara": {
        "name": "Chatara, Sunsari", "name_ne": "चतरा, सुनसरी", "lat": 26.87, "lon": 87.16,
        "river": "Koshi", "river_ne": "कोशी",
        "safe_places": ["Embankment road towards Barahakshetra (higher ground)", "Chatara school and temple grounds above the bank"],
        "context": "Koshi barrage area; embankment breaches in 2008 displaced tens of thousands.",
    },
}

EMERGENCY = {"NEOC (disaster)": "1149", "Police": "100", "Ambulance": "102"}


def find(query: str) -> dict | None:
    q = query.strip().lower()
    for key, p in PLACES.items():
        if q in (key, p["name"].lower(), p["name_ne"]) or q in p["name"].lower():
            return {"key": key, **p}
    return None


def listing() -> list[str]:
    return [f"{p['name']} ({p['river']})" for p in PLACES.values()]
