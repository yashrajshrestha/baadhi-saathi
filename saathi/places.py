"""Pilot places: where the household is, which river matters, and where to go.

Three pilot wards for the first version, chosen for the 2026 floods and for having well-known
higher ground. Safe places are *examples to be confirmed with the ward office*; the agent says so.
Emergency numbers: 1149 is Nepal's National Emergency Operation Center; 100 police; 102 ambulance.
"""
from __future__ import annotations

import re

PLACES = {
    "arughat": {
        "name": "Arughat, Gorkha", "name_ne": "आरुघाट, गोरखा", "lat": 28.04, "lon": 84.82,
        # The GloFAS cell on the river itself, checked on a map of the grid. The automatic scan picked a
        # bigger river 20 km away here, so every pilot place pins its cell.
        "river_cell": (28.025, 84.775),
        "river": "Budhi Gandaki", "river_ne": "बुढी गण्डकी",
        "safe_places": ["Higher ground above the bazaar towards the health post", "Arughat school building (upper floor)"],
        "safe_places_ne": ["बजारभन्दा माथि स्वास्थ्य चौकीतिरको अग्लो ठाउँ", "आरुघाट विद्यालय भवन (माथिल्लो तला)"],
        # Words that name a safe place; advice under a warning must contain one, so "go somewhere high" is not enough.
        "landmarks": ["health post", "school", "स्वास्थ्य चौकी", "विद्यालय"],
        "context": "Budhi Gandaki flash flood on 11 Oct 2026 from a landslide-dam breach upstream; bridges and homes lost.",
        # Upstream sources of sudden floods that no rain or river forecast can see. Distances are
        # approximate river kilometres, to be checked with DHM before any real use.
        "upstream": [
            {"id": "chumchet", "name": "Chumchet / Tsum valley (landslide dams)", "kind": "landslide_dam", "km": 60, "words": ["chumchet", "tsum", "चुम्चेट", "छुम्चेत", "त्सुम"]},
            {"id": "manaslu-glacial", "name": "Manaslu headwaters near the Tibet border (glacial lakes)", "kind": "glacial_lake", "km": 90, "words": ["manaslu", "tibet", "मनास्लु", "तिब्बत"]},
        ],
    },
    "narayanghat": {
        "name": "Narayanghat, Chitwan", "name_ne": "नारायणघाट, चितवन", "lat": 27.70, "lon": 84.43,
        "river_cell": (27.675, 84.275),
        "river": "Narayani", "river_ne": "नारायणी",
        "safe_places": ["Bharatpur hospital area (away from the river bank)", "Ward office and schools on the east side of the highway"],
        "safe_places_ne": ["भरतपुर अस्पताल क्षेत्र (नदी किनारबाट टाढा)", "राजमार्गको पूर्वपट्टिको वडा कार्यालय र विद्यालयहरू"],
        "landmarks": ["hospital", "ward office", "school", "अस्पताल", "वडा कार्यालय", "विद्यालय"],
        "context": "Low-lying settlements by the Narayani flood in most monsoons; the river rises over hours, not minutes.",
        "upstream": [
            {"id": "budhi-gandaki", "name": "Budhi Gandaki (landslide dams, glacial lakes), via Trishuli", "kind": "landslide_dam", "km": 140, "words": ["budhi gandaki", "बूढीगण्डकी", "बुढीगण्डकी", "बूढी गण्डकी", "बुढी गण्डकी"]},
            {"id": "kali-gandaki", "name": "Kali Gandaki headwaters (landslide dams)", "kind": "landslide_dam", "km": 220, "words": ["kali gandaki", "कालीगण्डकी", "काली गण्डकी"]},
        ],
    },
    "chatara": {
        "name": "Chatara, Sunsari", "name_ne": "चतरा, सुनसरी", "lat": 26.87, "lon": 87.16,
        "river_cell": (26.725, 87.025),
        "river": "Koshi", "river_ne": "कोशी",
        "safe_places": ["Embankment road towards Barahakshetra (higher ground)", "Chatara school and temple grounds above the bank"],
        "safe_places_ne": ["वराहक्षेत्रतर्फको तटबन्ध सडक (अग्लो ठाउँ)", "किनारभन्दा माथिको चतरा विद्यालय र मन्दिर परिसर"],
        "landmarks": ["embankment", "barahakshetra", "school", "temple", "तटबन्ध", "वराहक्षेत्र", "विद्यालय", "मन्दिर"],
        "context": "Koshi barrage area; embankment breaches in 2008 displaced tens of thousands.",
        "upstream": [
            {"id": "bhote-koshi", "name": "Bhote Koshi / Sun Koshi from Tibet (glacial lakes)", "kind": "glacial_lake", "km": 250, "words": ["bhote koshi", "sun koshi", "tibet", "भोटेकोशी", "भोटे कोशी", "सुनकोशी", "सुन कोशी", "तिब्बत"]},
            {"id": "arun", "name": "Arun from Tibet (glacial lakes, landslide dams)", "kind": "glacial_lake", "km": 180, "words": ["arun", "tibet", "अरुण", "तिब्बत"]},
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
    """A pilot place by key or name, in either script; tolerant of "(river)" suffixes and extra words, because
    a model copies names from listing() and once looped twelve times on "Chatara, Sunsari (Koshi)"."""
    q = re.sub(r"\(.*?\)", "", query).strip().strip(",. ").lower()
    for key, p in PLACES.items():
        town, town_ne = p["name"].split(",")[0].lower(), p["name_ne"].split(",")[0]
        if q in (key, p["name"].lower(), p["name_ne"]) or (q and q in p["name"].lower()) or town in q or town_ne in q:
            return {"key": key, **p}
    return None


def listing() -> list[str]:
    return [f"{p['name']} ({p['river']})" for p in PLACES.values()]
