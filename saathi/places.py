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
        # Upstream sources of sudden floods that no rain or river forecast can see. Distances are
        # approximate river kilometres, to be checked with DHM before any real use.
        "upstream": [
            {"id": "chumchet", "name": "Chumchet / Tsum valley (landslide dams)", "kind": "landslide_dam", "km": 60},
            {"id": "manaslu-glacial", "name": "Manaslu headwaters near the Tibet border (glacial lakes)", "kind": "glacial_lake", "km": 90},
        ],
    },
    "narayanghat": {
        "name": "Narayanghat, Chitwan", "name_ne": "नारायणघाट, चितवन", "lat": 27.70, "lon": 84.43,
        "river": "Narayani", "river_ne": "नारायणी",
        "safe_places": ["Bharatpur hospital area (away from the river bank)", "Ward office and schools on the east side of the highway"],
        "context": "Low-lying settlements by the Narayani flood in most monsoons; the river rises over hours, not minutes.",
        "upstream": [
            {"id": "budhi-gandaki", "name": "Budhi Gandaki (landslide dams, glacial lakes), via Trishuli", "kind": "landslide_dam", "km": 140},
            {"id": "kali-gandaki", "name": "Kali Gandaki headwaters (landslide dams)", "kind": "landslide_dam", "km": 220},
        ],
    },
    "chatara": {
        "name": "Chatara, Sunsari", "name_ne": "चतरा, सुनसरी", "lat": 26.87, "lon": 87.16,
        "river": "Koshi", "river_ne": "कोशी",
        "safe_places": ["Embankment road towards Barahakshetra (higher ground)", "Chatara school and temple grounds above the bank"],
        "context": "Koshi barrage area; embankment breaches in 2008 displaced tens of thousands.",
        "upstream": [
            {"id": "bhote-koshi", "name": "Bhote Koshi / Sun Koshi from Tibet (glacial lakes)", "kind": "glacial_lake", "km": 250},
            {"id": "arun", "name": "Arun from Tibet (glacial lakes, landslide dams)", "kind": "glacial_lake", "km": 180},
        ],
    },
}

# What people can see and hear before a sudden flood arrives. Taught so nobody waits for an SMS.
WARNING_SIGNS = {
    "en": [
        "The river suddenly drops or dries up: it may be blocked upstream and can burst.",
        "A loud roar or rumbling from upstream.",
        "The water turns muddy all at once and carries logs and rocks.",
        "The water rises fast, in minutes.",
    ],
    "ne": [
        "नदी अचानक घट्यो वा सुक्यो: माथि नदी थुनिएको हुन सक्छ र फुट्न सक्छ।",
        "माथितिरबाट ठूलो गड्याङगुडुङ आवाज आयो।",
        "पानी एक्कासि धमिलो भयो, काठ र ढुङ्गा बगेर आउन थाले।",
        "पानी केही मिनेटमै छिटो बढ्न थाल्यो।",
    ],
}
ACT_ON_SIGNS = {
    "en": "If you see any of these, go to high ground at once. Do not wait for an SMS.",
    "ne": "यीमध्ये कुनै संकेत देखे तुरुन्तै अग्लो ठाउँमा जानुहोस्। SMS को प्रतीक्षा नगर्नुहोस्।",
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
