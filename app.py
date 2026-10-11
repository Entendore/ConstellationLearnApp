#!/usr/bin/env python3
"""
Constellation Study App — Enhanced Edition v2.0
Features: External JSON databases (CWD), Settings dialog, Red Night Vision mode,
Tonight's Sky, multiple quiz types, constellation comparison, auto-advance flashcards,
export/import stats, user notes, random constellation, deep sky objects, and more.
"""

import sys, os, json, time, math, random, copy
import shiboken6
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QStackedWidget,
    QPushButton, QFrame, QScrollArea, QTextBrowser, QProgressBar,
    QGridLayout, QCheckBox, QSizePolicy, QComboBox, QDialog, QSpacerItem,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox, QTabWidget, QGroupBox,
    QSlider, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient,
    QLinearGradient, QIcon, QPixmap, QPainterPath, QKeySequence, QAction
)

# ============================================================
# PATHS — everything in CWD
# ============================================================
CWD = os.path.dirname(os.path.abspath(__file__))
CONSTELLATIONS_DB = os.path.join(CWD, "constellations.json")
STARS_DB = os.path.join(CWD, "stars.json")
SETTINGS_FILE = os.path.join(CWD, "settings.json")
STATS_FILE = os.path.join(CWD, "stats.json")
NOTES_FILE = os.path.join(CWD, "notes.json")

SEASONS = ["All", "Winter", "Spring", "Summer", "Autumn"]
HEMISPHERES = ["All", "Northern", "Southern", "Both"]

# ============================================================
# DATA LOADING
# ============================================================
def load_constellations():
    """Load constellations from external JSON, or fall back to built-in data."""
    if os.path.exists(CONSTELLATIONS_DB):
        try:
            with open(CONSTELLATIONS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Warning: Failed to load {CONSTELLATIONS_DB}: {e}")
    return BUILTIN_CONSTELLATIONS

def load_stars_db():
    """Load expanded stars database."""
    if os.path.exists(STARS_DB):
        try:
            with open(STARS_DB, "r", encoding="utf-8") as f:
                return json.load(f).get("stars", [])
        except Exception:
            pass
    return []

def load_settings():
    """Load settings from CWD."""
    defaults = {
        "animation_speed": 90, "bg_star_count": 350, "glow_intensity": 1.0,
        "show_star_names": True, "show_constellation_lines": True,
        "night_vision": False, "quiz_question_types": ["identify_constellation"],
        "matching_round_size": 6, "flashcard_auto_advance": False,
        "flashcard_auto_delay": 5.0, "theme": "Dark Blue",
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                s = json.load(f)
            defaults.update(s)
        except Exception:
            pass
    return defaults

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

def load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"quiz_history": [], "match_history": [], "flashcard_known": [], "flashcard_unknown": [], "favorites": []}

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

def load_notes():
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_notes(notes):
    try:
        with open(NOTES_FILE, "w") as f:
            json.dump(notes, f, indent=2)
    except Exception:
        pass

# ============================================================
# BUILT-IN FALLBACK CONSTELLATIONS (18 constellations, enriched)
# ============================================================
BUILTIN_CONSTELLATIONS = [
    {"name":"Orion","abbreviation":"Ori","season":"Winter","hemisphere":"Both","area":594,
     "description":"Orion is one of the most recognizable constellations, visible worldwide. Its distinctive three-star belt makes it easy to spot. Orion contains two first-magnitude stars: reddish Betelgeuse and blue-white Rigel.",
     "mythology":"In Greek mythology, Orion was a giant huntsman whom Zeus placed among the stars. He was killed by a scorpion (Scorpius), and both were set in the sky on opposite sides so they would never meet again.",
     "main_stars":"Betelgeuse (α) — Red supergiant, ~700× the Sun's diameter\nRigel (β) — Blue supergiant, ~120,000× the Sun's luminosity\nBellatrix (γ), Mintaka (δ), Alnilam (ε), Alnitak (ζ), Saiph (κ)",
     "best_viewing":"December – February","months":[12,1,2],
     "deep_sky_objects":[{"name":"Orion Nebula (M42)","type":"Emission Nebula","description":"One of the brightest nebulae, visible to the naked eye."},{"name":"Horsehead Nebula","type":"Dark Nebula","description":"A dark dust cloud silhouetted against IC 434."}],
     "relationships":["Taurus","Gemini","Canis Major","Eridanus","Lepus"],
     "stars":[{"name":"Betelgeuse","x":0.30,"y":0.12,"mag":0.5,"color":"#FF6644"},{"name":"Bellatrix","x":0.70,"y":0.15,"mag":1.6,"color":"#AACCFF"},
              {"name":"Mintaka","x":0.43,"y":0.42,"mag":2.2,"color":"#AACCFF"},{"name":"Alnilam","x":0.50,"y":0.45,"mag":1.7,"color":"#AACCFF"},
              {"name":"Alnitak","x":0.57,"y":0.48,"mag":1.8,"color":"#AACCFF"},{"name":"Saiph","x":0.33,"y":0.88,"mag":2.1,"color":"#AACCFF"},
              {"name":"Rigel","x":0.72,"y":0.85,"mag":0.1,"color":"#AACCFF"}],
     "lines":[[0,1],[0,2],[1,4],[2,3],[3,4],[2,5],[4,6]]},
    {"name":"Ursa Major","abbreviation":"UMa","season":"Spring","hemisphere":"Northern","area":1280,
     "description":"Ursa Major contains the famous Big Dipper asterism, one of the most useful navigational tools in the sky. The two 'pointer stars' Dubhe and Merak lead directly to Polaris.",
     "mythology":"In Greek myth, Zeus transformed the nymph Callisto into a bear. He placed her in the sky as Ursa Major. The handle represents her long tail.",
     "main_stars":"Dubhe (α) — Orange giant, 123 light-years\nMerak (β) — White main-sequence, pointer star\nPhecda (γ), Megrez (δ), Alioth (ε), Mizar (ζ), Alkaid (η)",
     "best_viewing":"March – June","months":[3,4,5,6],
     "deep_sky_objects":[{"name":"M81 (Bode's Galaxy)","type":"Spiral Galaxy","description":"A grand design spiral ~12 million ly away."},{"name":"M82 (Cigar Galaxy)","type":"Irregular Galaxy","description":"A starburst galaxy near M81."}],
     "relationships":["Ursa Minor","Leo","Canes Venatici","Boötes","Draco"],
     "stars":[{"name":"Alkaid","x":0.08,"y":0.42,"mag":1.9,"color":"#AACCFF"},{"name":"Mizar","x":0.22,"y":0.33,"mag":2.2,"color":"#FFFFFF"},
              {"name":"Alioth","x":0.38,"y":0.24,"mag":1.8,"color":"#FFFFFF"},{"name":"Megrez","x":0.52,"y":0.30,"mag":3.3,"color":"#FFFFFF"},
              {"name":"Dubhe","x":0.70,"y":0.22,"mag":1.8,"color":"#FFBB66"},{"name":"Merak","x":0.67,"y":0.48,"mag":2.4,"color":"#AACCFF"},
              {"name":"Phecda","x":0.52,"y":0.52,"mag":2.4,"color":"#FFFFFF"}],
     "lines":[[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,3]]},
    {"name":"Cassiopeia","abbreviation":"Cas","season":"Autumn","hemisphere":"Northern","area":598,
     "description":"Cassiopeia's distinctive W shape makes it one of the easiest constellations to identify. It is circumpolar from most northern latitudes.",
     "mythology":"Queen Cassiopeia boasted that she and her daughter were more beautiful than the sea nymphs. Poseidon punished her by chaining Andromeda.",
     "main_stars":"Schedar (α) — Orange giant, 228 light-years\nCaph (β) — White giant, variable star\nγ Cas — Eruptive variable\nRuchbah (δ), Segin (ε)",
     "best_viewing":"October – December","months":[10,11,12],
     "deep_sky_objects":[{"name":"NGC 457 (Owl Cluster)","type":"Open Cluster","description":"A bright cluster resembling an owl."},{"name":"M52","type":"Open Cluster","description":"A rich cluster of ~200 stars."}],
     "relationships":["Andromeda","Perseus","Cepheus","Lacerta"],
     "stars":[{"name":"Caph","x":0.10,"y":0.55,"mag":2.3,"color":"#FFFFEE"},{"name":"Schedar","x":0.28,"y":0.22,"mag":2.2,"color":"#FFBB66"},
              {"name":"γ Cas","x":0.50,"y":0.58,"mag":2.5,"color":"#AACCFF"},{"name":"Ruchbah","x":0.72,"y":0.20,"mag":2.7,"color":"#FFFFFF"},
              {"name":"Segin","x":0.90,"y":0.52,"mag":3.4,"color":"#AACCFF"}],
     "lines":[[0,1],[1,2],[2,3],[3,4]]},
    {"name":"Leo","abbreviation":"Leo","season":"Spring","hemisphere":"Both","area":947,
     "description":"Leo represents a lion, best identified by the 'Sickle' asterism — a backward question mark forming the lion's head. Regulus marks the lion's heart.",
     "mythology":"Leo represents the Nemean Lion slain by Heracles as the first of his twelve labors. The lion had an impenetrable hide.",
     "main_stars":"Regulus (α) — Blue-white, 79 light-years\nDenebola (β) — White main-sequence\nAlgieba (γ) — Beautiful double star\nZosma (δ), Chertan (θ)",
     "best_viewing":"March – May","months":[3,4,5],
     "deep_sky_objects":[{"name":"Leo Triplet","type":"Galaxy Group","description":"M65, M66, NGC 3628 — ~35 million ly away."},{"name":"M95","type":"Barred Spiral","description":"A barred spiral with a bright inner ring."}],
     "relationships":["Virgo","Cancer","Sextans","Hydra","Coma Berenices"],
     "stars":[{"name":"Regulus","x":0.12,"y":0.80,"mag":1.4,"color":"#AACCFF"},{"name":"η Leo","x":0.08,"y":0.60,"mag":3.5,"color":"#FFFFEE"},
              {"name":"Algieba","x":0.18,"y":0.45,"mag":2.6,"color":"#FFBB66"},{"name":"Adhafera","x":0.28,"y":0.28,"mag":3.4,"color":"#FFFFEE"},
              {"name":"Ras Elased","x":0.40,"y":0.15,"mag":3.0,"color":"#FFBB66"},{"name":"Zosma","x":0.62,"y":0.35,"mag":2.6,"color":"#FFFFFF"},
              {"name":"Denebola","x":0.85,"y":0.30,"mag":2.1,"color":"#FFFFFF"},{"name":"Chertan","x":0.55,"y":0.55,"mag":3.3,"color":"#FFFFFF"}],
     "lines":[[0,1],[1,2],[2,3],[3,4],[2,7],[4,5],[5,6],[6,7]]},
    {"name":"Scorpius","abbreviation":"Sco","season":"Summer","hemisphere":"Southern","area":497,
     "description":"Scorpius has a long, curving tail resembling a scorpion. Its red supergiant heart Antares rivals Mars in color — 'Rival of Mars'.",
     "mythology":"The scorpion was sent by Gaia to kill Orion. Both were placed on opposite sides of the sky — when Scorpius rises, Orion sets.",
     "main_stars":"Antares (α) — Red supergiant, ~680× Sun's diameter\nShaula (λ) — Blue subgiant, 'The Stinger'\nDschubba (δ), Graffias (β)",
     "best_viewing":"June – August","months":[6,7,8],
     "deep_sky_objects":[{"name":"M4","type":"Globular Cluster","description":"One of the nearest globular clusters, near Antares."},{"name":"M7 (Ptolemy Cluster)","type":"Open Cluster","description":"Bright cluster visible to the naked eye."}],
     "relationships":["Sagittarius","Libra","Ophiuchus","Lupus","Corona Australis"],
     "stars":[{"name":"Graffias","x":0.30,"y":0.05,"mag":2.6,"color":"#AACCFF"},{"name":"Dschubba","x":0.48,"y":0.08,"mag":2.3,"color":"#AACCFF"},
              {"name":"Pi Sco","x":0.58,"y":0.14,"mag":2.9,"color":"#AACCFF"},{"name":"Antares","x":0.44,"y":0.26,"mag":1.0,"color":"#FF6644"},
              {"name":"ε Sco","x":0.42,"y":0.40,"mag":2.3,"color":"#AACCFF"},{"name":"μ Sco","x":0.40,"y":0.54,"mag":3.0,"color":"#AACCFF"},
              {"name":"ζ Sco","x":0.36,"y":0.66,"mag":3.6,"color":"#AACCFF"},{"name":"η Sco","x":0.30,"y":0.76,"mag":3.3,"color":"#AACCFF"},
              {"name":"Sargas","x":0.24,"y":0.84,"mag":1.9,"color":"#FFFFEE"},{"name":"Shaula","x":0.14,"y":0.90,"mag":1.6,"color":"#AACCFF"},
              {"name":"Lesath","x":0.12,"y":0.94,"mag":2.7,"color":"#AACCFF"}],
     "lines":[[0,1],[1,2],[1,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,9],[9,10]]},
    {"name":"Cygnus","abbreviation":"Cyg","season":"Summer","hemisphere":"Northern","area":804,
     "description":"Cygnus, the Swan, flies along the Milky Way. Deneb forms one corner of the Summer Triangle. The Northern Cross asterism is very prominent.",
     "mythology":"Zeus disguised himself as a swan. Orpheus was transformed into a swan after death and placed next to his lyre.",
     "main_stars":"Deneb (α) — Blue-white supergiant\nSadr (γ) — Yellow-white supergiant\nAlbireo (β) — Famous gold-and-blue double\nGienah (ε), δ Cyg",
     "best_viewing":"June – October","months":[6,7,8,9,10],
     "deep_sky_objects":[{"name":"North America Nebula (NGC 7000)","type":"Emission Nebula","description":"Shaped like the North American continent."},{"name":"Veil Nebula","type":"Supernova Remnant","description":"Filamentary remnant of an exploded star."}],
     "relationships":["Lyra","Aquila","Pegasus","Lacerta","Draco"],
     "stars":[{"name":"Deneb","x":0.50,"y":0.08,"mag":1.3,"color":"#FFFFFF"},{"name":"Sadr","x":0.50,"y":0.42,"mag":2.2,"color":"#FFFFEE"},
              {"name":"Gienah","x":0.22,"y":0.55,"mag":2.5,"color":"#FFFFEE"},{"name":"δ Cyg","x":0.78,"y":0.38,"mag":2.9,"color":"#AACCFF"},
              {"name":"Albireo","x":0.50,"y":0.90,"mag":3.1,"color":"#FFBB66"}],
     "lines":[[0,1],[1,4],[2,1],[1,3]]},
    {"name":"Gemini","abbreviation":"Gem","season":"Winter","hemisphere":"Both","area":514,
     "description":"Gemini represents the twin brothers Castor and Pollux. Their heads are the two bright stars found northeast of Orion.",
     "mythology":"When mortal Castor died, immortal Pollux asked Zeus to share his immortality. Zeus placed them both in the sky together forever.",
     "main_stars":"Pollux (β) — Orange giant, 34 light-years\nCastor (α) — Sextuple star system, 51 ly\nAlhena (γ), Mebsuta (ε), Wasat (δ)",
     "best_viewing":"January – March","months":[1,2,3],
     "deep_sky_objects":[{"name":"M35","type":"Open Cluster","description":"A bright cluster of ~200 stars."},{"name":"NGC 2392 (Eskimo Nebula)","type":"Planetary Nebula","description":"A blue-green planetary nebula."}],
     "relationships":["Orion","Taurus","Auriga","Cancer","Canis Minor"],
     "stars":[{"name":"Castor","x":0.30,"y":0.08,"mag":1.6,"color":"#FFFFFF"},{"name":"Pollux","x":0.42,"y":0.12,"mag":1.1,"color":"#FFBB66"},
              {"name":"Mebsuta","x":0.28,"y":0.35,"mag":3.1,"color":"#FFFFEE"},{"name":"Wasat","x":0.48,"y":0.38,"mag":3.5,"color":"#FFFFEE"},
              {"name":"Mekbuda","x":0.52,"y":0.55,"mag":4.0,"color":"#FFFFEE"},{"name":"Alhena","x":0.62,"y":0.72,"mag":1.9,"color":"#FFFFFF"}],
     "lines":[[0,2],[2,3],[3,1],[3,4],[4,5]]},
    {"name":"Taurus","abbreviation":"Tau","season":"Winter","hemisphere":"Both","area":797,
     "description":"Taurus depicts a charging bull. The V-shaped Hyades form its face, Aldebaran marks its eye, and the Pleiades (M45) sit on its shoulder.",
     "mythology":"Zeus transformed into a white bull to abduct Europa. Another version says it is Io, transformed into a heifer by Hera.",
     "main_stars":"Aldebaran (α) — Orange giant, 65 light-years\nElnath (β) — Blue giant, 134 ly\nAlcyone (η Tau) — Brightest of the Pleiades",
     "best_viewing":"November – March","months":[11,12,1,2,3],
     "deep_sky_objects":[{"name":"M45 (Pleiades)","type":"Open Cluster","description":"The 'Seven Sisters' — stunning naked-eye cluster."},{"name":"Crab Nebula (M1)","type":"Supernova Remnant","description":"Remnant of the 1054 AD supernova. Contains a pulsar."}],
     "relationships":["Orion","Gemini","Auriga","Perseus","Aries","Cetus"],
     "stars":[{"name":"Elnath","x":0.82,"y":0.18,"mag":1.7,"color":"#AACCFF"},{"name":"ζ Tau","x":0.68,"y":0.30,"mag":3.0,"color":"#AACCFF"},
              {"name":"Aldebaran","x":0.38,"y":0.48,"mag":0.9,"color":"#FFBB66"},{"name":"Ain","x":0.32,"y":0.38,"mag":3.5,"color":"#FFFFEE"},
              {"name":"γ Tau","x":0.42,"y":0.58,"mag":3.7,"color":"#FFFFEE"},{"name":"δ Tau","x":0.28,"y":0.56,"mag":3.8,"color":"#FFFFEE"},
              {"name":"θ Tau","x":0.50,"y":0.70,"mag":3.4,"color":"#FFFFEE"}],
     "lines":[[3,2],[2,4],[4,5],[5,3],[2,1],[1,0],[4,6]]},
    {"name":"Canis Major","abbreviation":"CMa","season":"Winter","hemisphere":"Southern","area":380,
     "description":"Canis Major is dominated by Sirius — the brightest star in the entire night sky at magnitude −1.46. Represents one of Orion's hunting dogs.",
     "mythology":"Canis Major is one of Orion's hunting dogs. Zeus placed the dog in the sky to honor its loyalty.",
     "main_stars":"Sirius (α) — White main-sequence, 8.6 light-years, brightest star\nAdhara (ε) — Blue giant\nWezen (δ), Mirzam (β), Aludra (η)",
     "best_viewing":"December – February","months":[12,1,2],
     "deep_sky_objects":[{"name":"M41","type":"Open Cluster","description":"A bright cluster of ~100 stars, 4° south of Sirius."},{"name":"Thor's Helmet (NGC 2359)","type":"Emission Nebula","description":"A helmet-shaped nebula powered by a Wolf-Rayet star."}],
     "relationships":["Orion","Canis Minor","Monoceros","Puppis","Lepus"],
     "stars":[{"name":"Mirzam","x":0.15,"y":0.15,"mag":2.0,"color":"#AACCFF"},{"name":"Sirius","x":0.30,"y":0.35,"mag":-1.5,"color":"#FFFFFF"},
              {"name":"Muliphein","x":0.40,"y":0.22,"mag":4.0,"color":"#FFFFEE"},{"name":"Wezen","x":0.52,"y":0.52,"mag":1.8,"color":"#FFFFEE"},
              {"name":"Adhara","x":0.60,"y":0.68,"mag":1.5,"color":"#AACCFF"},{"name":"Furud","x":0.72,"y":0.52,"mag":3.0,"color":"#AACCFF"},
              {"name":"Aludra","x":0.80,"y":0.82,"mag":2.4,"color":"#AACCFF"}],
     "lines":[[0,2],[2,1],[1,3],[3,4],[4,6],[3,5]]},
    {"name":"Lyra","abbreviation":"Lyr","season":"Summer","hemisphere":"Northern","area":286,
     "description":"Lyra is a small but prominent constellation anchored by Vega, the fifth-brightest star and a corner of the Summer Triangle.",
     "mythology":"The lyre belonged to Orpheus, the greatest musician who ever lived. After his death, Zeus placed his lyre in the sky.",
     "main_stars":"Vega (α) — White main-sequence, 25 light-years\nSheliak (β) — Eclipsing binary prototype\nSulafat (γ), ε Lyr (quadruple star)",
     "best_viewing":"June – October","months":[6,7,8,9,10],
     "deep_sky_objects":[{"name":"M57 (Ring Nebula)","type":"Planetary Nebula","description":"Famous planetary nebula — a glowing smoke ring."},{"name":"M56","type":"Globular Cluster","description":"A compact globular cluster ~33,000 ly away."}],
     "relationships":["Cygnus","Hercules","Draco"],
     "stars":[{"name":"Vega","x":0.50,"y":0.10,"mag":0.0,"color":"#AACCFF"},{"name":"ε Lyr","x":0.38,"y":0.40,"mag":4.2,"color":"#FFFFFF"},
              {"name":"ζ Lyr","x":0.32,"y":0.55,"mag":4.3,"color":"#FFFFEE"},{"name":"Sheliak","x":0.42,"y":0.72,"mag":3.5,"color":"#FFFFFF"},
              {"name":"Sulafat","x":0.58,"y":0.68,"mag":3.2,"color":"#FFFFEE"},{"name":"δ Lyr","x":0.68,"y":0.50,"mag":4.3,"color":"#FFBB66"},
              {"name":"γ Lyr","x":0.62,"y":0.38,"mag":3.3,"color":"#FFFFFF"}],
     "lines":[[0,6],[0,1],[1,2],[2,3],[3,4],[4,5],[5,6]]},
    {"name":"Aquila","abbreviation":"Aql","season":"Summer","hemisphere":"Both","area":652,
     "description":"Aquila represents an eagle, best known for Altair — the third vertex of the Summer Triangle. Altair spins once every 8.9 hours.",
     "mythology":"The eagle carried Zeus's thunderbolts. It also carried Ganymede to Olympus to serve as cup-bearer.",
     "main_stars":"Altair (α) — White main-sequence, 16.7 light-years\nTarazed (γ) — Orange giant, 460 ly\nAlshain (β), δ Aql, λ Aql",
     "best_viewing":"June – October","months":[6,7,8,9,10],
     "deep_sky_objects":[{"name":"Dark Rift","type":"Dark Nebula","description":"Dense dust clouds splitting the Milky Way."}],
     "relationships":["Cygnus","Lyra","Sagittarius","Scutum","Serpens"],
     "stars":[{"name":"Tarazed","x":0.48,"y":0.28,"mag":2.7,"color":"#FFBB66"},{"name":"Altair","x":0.50,"y":0.45,"mag":0.8,"color":"#FFFFEE"},
              {"name":"Alshain","x":0.52,"y":0.60,"mag":3.7,"color":"#FFFFEE"},{"name":"δ Aql","x":0.25,"y":0.35,"mag":3.4,"color":"#FFFFEE"},
              {"name":"λ Aql","x":0.75,"y":0.55,"mag":3.4,"color":"#FFFFEE"},{"name":"θ Aql","x":0.30,"y":0.62,"mag":3.2,"color":"#FFFFEE"},
              {"name":"ζ Aql","x":0.70,"y":0.28,"mag":3.0,"color":"#FFFFEE"}],
     "lines":[[0,1],[1,2],[3,1],[1,4],[5,2],[0,6]]},
    {"name":"Pegasus","abbreviation":"Peg","season":"Autumn","hemisphere":"Northern","area":1121,
     "description":"Pegasus is dominated by the Great Square — four stars forming a large pattern. Alpheratz is shared with Andromeda.",
     "mythology":"Pegasus sprang from Medusa's blood. Bellerophon tamed it with a golden bridle and rode it to defeat the Chimera.",
     "main_stars":"Enif (ε) — Orange supergiant\nScheat (β) — Red giant, variable\nMarkab (α), Algenib (γ), Alpheratz (shared)",
     "best_viewing":"August – November","months":[8,9,10,11],
     "deep_sky_objects":[{"name":"M15","type":"Globular Cluster","description":"One of the oldest and densest globular clusters."},{"name":"Stephan's Quintet","type":"Galaxy Group","description":"A famous compact group of five galaxies."}],
     "relationships":["Andromeda","Pisces","Aquarius","Aries","Cetus","Cygnus"],
     "stars":[{"name":"Markab","x":0.25,"y":0.35,"mag":2.5,"color":"#AACCFF"},{"name":"Scheat","x":0.25,"y":0.62,"mag":2.4,"color":"#FFBB66"},
              {"name":"Algenib","x":0.55,"y":0.62,"mag":2.8,"color":"#AACCFF"},{"name":"Alpheratz","x":0.55,"y":0.35,"mag":2.1,"color":"#AACCFF"},
              {"name":"Homam","x":0.08,"y":0.30,"mag":3.4,"color":"#AACCFF"},{"name":"Matar","x":0.10,"y":0.58,"mag":2.9,"color":"#FFFFEE"},
              {"name":"Enif","x":0.82,"y":0.52,"mag":2.4,"color":"#FFBB66"}],
     "lines":[[0,1],[1,2],[2,3],[3,0],[4,0],[5,1],[2,6]]},
    {"name":"Andromeda","abbreviation":"And","season":"Autumn","hemisphere":"Northern","area":722,
     "description":"Andromeda contains M31 — the nearest large spiral galaxy at 2.5 million light-years, visible to the naked eye as a fuzzy patch.",
     "mythology":"Andromeda was chained to a rock as a sacrifice to Cetus but was rescued by Perseus, who later married her.",
     "main_stars":"Alpheratz (α) — Blue subgiant, shared with Pegasus\nMirach (β) — Red giant, 197 ly\nAlmach (γ) — Gold-and-blue double star",
     "best_viewing":"September – November","months":[9,10,11],
     "deep_sky_objects":[{"name":"M31 (Andromeda Galaxy)","type":"Spiral Galaxy","description":"Nearest large spiral at 2.537 million ly."},{"name":"M32","type":"Elliptical Galaxy","description":"Satellite galaxy of M31."},{"name":"M110","type":"Elliptical Galaxy","description":"Larger satellite of M31."}],
     "relationships":["Pegasus","Perseus","Cassiopeia","Lacerta","Pisces"],
     "stars":[{"name":"Alpheratz","x":0.10,"y":0.50,"mag":2.1,"color":"#AACCFF"},{"name":"δ And","x":0.25,"y":0.42,"mag":3.3,"color":"#FFFFEE"},
              {"name":"Mirach","x":0.42,"y":0.38,"mag":2.1,"color":"#FFBB66"},{"name":"Almach","x":0.70,"y":0.30,"mag":2.3,"color":"#FFBB66"},
              {"name":"μ And","x":0.32,"y":0.58,"mag":3.9,"color":"#FFFFEE"},{"name":"ν And","x":0.55,"y":0.50,"mag":4.5,"color":"#FFFFEE"}],
     "lines":[[0,1],[1,2],[2,3],[1,4],[2,5]]},
    {"name":"Sagittarius","abbreviation":"Sgr","season":"Summer","hemisphere":"Southern","area":867,
     "description":"Sagittarius points toward the center of our Milky Way. Its famous 'Teapot' asterism is easy to spot. Contains numerous nebulae and clusters.",
     "mythology":"Sagittarius represents a centaur drawing a bow, often identified as Chiron, the wisest centaur.",
     "main_stars":"Kaus Australis (ε) — Blue giant\nNunki (σ) — Blue main-sequence, 224 ly\nAscella (ζ), Kaus Media (δ)",
     "best_viewing":"June – September","months":[6,7,8,9],
     "deep_sky_objects":[{"name":"M8 (Lagoon Nebula)","type":"Emission Nebula","description":"Bright nebula visible to naked eye."},{"name":"M20 (Trifid Nebula)","type":"Emission Nebula","description":"Striking nebula divided into three lobes."},{"name":"M22","type":"Globular Cluster","description":"One of the finest globular clusters."}],
     "relationships":["Scorpius","Ophiuchus","Scutum","Serpens","Capricornus"],
     "stars":[{"name":"Kaus Borealis","x":0.38,"y":0.48,"mag":2.8,"color":"#FFBB66"},{"name":"φ Sgr","x":0.50,"y":0.42,"mag":3.2,"color":"#FFFFEE"},
              {"name":"Nunki","x":0.65,"y":0.45,"mag":2.0,"color":"#AACCFF"},{"name":"Ascella","x":0.72,"y":0.62,"mag":2.6,"color":"#AACCFF"},
              {"name":"Kaus Australis","x":0.55,"y":0.78,"mag":1.8,"color":"#AACCFF"},{"name":"Kaus Media","x":0.42,"y":0.62,"mag":2.7,"color":"#FFFFEE"},
              {"name":"ζ Sgr","x":0.58,"y":0.28,"mag":2.6,"color":"#AACCFF"},{"name":"τ Sgr","x":0.30,"y":0.38,"mag":3.3,"color":"#FFFFEE"},
              {"name":"σ Sgr","x":0.80,"y":0.48,"mag":2.1,"color":"#AACCFF"}],
     "lines":[[0,1],[1,2],[2,3],[3,4],[4,5],[5,0],[1,6],[2,8],[0,7]]},
    {"name":"Virgo","abbreviation":"Vir","season":"Spring","hemisphere":"Both","area":1294,
     "description":"Virgo is the second-largest constellation. Contains the Virgo Cluster of over 2,000 galaxies.",
     "mythology":"Virgo is associated with Demeter, goddess of agriculture. Its appearance in spring was linked to the growing season.",
     "main_stars":"Spica (α) — Blue giant binary, 250 light-years\nVindemiatrix (ε) — Yellow giant\nPorrima (γ), Auva (δ), Zavijava (β)",
     "best_viewing":"April – June","months":[4,5,6],
     "deep_sky_objects":[{"name":"Virgo Cluster","type":"Galaxy Cluster","description":"Over 2,000 galaxies ~53 million ly away."},{"name":"M87","type":"Elliptical Galaxy","description":"Supergiant elliptical with supermassive black hole."}],
     "relationships":["Leo","Coma Berenices","Boötes","Corvus","Hydra","Libra"],
     "stars":[{"name":"Zavijava","x":0.65,"y":0.20,"mag":3.6,"color":"#FFFFEE"},{"name":"Vindemiatrix","x":0.70,"y":0.35,"mag":2.8,"color":"#FFFFEE"},
              {"name":"Porrima","x":0.55,"y":0.48,"mag":2.7,"color":"#FFFFEE"},{"name":"Auva","x":0.38,"y":0.55,"mag":3.4,"color":"#FFBB66"},
              {"name":"Heze","x":0.55,"y":0.72,"mag":3.4,"color":"#AACCFF"},{"name":"Spica","x":0.45,"y":0.88,"mag":1.0,"color":"#AACCFF"}],
     "lines":[[0,1],[1,2],[2,3],[3,4],[4,5]]},
    {"name":"Boötes","abbreviation":"Boo","season":"Summer","hemisphere":"Northern","area":907,
     "description":"Boötes is dominated by Arcturus — the fourth-brightest star, a brilliant orange giant. Its kite shape is found by following the Big Dipper's handle arc.",
     "mythology":"Boötes is Icarius, taught winemaking by Dionysus. Shepherds thought he poisoned them and killed him.",
     "main_stars":"Arcturus (α) — Orange giant, 37 light-years\nIzar (ε) — Orange-and-blue double star\nMuphrid (η), Nekkar (β)",
     "best_viewing":"April – July","months":[4,5,6,7],
     "deep_sky_objects":[{"name":"Arcturus Stream","type":"Stellar Stream","description":"Remnant of a dwarf galaxy consumed by the Milky Way."}],
     "relationships":["Ursa Major","Canes Venatici","Virgo","Corona Borealis","Draco","Hercules"],
     "stars":[{"name":"Nekkar","x":0.35,"y":0.18,"mag":3.5,"color":"#FFFFEE"},{"name":"Seginus","x":0.62,"y":0.25,"mag":3.0,"color":"#AACCFF"},
              {"name":"Izar","x":0.38,"y":0.48,"mag":2.7,"color":"#FFBB66"},{"name":"Muphrid","x":0.52,"y":0.58,"mag":2.7,"color":"#FFFFEE"},
              {"name":"Arcturus","x":0.45,"y":0.82,"mag":-0.05,"color":"#FFBB66"}],
     "lines":[[0,2],[2,4],[4,3],[3,1],[1,0]]},
    {"name":"Perseus","abbreviation":"Per","season":"Autumn","hemisphere":"Northern","area":615,
     "description":"Perseus depicts the hero who slew Medusa. Contains Algol, the 'Demon Star', which dims dramatically every 2.87 days.",
     "mythology":"Perseus beheaded the Gorgon Medusa and used her head as a weapon. He rescued Andromeda from Cetus.",
     "main_stars":"Mirfak (α) — White supergiant, 510 ly\nAlgol (β) — Eclipsing binary, 'Demon Star'\nζ Per, ε Per",
     "best_viewing":"October – January","months":[10,11,12,1],
     "deep_sky_objects":[{"name":"Double Cluster","type":"Open Cluster","description":"Two spectacular adjacent clusters visible to naked eye."},{"name":"California Nebula (NGC 1499)","type":"Emission Nebula","description":"Large nebula shaped like California."}],
     "relationships":["Andromeda","Cassiopeia","Taurus","Aries"],
     "stars":[{"name":"Mirfak","x":0.38,"y":0.18,"mag":1.8,"color":"#FFFFEE"},{"name":"δ Per","x":0.30,"y":0.38,"mag":3.0,"color":"#AACCFF"},
              {"name":"Algol","x":0.48,"y":0.52,"mag":2.1,"color":"#AACCFF"},{"name":"ρ Per","x":0.58,"y":0.35,"mag":3.3,"color":"#FFBB66"},
              {"name":"ζ Per","x":0.22,"y":0.58,"mag":2.8,"color":"#AACCFF"},{"name":"ε Per","x":0.65,"y":0.65,"mag":2.9,"color":"#AACCFF"},
              {"name":"κ Per","x":0.42,"y":0.78,"mag":3.8,"color":"#FFFFEE"}],
     "lines":[[0,1],[1,4],[4,6],[0,3],[3,2],[2,5]]},
]

# ============================================================
# UTILITIES
# ============================================================
SPECTRAL_MAP = {"#FF6644": "Red (M/K)", "#FFBB66": "Orange (K/G)", "#FFFFEE": "Yellow-white (F/G)",
                "#AACCFF": "Blue-white (B/A)", "#FFFFFF": "White (A)"}

def make_star_icon(filled):
    pm = QPixmap(14, 14); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    color = QColor(255, 210, 60) if filled else QColor(50, 50, 90)
    p.setPen(Qt.NoPen); p.setBrush(color)
    path = QPainterPath()
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; r = 6 if i % 2 == 0 else 2.5
        x, y = 7 + r * math.cos(a), 7 + r * math.sin(a)
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    path.closeSubpath(); p.drawPath(path); p.end()
    return QIcon(pm)

# Lazy-initialized to avoid QPixmap-before-QApplication error
_STAR_ICON_CACHE = {}
def STAR_ICON_ON():
    if True not in _STAR_ICON_CACHE:
        _STAR_ICON_CACHE[True] = make_star_icon(True)
    return _STAR_ICON_CACHE[True]
def STAR_ICON_OFF():
    if False not in _STAR_ICON_CACHE:
        _STAR_ICON_CACHE[False] = make_star_icon(False)
    return _STAR_ICON_CACHE[False]

def current_month():
    return datetime.now().month

def get_tonight_constellations(constellations):
    """Return indices of constellations visible in the current month."""
    m = current_month()
    result = []
    for i, c in enumerate(constellations):
        months = c.get("months", [])
        if not months:
            # Fallback: map season to months
            smap = {"Winter": [12,1,2], "Spring": [3,4,5], "Summer": [6,7,8], "Autumn": [9,10,11]}
            months = smap.get(c["season"], list(range(1,13)))
        if m in months:
            result.append(i)
    return result

# ============================================================
# SHARED PAINTING FUNCTION
# ============================================================
def paint_constellation_stars(painter, rect, data, show_lines=True, show_names=False, glow_mult=1.0, night_vision=False):
    if data is None: return
    mx = rect.x() + rect.width() * 0.12
    my = rect.y() + rect.height() * 0.12
    dw, dh = rect.width() * 0.76, rect.height() * 0.76
    pts = [(mx + s["x"] * dw, my + s["y"] * dh) for s in data["stars"]]
    mini = rect.width() < 200

    if night_vision:
        line_col = QColor(80, 20, 20, 60 if mini else 70)
    else:
        line_col = QColor(70, 120, 220, 60 if mini else 70)

    if show_lines:
        painter.setPen(QPen(line_col, 1.2 if mini else 2.0))
        for i1, i2 in data.get("lines", []):
            painter.drawLine(QPointF(*pts[i1]), QPointF(*pts[i2]))

    for i, s in enumerate(data["stars"]):
        sx, sy = pts[i]
        sz = max(1.5, min(9.0, 7.5 - s["mag"] * 1.4)) * (0.65 if mini else 1.0)
        if night_vision:
            col = QColor(180, 60, 60)
        else:
            col = QColor(s["color"])
        painter.setPen(Qt.NoPen)
        g = QRadialGradient(sx, sy, sz * 4)
        g.setColorAt(0, QColor(col.red(), col.green(), col.blue(), int((90 if mini else 120) * glow_mult)))
        g.setColorAt(1, QColor(col.red(), col.green(), col.blue(), 0))
        painter.setBrush(g); painter.drawEllipse(QPointF(sx, sy), sz * 4, sz * 4)
        c = QRadialGradient(sx, sy, sz)
        if night_vision:
            c.setColorAt(0, QColor(255, 120, 120, 220))
            c.setColorAt(0.5, QColor(180, 60, 60, 180))
            c.setColorAt(1, QColor(100, 30, 30, 0))
        else:
            c.setColorAt(0, QColor(255, 255, 255, 220))
            c.setColorAt(0.5, QColor(col.red(), col.green(), col.blue(), 180))
            c.setColorAt(1, QColor(col.red(), col.green(), col.blue(), 0))
        painter.setBrush(c); painter.drawEllipse(QPointF(sx, sy), sz, sz)
        if show_names and not mini:
            tc = QColor(180, 60, 60) if night_vision else QColor(180, 190, 220, 190)
            painter.setPen(tc); painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QPointF(sx + sz + 5, sy + 4), s["name"])

# ============================================================
# DARK STYLESHEETS
# ============================================================
DARK_STYLE = """
QMainWindow,QWidget{background-color:#080818;color:#c0c8e0;font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;font-size:13px}
QListWidget{background-color:#0c0c28;border:1px solid #1a1a4a;border-radius:8px;padding:4px;outline:none}
QListWidget::item{padding:7px 10px;border-radius:5px;margin:1px 3px}
QListWidget::item:selected{background-color:#1a2a6a;color:#b0c0ff}
QListWidget::item:hover:!selected{background-color:#12123a}
QLineEdit{background-color:#0c0c28;border:1px solid #1a1a4a;border-radius:6px;padding:7px 11px;color:#c0c8e0}
QLineEdit:focus{border-color:#3858cc}
QPushButton{background-color:#12123a;border:1px solid #22226a;border-radius:6px;padding:7px 16px;color:#90a8ff;font-weight:bold}
QPushButton:hover{background-color:#1a2a6a;border-color:#3858cc;color:#b0c0ff}
QPushButton:pressed{background-color:#0a1a4a}
QPushButton:checked{background-color:#1a3080;border-color:#4878ff;color:#fff}
QPushButton:disabled{background-color:#0a0a20;color:#3a3a6a;border-color:#14143a}
QTextBrowser{background-color:#0c0c28;border:1px solid #1a1a4a;border-radius:8px;padding:14px;color:#c0c8e0}
QTextBrowser h2{color:#8098e0;font-size:16px;margin-top:10px}
QTextBrowser h3{color:#6878c0;font-size:14px;margin-top:8px}
QTextBrowser p{margin:3px 0;line-height:1.5}
QScrollBar:vertical{background:#080818;width:10px;border-radius:5px}
QScrollBar::handle:vertical{background:#2a2a5a;border-radius:5px;min-height:30px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
QProgressBar{background:#0c0c28;border:1px solid #1a1a4a;border-radius:5px;text-align:center;color:#90a8ff;height:22px;font-weight:bold}
QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1a40a0,stop:1 #3870e0);border-radius:4px}
QCheckBox{color:#90a8ff;spacing:7px;font-size:12px}
QCheckBox::indicator{width:17px;height:17px;border-radius:4px;border:1px solid #2a2a6a;background:#0c0c28}
QCheckBox::indicator:checked{background:#1a40a0;border-color:#4878ff}
QComboBox{background:#0c0c28;border:1px solid #1a1a4a;border-radius:6px;padding:5px 9px;color:#c0c8e0;min-width:80px}
QComboBox::drop-down{border:none;width:22px}
QComboBox QAbstractItemView{background:#0c0c28;border:1px solid #1a1a4a;color:#c0c8e0;selection-background-color:#1a2a6a}
QLabel{background:transparent}
QScrollArea{border:none}
QSlider::groove:horizontal{height:6px;background:#1a1a4a;border-radius:3px}
QSlider::handle:horizontal{background:#4878ff;width:16px;margin:-5px 0;border-radius:8px}
QSlider::sub-page:horizontal{background:#2850b0;border-radius:3px}
QTextEdit{background-color:#0c0c28;border:1px solid #1a1a4a;border-radius:6px;padding:7px;color:#c0c8e0}
QGroupBox{color:#8098e0;border:1px solid #1a1a4a;border-radius:8px;margin-top:12px;padding-top:14px;font-weight:bold}
QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px}
QTabWidget::pane{border:1px solid #1a1a4a;background:#0a0a20;border-radius:6px}
QTabBar::tab{background:#0c0c28;color:#6878a0;padding:8px 16px;border:1px solid #1a1a4a;border-bottom:none;border-top-left-radius:6px;border-top-right-radius:6px}
QTabBar::tab:selected{background:#0a0a20;color:#90a8ff}
QSpinBox,QDoubleSpinBox{background:#0c0c28;border:1px solid #1a1a4a;border-radius:6px;padding:4px 8px;color:#c0c8e0}
"""

NIGHT_STYLE = """
QMainWindow,QWidget{background-color:#1a0000;color:#ff8080;font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;font-size:13px}
QListWidget{background-color:#200000;border:1px solid #4a0000;border-radius:8px;padding:4px;outline:none}
QListWidget::item{padding:7px 10px;border-radius:5px;margin:1px 3px}
QListWidget::item:selected{background-color:#4a0000;color:#ffaaaa}
QListWidget::item:hover:!selected{background-color:#300000}
QLineEdit{background-color:#200000;border:1px solid #4a0000;border-radius:6px;padding:7px 11px;color:#ff8080}
QLineEdit:focus{border-color:#aa2020}
QPushButton{background-color:#300000;border:1px solid #6a0000;border-radius:6px;padding:7px 16px;color:#ff6666;font-weight:bold}
QPushButton:hover{background-color:#4a0000;border-color:#aa2020;color:#ffaaaa}
QPushButton:pressed{background-color:#2a0000}
QPushButton:checked{background-color:#600000;border-color:#ff4040;color:#fff}
QPushButton:disabled{background-color:#1a0000;color:#6a2020;border-color:#3a0000}
QTextBrowser{background-color:#200000;border:1px solid #4a0000;border-radius:8px;padding:14px;color:#ff8080}
QTextBrowser h2{color:#ff6666;font-size:16px;margin-top:10px}
QTextBrowser h3{color:#cc4040;font-size:14px;margin-top:8px}
QScrollBar:vertical{background:#1a0000;width:10px;border-radius:5px}
QScrollBar::handle:vertical{background:#5a0000;border-radius:5px;min-height:30px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
QProgressBar{background:#200000;border:1px solid #4a0000;border-radius:5px;text-align:center;color:#ff6666;height:22px;font-weight:bold}
QProgressBar::chunk{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6a0000,stop:1 #aa2020);border-radius:4px}
QCheckBox{color:#ff6666;spacing:7px;font-size:12px}
QCheckBox::indicator{width:17px;height:17px;border-radius:4px;border:1px solid #6a0000;background:#200000}
QCheckBox::indicator:checked{background:#6a0000;border-color:#ff4040}
QComboBox{background:#200000;border:1px solid #4a0000;border-radius:6px;padding:5px 9px;color:#ff8080;min-width:80px}
QComboBox::drop-down{border:none;width:22px}
QComboBox QAbstractItemView{background:#200000;border:1px solid #4a0000;color:#ff8080;selection-background-color:#4a0000}
QLabel{background:transparent}
QScrollArea{border:none}
QTextEdit{background-color:#200000;border:1px solid #4a0000;border-radius:6px;padding:7px;color:#ff8080}
QGroupBox{color:#ff6666;border:1px solid #4a0000;border-radius:8px;margin-top:12px;padding-top:14px;font-weight:bold}
QGroupBox::title{subcontrol-origin:margin;left:10px;padding:0 5px}
QSlider::groove:horizontal{height:6px;background:#4a0000;border-radius:3px}
QSlider::handle:horizontal{background:#ff4040;width:16px;margin:-5px 0;border-radius:8px}
QSlider::sub-page:horizontal{background:#aa2020;border-radius:3px}
QSpinBox,QDoubleSpinBox{background:#200000;border:1px solid #4a0000;border-radius:6px;padding:4px 8px;color:#ff8080}
"""# ============================================================
# STAR MAP WIDGET  (zoom, pan, hover, legend)
# ============================================================
class StarMapWidget(QWidget):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self._settings = settings or {}
        self.current = None
        self.show_names = True
        self.show_lines = True
        self.quiz_mode = False
        self.night_vision = False
        self.glow_mult = self._settings.get("glow_intensity", 1.0)
        self._zoom = 1.0
        self._ox = self._oy = 0.0
        self._dragging = False
        self._drag_sx = self._drag_sy = 0.0
        self._drag_ox = self._drag_oy = 0.0
        self._bg_stars = []
        n = self._settings.get("bg_star_count", 350)
        rng = random.Random(42)
        for _ in range(n):
            self._bg_stars.append((rng.random(), rng.random(), rng.uniform(0.4, 1.6),
                                   rng.randint(55, 210), rng.uniform(0, 6.28), rng.uniform(0.3, 1.4)))
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(self._settings.get("animation_speed", 90))
        self.setMinimumSize(280, 280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

    def set_constellation(self, data):
        self.current = data
        self._zoom = 1.0; self._ox = self._oy = 0.0
        self.update()

    def reset_view(self):
        self._zoom = 1.0; self._ox = self._oy = 0.0; self.update()

    def _star_screen(self, s):
        w, h = self.width(), self.height()
        dw, dh = w * 0.76, h * 0.76
        return ((s["x"] - 0.5) * self._zoom * dw + w / 2 + self._ox,
                (s["y"] - 0.5) * self._zoom * dh + h / 2 + self._oy)

    def _effective_rect(self):
        w, h = self.width(), self.height()
        dw, dh = w * 0.76, h * 0.76; z = self._zoom
        cx, cy = w / 2 + self._ox, h / 2 + self._oy
        hw, hh = dw * z / 2, dh * z / 2
        x0 = 0.5 - hw / dw; y0 = 0.5 - hh / dh
        x1 = 0.5 + hw / dw; y1 = 0.5 + hh / dh
        return QRectF(x0 * w * 0.76 + w * 0.12, y0 * h * 0.76 + h * 0.14,
                       (x1 - x0) * w * 0.76, (y1 - y0) * h * 0.76)

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self.night_vision:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0, QColor(15, 0, 0)); bg.setColorAt(0.4, QColor(25, 2, 2)); bg.setColorAt(1, QColor(15, 0, 0))
        else:
            bg = QLinearGradient(0, 0, 0, h)
            bg.setColorAt(0, QColor(4, 4, 22)); bg.setColorAt(0.4, QColor(8, 8, 38)); bg.setColorAt(1, QColor(4, 4, 18))
        p.fillRect(0, 0, w, h, bg)
        ms = int(time.time() * 1000)
        for (sx, sy, sz, sb, sp, sf) in self._bg_stars:
            b = int(sb + 35 * math.sin(2 * math.pi * sf * ms / 1000 + sp))
            b = max(25, min(235, b))
            if self.night_vision:
                p.setPen(Qt.NoPen); p.setBrush(QColor(120, 30, 30, b // 2))
            else:
                p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, b))
            p.drawEllipse(QPointF(sx * w, sy * h), sz, sz)
        if self.current:
            er = self._effective_rect()
            paint_constellation_stars(p, er, self.current, self.show_lines,
                                      self.show_names and not self.quiz_mode,
                                      self.glow_mult, self.night_vision)
            if not self.quiz_mode:
                self._draw_legend(p, w, h)
                tc = QColor(200, 100, 100) if self.night_vision else QColor(160, 180, 240, 200)
                p.setPen(tc); p.setFont(QFont("Segoe UI", 14, QFont.Bold))
                p.drawText(QRectF(0, h - 32, w, 28), Qt.AlignCenter,
                           f"{self.current['name']}  ({self.current['abbreviation']})")
                if abs(self._zoom - 1.0) > 0.05 or abs(self._ox) > 1 or abs(self._oy) > 1:
                    zc = QColor(120, 50, 50, 140) if self.night_vision else QColor(100, 120, 180, 140)
                    p.setPen(zc); p.setFont(QFont("Segoe UI", 9))
                    p.drawText(10, h - 40, f"Zoom: {self._zoom:.1f}x  |  Right-click to reset")
        else:
            pc = QColor(120, 40, 40, 180) if self.night_vision else QColor(80, 90, 140, 180)
            p.setPen(pc); p.setFont(QFont("Segoe UI", 14))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "Select a constellation to begin")
        p.end()

    def _draw_legend(self, p, w, h):
        lx, ly = w - 135, h - 130
        bc = QColor(20, 5, 5, 190) if self.night_vision else QColor(6, 6, 24, 190)
        p.setPen(Qt.NoPen); p.setBrush(bc); p.drawRoundedRect(lx, ly, 125, 95, 6, 6)
        tc = QColor(160, 60, 60) if self.night_vision else QColor(120, 140, 200)
        sc = QColor(120, 40, 40) if self.night_vision else QColor(110, 130, 190)
        p.setPen(tc); p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(lx + 8, ly + 13, "Magnitude Scale")
        for i, (mag, lab) in enumerate([(-1, "-1 (Sirius)"), (0, " 0 (Vega)"), (1, " 1"), (2, " 2"), (3, " 3+")]):
            y = ly + 28 + i * 13; sz = max(1.5, min(8, 7 - mag * 1.5))
            dc = QColor(220, 100, 100) if self.night_vision else QColor(220, 230, 255)
            p.setPen(Qt.NoPen); p.setBrush(dc); p.drawEllipse(QPointF(lx + 14, y), sz, sz)
            p.setPen(sc); p.setFont(QFont("Segoe UI", 7))
            p.drawText(lx + 28, y + 4, lab)

    def wheelEvent(self, e):
        if not self.current: return
        old = self._zoom; d = e.angleDelta().y()
        self._zoom = min(6.0, self._zoom * 1.2) if d > 0 else max(0.4, self._zoom / 1.2)
        f = self._zoom / old; mx, my = e.position().x(), e.position().y()
        self._ox = mx - (mx - self.width() / 2 - self._ox) * f - self.width() / 2
        self._oy = my - (my - self.height() / 2 - self._oy) * f - self.height() / 2
        self.update()

    def mousePressEvent(self, e):
        if e.button() in (Qt.LeftButton, Qt.MiddleButton):
            self._dragging = True
            self._drag_sx, self._drag_sy = e.position().x(), e.position().y()
            self._drag_ox, self._drag_oy = self._ox, self._oy
            self.setCursor(Qt.ClosedHandCursor)
        elif e.button() == Qt.RightButton:
            self.reset_view()

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._ox = self._drag_ox + e.position().x() - self._drag_sx
            self._oy = self._drag_oy + e.position().y() - self._drag_sy
            self.update()
        elif self.current and not self.quiz_mode:
            mx, my = e.position().x(), e.position().y()
            for s in self.current["stars"]:
                sx, sy = self._star_screen(s)
                if math.hypot(mx - sx, my - sy) < max(12, 9 - s["mag"] * 1.2) + 6:
                    self.setToolTip(f"<b>{s['name']}</b><br>Magnitude: {s['mag']:.1f}<br>Color: {SPECTRAL_MAP.get(s['color'], 'Unknown')}")
                    return
            self.setToolTip("")

    def mouseReleaseEvent(self, e):
        if self._dragging:
            self._dragging = False; self.setCursor(Qt.CrossCursor)

    def mouseDoubleClickEvent(self, e):
        self.reset_view()

# ============================================================
# MINI STAR MAP
# ============================================================
class MiniStarMap(QWidget):
    clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = None; self.show_lines = True; self.matched = False; self._wrong = False
        self._wt = QTimer(self); self._wt.setSingleShot(True); self._wt.timeout.connect(self._cw)
        self.setMinimumSize(100, 100); self.setCursor(Qt.PointingHandCursor)

    def set_constellation(self, d):
        self.data = d; self.update()

    def flash_wrong(self):
        self._wrong = True; self.update(); self._wt.start(450)

    def _cw(self):
        self._wrong = False; self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        if self.matched:
            p.fillRect(0, 0, w, h, QColor(10, 38, 20)); bc = QColor(30, 180, 80)
        elif self._wrong:
            p.fillRect(0, 0, w, h, QColor(50, 10, 10)); bc = QColor(200, 40, 40)
        else:
            p.fillRect(0, 0, w, h, QColor(6, 6, 24)); bc = QColor(30, 30, 80)
        p.setPen(QPen(bc, 1.5)); p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, w - 2, h - 2, 8, 8)
        if self.data:
            paint_constellation_stars(p, QRectF(6, 6, w - 12, h - 12), self.data, self.show_lines, False)
        if self.matched:
            p.setPen(QColor(40, 200, 80)); p.setFont(QFont("Segoe UI", 22, QFont.Bold))
            p.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "OK")
        p.end()

    def mousePressEvent(self, e):
        if not self.matched: self.clicked.emit()

# ============================================================
# INFO PANEL (enriched with deep sky objects, relationships, notes)
# ============================================================
class InfoPanel(QScrollArea):
    note_changed = Signal(str, str)  # constellation_name, note_text
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self._container = QWidget()
        self._lay = QVBoxLayout(self._container); self._lay.setContentsMargins(6, 6, 6, 6); self._lay.setSpacing(4)
        self.setWidget(self._container)
        self._current_name = None
        self._notes = {}
        self._note_edit = QTextEdit(); self._note_edit.setMaximumHeight(80)
        self._note_edit.setPlaceholderText("Add your notes here...")
        self._note_edit.textChanged.connect(self._on_note_changed)
        self._note_lbl = QLabel("My Notes"); self._note_lbl.setStyleSheet("color:#8098e0;font-weight:bold;font-size:13px;margin-top:8px")

    def _on_note_changed(self):
        if self._current_name:
            self._notes[self._current_name] = self._note_edit.toPlainText()
            self.note_changed.emit(self._current_name, self._note_edit.toPlainText())

    def set_notes(self, notes):
        self._notes = notes

    def show_constellation(self, data):
        # Clear old widgets (but NOT our persistent note widgets)
        _persistent = {self._note_lbl, self._note_edit}
        while self._lay.count():
            item = self._lay.takeAt(0)
            w = item.widget() if item.widget() else item.layout()
            if w is not None and w not in _persistent:
                w.deleteLater()
        if not data:
            lbl = QLabel("Select a constellation\nto view its details.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#556080;margin-top:60px;font-size:14px")
            self._lay.addWidget(lbl)
            self._current_name = None
            return
        self._current_name = data["name"]

        # Name + abbrev
        hdr = QLabel(f"{data['name']} ({data['abbreviation']})")
        hdr.setFont(QFont("Segoe UI", 16, QFont.Bold)); hdr.setStyleSheet("color:#8098e0")
        self._lay.addWidget(hdr)

        # Quick info
        info_html = f"""<table style="width:100%;font-size:12px;color:#7888b8">
        <tr><td><b>Season:</b></td><td>{data['season']}</td></tr>
        <tr><td><b>Hemisphere:</b></td><td>{data['hemisphere']}</td></tr>
        <tr><td><b>Area:</b></td><td>{data['area']} sq deg</td></tr>
        <tr><td><b>Best Viewing:</b></td><td>{data['best_viewing']}</td></tr>
        <tr><td><b>Stars:</b></td><td>{len(data['stars'])} charted</td></tr></table>"""
        tb = QTextBrowser(); tb.setFrameShape(QFrame.NoFrame); tb.setMaximumHeight(140)
        tb.setHtml(info_html); self._lay.addWidget(tb)

        # Description
        self._lay.addWidget(self._section_label("Description"))
        dl = QLabel(data["description"]); dl.setWordWrap(True)
        dl.setStyleSheet("color:#a0a8c8;font-size:12px"); self._lay.addWidget(dl)

        # Mythology
        self._lay.addWidget(self._section_label("Mythology"))
        ml = QLabel(data["mythology"]); ml.setWordWrap(True)
        ml.setStyleSheet("color:#a0a8c8;font-size:12px"); self._lay.addWidget(ml)

        # Main Stars
        self._lay.addWidget(self._section_label("Main Stars"))
        sl = QLabel(data["main_stars"]); sl.setWordWrap(True)
        sl.setStyleSheet("color:#a0a8c8;font-size:11px;white-space:pre-wrap"); self._lay.addWidget(sl)

        # Deep Sky Objects
        dso = data.get("deep_sky_objects", [])
        if dso:
            self._lay.addWidget(self._section_label("Deep Sky Objects"))
            for obj in dso:
                tb2 = QTextBrowser(); tb2.setFrameShape(QFrame.NoFrame); tb2.setMaximumHeight(80)
                tb2.setHtml(f"<b>{obj['name']}</b> <span style='color:#5868a0'>({obj['type']})</span>"
                           f"<p style='font-size:11px;color:#8898b8;margin:2px 0'>{obj['description']}</p>")
                self._lay.addWidget(tb2)

        # Relationships
        rels = data.get("relationships", [])
        if rels:
            self._lay.addWidget(self._section_label("Neighboring Constellations"))
            rl = QLabel(", ".join(rels)); rl.setWordWrap(True)
            rl.setStyleSheet("color:#6878b0;font-size:12px"); self._lay.addWidget(rl)

        # Cultural Knowledge
        cult = data.get("cultural_knowledge", "")
        if cult:
            self._lay.addWidget(self._section_label("Cultural Knowledge"))
            cl = QLabel(cult); cl.setWordWrap(True)
            cl.setStyleSheet("color:#a0a8c8;font-size:12px;line-height:1.5"); self._lay.addWidget(cl)

        # User Notes
        if self._note_lbl.parentWidget() is None:
            self._note_lbl.setParent(self._container)
        self._lay.addWidget(self._note_lbl)
        self._note_edit.blockSignals(True)
        self._note_edit.setPlainText(self._notes.get(data["name"], ""))
        self._note_edit.blockSignals(False)
        if self._note_edit.parentWidget() is None:
            self._note_edit.setParent(self._container)
        self._lay.addWidget(self._note_edit)
        self._lay.addStretch()

    def _section_label(self, text):
        lbl = QLabel(text); lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet("color:#6878c0;margin-top:10px"); return lbl

    def save_current_note(self):
        if self._current_name and not shiboken6.isDeleted(self._note_edit):
            self._notes[self._current_name] = self._note_edit.toPlainText()

# ============================================================
# ALL-SKY OVERVIEW (with Tonight's Sky highlight)
# ============================================================
class AllSkyOverview(QScrollArea):
    constellation_clicked = Signal(int)
    def __init__(self, parent=None, tonight_indices=None):
        super().__init__(parent)
        self._tonight = tonight_indices or []
        self.setWidgetResizable(True); self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        c = QWidget(); self._gl = QGridLayout(c)
        self._gl.setSpacing(6); self._gl.setContentsMargins(12, 12, 12, 12)
        self.setWidget(c)

    def build(self, constellations):
        # Clear
        while self._gl.count():
            w = self._gl.takeAt(0).widget()
            if w: w.deleteLater()
        col = row = 0
        for season in ["Winter", "Spring", "Summer", "Autumn"]:
            icon = "TONIGHT" if any(constellations[i]["season"] == season for i in self._tonight) else ""
            lbl_text = f"{season}  {'[Visible Now]' if icon else ''}"
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("color:#8098e0;font-weight:bold;font-size:13px")
            if icon:
                lbl.setStyleSheet("color:#40ff80;font-weight:bold;font-size:13px")
            self._gl.addWidget(lbl, row, 0, 1, 4); row += 1; col = 0
            for i, c in enumerate(constellations):
                if c["season"] != season: continue
                m = MiniStarMap(); m.set_constellation(c); m.show_lines = True
                if i in self._tonight:
                    m.setStyleSheet("border: 2px solid #20c060; border-radius: 10px;")
                idx = i; m.clicked.connect(lambda _, ii=idx: self.constellation_clicked.emit(ii))
                self._gl.addWidget(m, row, col)
                n = QLabel(c["name"]); n.setAlignment(Qt.AlignCenter)
                nc = "#40ff80" if i in self._tonight else "#7888b8"
                n.setStyleSheet(f"color:{nc};font-size:11px")
                self._gl.addWidget(n, row + 1, col); col += 1
                if col >= 4: col = 0; row += 2
            if col > 0: row += 2
            row += 1
        self._gl.setRowStretch(row, 1)

# ============================================================
# CONSTELLATION COMPARISON MODE
# ============================================================
class ComparisonMode(QWidget):
    def __init__(self, constellations, parent=None):
        super().__init__(parent)
        self._constellations = constellations
        lay = QVBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(6)

        hdr = QHBoxLayout()
        t = QLabel("Compare Constellations"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); hdr.addWidget(t); hdr.addStretch()
        lay.addLayout(hdr)

        sel = QHBoxLayout()
        sel.addWidget(QLabel("Left:"))
        self.cb_left = QComboBox(); sel.addWidget(self.cb_left, 1)
        sel.addWidget(QLabel("Right:"))
        self.cb_right = QComboBox(); sel.addWidget(self.cb_right, 1)
        for c in constellations:
            self.cb_left.addItem(f"{c['name']} ({c['abbreviation']})")
            self.cb_right.addItem(f"{c['name']} ({c['abbreviation']})")
        if len(constellations) > 1:
            self.cb_right.setCurrentIndex(1)
        self.cb_left.currentIndexChanged.connect(self._update)
        self.cb_right.currentIndexChanged.connect(self._update)
        lay.addLayout(sel)

        # Splitter with two star maps + info
        splitter = QSplitter(Qt.Horizontal)
        self.map_left = StarMapWidget()
        self.info_left = QTextBrowser(); self.info_left.setFrameShape(QFrame.NoFrame); self.info_left.setMaximumWidth(300)
        w_left = QWidget(); vl_left = QVBoxLayout(w_left); vl_left.setContentsMargins(0,0,0,0)
        vl_left.addWidget(self.map_left, 1); vl_left.addWidget(self.info_left)
        splitter.addWidget(w_left)

        self.map_right = StarMapWidget()
        self.info_right = QTextBrowser(); self.info_right.setFrameShape(QFrame.NoFrame); self.info_right.setMaximumWidth(300)
        w_right = QWidget(); vl_right = QVBoxLayout(w_right); vl_right.setContentsMargins(0,0,0,0)
        vl_right.addWidget(self.map_right, 1); vl_right.addWidget(self.info_right)
        splitter.addWidget(w_right)
        splitter.setSizes([600, 600])
        lay.addWidget(splitter, 1)
        self._update()

    def _update(self):
        li = self.cb_left.currentIndex(); ri = self.cb_right.currentIndex()
        if li < 0 or ri < 0: return
        cl = self._constellations[li]; cr = self._constellations[ri]
        self.map_left.set_constellation(cl); self.map_right.set_constellation(cr)
        self._show_info(self.info_left, cl)
        self._show_info(self.info_right, cr)

    def _show_info(self, tb, c):
        dso_html = ""
        for obj in c.get("deep_sky_objects", []):
            dso_html += f"<li><b>{obj['name']}</b> ({obj['type']}) — {obj['description']}</li>"
        dso_html = f"<ul>{dso_html}</ul>" if dso_html else "<p style='color:#556080'>None listed</p>"
        tb.setHtml(f"""
        <h2>{c['name']} ({c['abbreviation']})</h2>
        <p>Season: <b>{c['season']}</b> | Hemisphere: <b>{c['hemisphere']}</b></p>
        <p>Area: <b>{c['area']} sq deg</b> | Stars charted: <b>{len(c['stars'])}</b></p>
        <p>Best Viewing: <b>{c['best_viewing']}</b></p>
        <h3>Deep Sky Objects</h3>{dso_html}
        <h3>Neighbors</h3><p>{', '.join(c.get('relationships', []))}</p>""")

    def set_night_vision(self, on):
        self.map_left.night_vision = on; self.map_right.night_vision = on
        self.map_left.update(); self.map_right.update()

# ============================================================
# STUDY MODE (with notes, tonight's sky, random button)
# ============================================================
class StudyMode(QWidget):
    def __init__(self, constellations, stats, notes, settings, parent=None):
        super().__init__(parent)
        self._constellations = constellations
        self._stats = stats; self._notes = notes; self._settings = settings
        self._favorites = set(stats.get("favorites", []))
        self._in_detail = False
        lay = QHBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(6)

        # Sidebar
        sb = QWidget(); sb.setFixedWidth(240)
        sl = QVBoxLayout(sb); sl.setContentsMargins(0, 0, 0, 0); sl.setSpacing(5)
        t = QLabel("Constellations"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0;padding:4px 0"); sl.addWidget(t)

        self.search = QLineEdit(); self.search.setPlaceholderText("Search stars & names...")
        self.search.textChanged.connect(self._filter); sl.addWidget(self.search)

        hf = QHBoxLayout()
        self.season_cb = QComboBox(); self.season_cb.addItems(SEASONS)
        self.season_cb.currentTextChanged.connect(self._filter); hf.addWidget(self.season_cb)
        self.hemi_cb = QComboBox(); self.hemi_cb.addItems(HEMISPHERES)
        self.hemi_cb.currentTextChanged.connect(self._filter); hf.addWidget(self.hemi_cb)
        sl.addLayout(hf)

        self.fav_chk = QCheckBox("Favorites only")
        self.fav_chk.toggled.connect(self._filter); sl.addWidget(self.fav_chk)

        self.tonight_chk = QCheckBox("Tonight's Sky")
        self.tonight_chk.toggled.connect(self._filter); sl.addWidget(self.tonight_chk)

        self.lst = QListWidget(); self.lst.currentRowChanged.connect(self._on_select)
        sl.addWidget(self.lst, 1)

        # Random button
        self.btn_random = QPushButton("Random Constellation")
        self.btn_random.clicked.connect(self._random_constellation); sl.addWidget(self.btn_random)

        self.chk_names = QCheckBox("Star names"); self.chk_names.setChecked(self._settings.get("show_star_names", True))
        self.chk_names.toggled.connect(self._on_names_toggle)
        sl.addWidget(self.chk_names)
        self.chk_lines = QCheckBox("Constellation lines"); self.chk_lines.setChecked(self._settings.get("show_constellation_lines", True))
        self.chk_lines.toggled.connect(self._on_lines_toggle)
        sl.addWidget(self.chk_lines)
        lay.addWidget(sb)

        # Center stack
        self.center_stack = QStackedWidget()
        self.overview = AllSkyOverview(tonight_indices=get_tonight_constellations(constellations))
        self.overview.constellation_clicked.connect(self._go_to_constellation)
        self.center_stack.addWidget(self.overview)

        detail_w = QWidget(); dl = QHBoxLayout(); dl.setContentsMargins(0, 0, 0, 0); dl.setSpacing(6)
        self.star_map = StarMapWidget(settings=settings)
        self.star_map.show_names = self.chk_names.isChecked()
        self.star_map.show_lines = self.chk_lines.isChecked()
        dl.addWidget(self.star_map, 1)

        self.info = InfoPanel()
        self.info.set_notes(notes)
        self.info.note_changed.connect(self._on_note_changed)
        self.info.setFixedWidth(320)
        dl.addWidget(self.info)

        self.btn_back = QPushButton("<-  Overview"); self.btn_back.setFixedHeight(30)
        self.btn_back.clicked.connect(self._go_overview)
        dl_top = QHBoxLayout(); dl_top.addWidget(self.btn_back); dl_top.addStretch()
        dv = QVBoxLayout(); dv.addLayout(dl_top); dv.addLayout(dl, 1)
        detail_w.setLayout(dv)
        self.center_stack.addWidget(detail_w)
        lay.addWidget(self.center_stack, 1)
        self.info.show_constellation(None)
        self._filter()

    def _on_names_toggle(self, v):
        self._settings["show_star_names"] = v
        self.star_map.show_names = v

    def _on_lines_toggle(self, v):
        self._settings["show_constellation_lines"] = v
        self.star_map.show_lines = v

    def _on_note_changed(self, name, text):
        self._notes[name] = text

    def _filter(self):
        txt = self.search.text().lower().strip()
        season = self.season_cb.currentText(); hemi = self.hemi_cb.currentText()
        fav = self.fav_chk.isChecked(); tonight = self.tonight_chk.isChecked()
        tonight_set = set(get_tonight_constellations(self._constellations))
        self.lst.blockSignals(True); self.lst.clear()
        for i, c in enumerate(self._constellations):
            if season != "All" and c["season"] != season: continue
            if hemi != "All" and c["hemisphere"] != hemi: continue
            if fav and i not in self._favorites: continue
            if tonight and i not in tonight_set: continue
            if txt:
                nm = txt in c["name"].lower() or txt in c["abbreviation"].lower()
                sm = any(txt in s["name"].lower() for s in c["stars"])
                dso = any(txt in o["name"].lower() for o in c.get("deep_sky_objects", []))
                if not nm and not sm and not dso: continue
            item = QListWidgetItem(f"  {c['name']}  ({c['abbreviation']})")
            item.setData(Qt.UserRole, i)
            item.setIcon(STAR_ICON_ON() if i in self._favorites else STAR_ICON_OFF())
            self.lst.addItem(item)
        self.lst.blockSignals(False)
        if self.lst.count() > 0: self.lst.setCurrentRow(0)

    def _on_select(self, row):
        if row < 0: return
        idx = self.lst.item(row).data(Qt.UserRole)
        self._go_to_constellation(idx)

    def _go_to_constellation(self, idx):
        c = self._constellations[idx]
        self.star_map.set_constellation(c)
        self.info.show_constellation(c)
        self._in_detail = True
        self.center_stack.setCurrentIndex(1)

    def _go_overview(self):
        self.info.save_current_note()
        self._in_detail = False
        self.center_stack.setCurrentIndex(0)

    def _random_constellation(self):
        idx = random.randint(0, len(self._constellations) - 1)
        self._go_to_constellation(idx)

    def toggle_favorite(self):
        row = self.lst.currentRow()
        if row < 0: return
        idx = self.lst.item(row).data(Qt.UserRole)
        if idx in self._favorites:
            self._favorites.discard(idx)
        else:
            self._favorites.add(idx)
        self._stats["favorites"] = list(self._favorites)
        save_stats(self._stats)
        self._filter()

    def refresh_overview(self):
        self.overview.build(self._constellations)
        self._filter()

# ============================================================
# QUIZ MODE  (multiple question types)
# ============================================================
class QuizMode(QWidget):
    def __init__(self, constellations, stars_db, stats, settings, parent=None):
        super().__init__(parent)
        self._constellations = constellations
        self._stars_db = stars_db
        self._stats = stats; self._settings = settings
        self._questions = []; self._current = 0; self._score = 0
        self._answered = False; self._correct_idx = -1; self._choice_map = []
        self._q_type = "identify_constellation"
        lay = QVBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(8)

        hdr = QHBoxLayout()
        t = QLabel("Constellation Quiz"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); hdr.addWidget(t); hdr.addStretch()
        self.lbl_score = QLabel("Score: 0 / 0"); self.lbl_score.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_score.setStyleSheet("color:#90a8ff"); hdr.addWidget(self.lbl_score)
        lay.addLayout(hdr)

        # Difficulty + Question type
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Difficulty:"))
        self.diff_btns = []
        for label, key in [("Easy", "Easy"), ("Medium", "Medium"), ("Hard", "Hard")]:
            b = QPushButton(label); b.setCheckable(True); b.setFixedHeight(30)
            b.clicked.connect(lambda _, k=key: self._set_diff(k))
            ctrl.addWidget(b); self.diff_btns.append(b)
        self.diff_btns[1].setChecked(True); self._difficulty = "Medium"
        ctrl.addSpacing(10)
        ctrl.addWidget(QLabel("Type:"))
        self.type_cb = QComboBox()
        self.type_cb.addItems(["Identify Constellation", "Identify Star", "Hemisphere Quiz", "Season Quiz"])
        self.type_cb.currentIndexChanged.connect(self._set_qtype)
        ctrl.addWidget(self.type_cb)
        ctrl.addStretch(); lay.addLayout(ctrl)

        self.progress = QProgressBar(); self.progress.setRange(0, 10); self.progress.setValue(0)
        self.progress.setFormat("Question %v / %m"); lay.addWidget(self.progress)

        self.star_map = StarMapWidget(settings=settings)
        self.star_map.quiz_mode = True; self.star_map.setMinimumHeight(320)
        lay.addWidget(self.star_map, 1)

        self.question_lbl = QLabel(); self.question_lbl.setAlignment(Qt.AlignCenter)
        self.question_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.question_lbl.setStyleSheet("color:#8098e0"); self.question_lbl.setWordWrap(True)
        lay.addWidget(self.question_lbl)

        grid = QWidget(); gl = QHBoxLayout(grid); gl.setSpacing(10)
        self.buttons = []
        for i in range(4):
            b = QPushButton(); b.setFont(QFont("Segoe UI", 13, QFont.Bold)); b.setMinimumHeight(50)
            b.clicked.connect(lambda _, idx=i: self._answer(idx))
            gl.addWidget(b); self.buttons.append(b)
        lay.addWidget(grid)

        bot = QHBoxLayout(); bot.addStretch()
        self.btn_next = QPushButton("Next  ->"); self.btn_next.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_next.setEnabled(False); self.btn_next.clicked.connect(self._next); bot.addWidget(self.btn_next)
        self.btn_new = QPushButton("New Quiz"); self.btn_new.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_new.clicked.connect(self._new_quiz); bot.addWidget(self.btn_new)
        lay.addLayout(bot)
        self._new_quiz()

    def _set_diff(self, d):
        self._difficulty = d
        for b, k in zip(self.diff_btns, ["Easy", "Medium", "Hard"]):
            b.setChecked(k == d)
        self._new_quiz()

    def _set_qtype(self, idx):
        types = ["identify_constellation", "identify_star", "hemisphere", "season"]
        self._q_type = types[idx]
        self._new_quiz()

    def _apply_difficulty(self):
        self.star_map.show_lines = self._difficulty != "Hard"
        self.star_map.show_names = self._difficulty == "Easy"

    def _new_quiz(self):
        self._questions = list(range(len(self._constellations)))
        random.shuffle(self._questions)
        self._questions = self._questions[:10]
        self._current = 0; self._score = 0; self._answered = False
        self.progress.setValue(0); self._apply_difficulty(); self._show_question()

    def _show_question(self):
        if self._current >= len(self._questions):
            self._show_results(); return
        self._answered = False
        ci = self._questions[self._current]
        self._apply_difficulty()
        self.progress.setValue(self._current + 1)
        self.lbl_score.setText(f"Score: {self._score} / {self._current}")
        self.btn_next.setEnabled(False)
        qt = self._q_type

        if qt == "identify_constellation":
            self._correct_idx = ci
            self.star_map.set_constellation(self._constellations[ci])
            self.star_map.setVisible(True); self.question_lbl.setVisible(True)
            self.question_lbl.setText("Which constellation is shown?")
            self._setup_choices([self._constellations[i]["name"] for i in [ci] + random.sample([x for x in range(len(self._constellations)) if x != ci], 3)])

        elif qt == "identify_star":
            c = self._constellations[ci]
            self.star_map.set_constellation(c)
            self.star_map.show_names = False
            self.star_map.setVisible(True); self.question_lbl.setVisible(True)
            star_idx = random.randint(0, len(c["stars"]) - 1)
            correct_star = c["stars"][star_idx]["name"]
            self._correct_idx = ci  # reuse
            self._star_correct_name = correct_star
            self.question_lbl.setText(f"What is the highlighted star in {c['name']}?")
            wrong_stars = [s["name"] for s in c["stars"] if s["name"] != correct_star]
            random.shuffle(wrong_stars)
            choices = [correct_star] + wrong_stars[:3]
            random.shuffle(choices)
            self._star_choices = choices
            self._setup_choices(choices)

        elif qt == "hemisphere":
            self._correct_idx = ci
            self.star_map.set_constellation(self._constellations[ci])
            self.star_map.setVisible(True); self.question_lbl.setVisible(True)
            correct_hemi = self._constellations[ci]["hemisphere"]
            self._text_correct = correct_hemi
            self.question_lbl.setText(f"Which hemisphere is {self._constellations[ci]['name']} in?")
            hemis = ["Northern", "Southern", "Both"]
            choices = [correct_hemi] + [h for h in hemis if h != correct_hemi]
            random.shuffle(choices)
            self._text_choices = choices
            self._setup_choices(choices)

        elif qt == "season":
            self._correct_idx = ci
            self.star_map.set_constellation(self._constellations[ci])
            self.star_map.setVisible(True); self.question_lbl.setVisible(True)
            correct_season = self._constellations[ci]["season"]
            self._text_correct = correct_season
            self.question_lbl.setText(f"What season is {self._constellations[ci]['name']} best viewed?")
            seasons = ["Winter", "Spring", "Summer", "Autumn"]
            choices = [correct_season] + random.sample([s for s in seasons if s != correct_season], 3)
            random.shuffle(choices)
            self._text_choices = choices
            self._setup_choices(choices)

    def _setup_choices(self, labels):
        self._choice_map = list(range(len(labels)))
        for i, b in enumerate(self.buttons):
            b.setText(labels[i]); b.setEnabled(True)
            b.setStyleSheet(""); b.setChecked(False)
            if i < len(labels):
                b.setVisible(True)
            else:
                b.setVisible(False)

    def _answer(self, bi):
        if self._answered: return
        self._answered = True
        qt = self._q_type; ok = False

        if qt == "identify_constellation":
            ok = self._choice_map[bi] == 0  # first choice is always correct in setup
        elif qt == "identify_star":
            ok = self._star_choices[bi] == self._star_correct_name
        elif qt in ("hemisphere", "season"):
            ok = self._text_choices[bi] == self._text_correct

        if ok:
            self._score += 1
            self.buttons[bi].setStyleSheet("background:#0a3a1a;border:2px solid #20c060;color:#40ff80")
        else:
            self.buttons[bi].setStyleSheet("background:#3a0a0a;border:2px solid #c02020;color:#ff4040")
            # Highlight correct
            for j in range(len(self.buttons)):
                if not self.buttons[j].isVisible(): break
                is_correct = False
                if qt == "identify_constellation" and j == 0:
                    is_correct = True
                elif qt == "identify_star" and self._star_choices[j] == self._star_correct_name:
                    is_correct = True
                elif qt in ("hemisphere", "season") and self._text_choices[j] == self._text_correct:
                    is_correct = True
                if is_correct:
                    self.buttons[j].setStyleSheet("background:#0a3a1a;border:2px solid #20c060;color:#40ff80")
        self.lbl_score.setText(f"Score: {self._score} / {self._current + 1}")
        for b in self.buttons: b.setEnabled(False)
        self.btn_next.setEnabled(True)

    def _next(self):
        self._current += 1; self._show_question()

    def _show_results(self):
        self.star_map.current = None; self.star_map.update()
        pct = int(self._score / len(self._questions) * 100)
        msg = "Outstanding!" if pct >= 80 else "Good job!" if pct >= 60 else "Keep studying!" if pct >= 40 else "Keep practicing!"
        self._stats.setdefault("quiz_history", []).append(
            {"score": self._score, "total": len(self._questions), "difficulty": self._difficulty,
             "type": self._q_type, "time": time.time()})
        save_stats(self._stats)
        for b in self.buttons: b.setEnabled(False); b.setText(""); b.setStyleSheet(""); b.setVisible(True)
        self.buttons[0].setText(f"{self._score} / {len(self._questions)} ({pct}%)")
        self.buttons[0].setStyleSheet("background:#12123a;border:2px solid #3858cc;color:#b0c0ff;font-size:15px")
        self.buttons[1].setText(msg)
        self.buttons[1].setStyleSheet("background:#12123a;border:1px solid #22226a;color:#7888b8;font-size:12px")
        self.question_lbl.setText(f"Quiz Complete!")
        self.btn_next.setEnabled(False); self.progress.setValue(self.progress.maximum())

# ============================================================
# FLASHCARD MODE (with auto-advance)
# ============================================================
class FlashcardMode(QWidget):
    def __init__(self, constellations, stats, settings, parent=None):
        super().__init__(parent)
        self._constellations = constellations
        self._stats = stats; self._settings = settings
        self._cards = list(range(len(constellations))); self._pos = 0
        self._showing_answer = False
        self._known = set(stats.get("flashcard_known", []))
        self._unknown = set(stats.get("flashcard_unknown", []))
        self._auto_advance = settings.get("flashcard_auto_advance", False)
        self._auto_delay = settings.get("flashcard_auto_delay", 5.0)
        lay = QVBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(8)

        hdr = QHBoxLayout()
        l = QLabel("Flashcards"); l.setFont(QFont("Segoe UI", 15, QFont.Bold))
        l.setStyleSheet("color:#8098e0"); hdr.addWidget(l); hdr.addStretch()
        self.lbl_prog = QLabel("1 / ?"); self.lbl_prog.setFont(QFont("Segoe UI", 12))
        self.lbl_prog.setStyleSheet("color:#7888b8"); hdr.addWidget(self.lbl_prog)
        lay.addLayout(hdr)

        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("QFrame{background:#0e0e30;border:2px solid #1e1e5a;border-radius:14px}")
        cl = QVBoxLayout(self.card_frame); cl.setContentsMargins(16, 16, 16, 16)
        self.cq = QLabel(); self.cq.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.cq.setAlignment(Qt.AlignCenter); self.cq.setStyleSheet("color:#90a8ff"); self.cq.setWordWrap(True)
        cl.addWidget(self.cq, 1)
        self.cd = QLabel(); self.cd.setFont(QFont("Segoe UI", 12)); self.cd.setAlignment(Qt.AlignCenter)
        self.cd.setStyleSheet("color:#6878a8"); self.cd.setWordWrap(True); cl.addWidget(self.cd)
        self.cmap = StarMapWidget(settings=settings); self.cmap.show_names = False; self.cmap.show_lines = True
        self.cmap.setMinimumHeight(200); self.cmap.setVisible(False); cl.addWidget(self.cmap)
        lay.addWidget(self.card_frame, 1)

        self.btn_flip = QPushButton("Show Star Map"); self.btn_flip.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.btn_flip.setMinimumHeight(44); self.btn_flip.clicked.connect(self._flip); lay.addWidget(self.btn_flip)

        ctrl = QHBoxLayout()
        self.btn_prev = QPushButton("<- Prev"); self.btn_prev.clicked.connect(self._prev); ctrl.addWidget(self.btn_prev)
        self.btn_known = QPushButton("Got it"); self.btn_known.clicked.connect(self._mark_known); ctrl.addWidget(self.btn_known)
        self.btn_unk = QPushButton("Missed"); self.btn_unk.clicked.connect(self._mark_unknown); ctrl.addWidget(self.btn_unk)
        self.btn_nxt = QPushButton("Next ->"); self.btn_nxt.clicked.connect(self._next_card); ctrl.addWidget(self.btn_nxt)
        lay.addLayout(ctrl)

        bot = QHBoxLayout()
        self.lbl_stats = QLabel(""); self.lbl_stats.setStyleSheet("color:#5868a0;font-size:12px"); bot.addWidget(self.lbl_stats)
        bot.addStretch()
        self.btn_shuf = QPushButton("Shuffle"); self.btn_shuf.clicked.connect(self._shuffle); bot.addWidget(self.btn_shuf)
        self.btn_rst = QPushButton("Reset"); self.btn_rst.clicked.connect(self._reset); bot.addWidget(self.btn_rst)
        lay.addLayout(bot)

        # Auto-advance timer (must exist before _show_card)
        self._auto_timer = QTimer(self); self._auto_timer.setSingleShot(True)
        self._auto_timer.timeout.connect(self._auto_next)
        self._show_card()

    def _start_auto_timer(self):
        if self._auto_advance and self._showing_answer:
            self._auto_timer.start(int(self._auto_delay * 1000))
        else:
            self._auto_timer.stop()

    def _auto_next(self):
        if self._pos < len(self._cards) - 1:
            self._pos += 1; self._show_card()

    def _show_card(self):
        if not self._cards: return
        c = self._constellations[self._cards[self._pos]]
        self._showing_answer = False; self.cq.setText(c["name"])
        self.cd.setText(f"{c['season']}  |  {c['hemisphere']}  |  {c['best_viewing']}")
        self.cd.setVisible(True); self.cmap.setVisible(False)
        self.btn_flip.setText("Show Star Map")
        self.lbl_prog.setText(f"{self._pos + 1} / {len(self._cards)}"); self._update_stats()
        self._auto_timer.stop()

    def _flip(self):
        if self._showing_answer:
            self._showing_answer = False; c = self._constellations[self._cards[self._pos]]
            self.cq.setText(c["name"]); self.cd.setVisible(True); self.cmap.setVisible(False)
            self.btn_flip.setText("Show Star Map"); self._auto_timer.stop()
        else:
            self._showing_answer = True; self.cq.setText("What constellation is this?")
            self.cd.setVisible(False); self.cmap.setVisible(True)
            self.cmap.set_constellation(self._constellations[self._cards[self._pos]])
            self.btn_flip.setText("Show Name"); self._start_auto_timer()

    def _prev(self):
        if self._pos > 0: self._pos -= 1; self._show_card()

    def _next_card(self):
        if self._pos < len(self._cards) - 1: self._pos += 1; self._show_card()

    def _mark_known(self):
        i = self._cards[self._pos]; self._known.add(i); self._unknown.discard(i)
        self._stats["flashcard_known"] = list(self._known)
        self._stats["flashcard_unknown"] = list(self._unknown); save_stats(self._stats)
        self._update_stats()
        if self._pos < len(self._cards) - 1: self._pos += 1; self._show_card()

    def _mark_unknown(self):
        i = self._cards[self._pos]; self._unknown.add(i); self._known.discard(i)
        self._stats["flashcard_known"] = list(self._known)
        self._stats["flashcard_unknown"] = list(self._unknown); save_stats(self._stats)
        self._update_stats()
        if self._pos < len(self._cards) - 1: self._pos += 1; self._show_card()

    def _shuffle(self):
        random.shuffle(self._cards); self._pos = 0; self._show_card()

    def _reset(self):
        self._known.clear(); self._unknown.clear(); self._pos = 0; self._show_card()

    def _update_stats(self):
        self.lbl_stats.setText(f"Known: {len(self._known)}   Missed: {len(self._unknown)}   Remaining: {len(self._cards) - len(self._known) - len(self._unknown)}")

# ============================================================
# MATCHING GAME (variable round size)
# ============================================================
class MatchGame(QWidget):
    def __init__(self, constellations, stats, settings, parent=None):
        super().__init__(parent)
        self._constellations = constellations
        self._stats = stats; self._settings = settings
        self._maps = []; self._name_btns = []; self._matched = set()
        self._selected_name = -1; self._mistakes = 0; self._round_cons = []
        self._timer_val = 0; self._timer_active = False; self._round_size = settings.get("matching_round_size", 6)
        lay = QVBoxLayout(self); lay.setContentsMargins(6, 6, 6, 6); lay.setSpacing(8)

        hdr = QHBoxLayout()
        t = QLabel("Matching Game"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); hdr.addWidget(t); hdr.addStretch()
        self.lbl_timer = QLabel("0:00"); self.lbl_timer.setFont(QFont("Segoe UI", 12))
        self.lbl_timer.setStyleSheet("color:#7888b8"); hdr.addWidget(self.lbl_timer)
        self.lbl_mistakes = QLabel("Mistakes: 0"); self.lbl_mistakes.setFont(QFont("Segoe UI", 12))
        self.lbl_mistakes.setStyleSheet("color:#7888b8"); hdr.addWidget(self.lbl_mistakes)
        lay.addLayout(hdr)

        self.lbl_inst = QLabel("Click a name, then click the matching star map")
        self.lbl_inst.setAlignment(Qt.AlignCenter)
        self.lbl_inst.setStyleSheet("color:#5868a0;font-size:12px"); lay.addWidget(self.lbl_inst)

        self.maps_grid = QGridLayout(); self.maps_grid.setSpacing(8)
        lay.addLayout(self.maps_grid, 1)
        self.names_grid = QGridLayout(); self.names_grid.setSpacing(8)
        lay.addLayout(self.names_grid)

        bot = QHBoxLayout(); bot.addStretch()
        self.btn_new_round = QPushButton("New Round"); self.btn_new_round.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_new_round.clicked.connect(self._new_round); bot.addWidget(self.btn_new_round)
        lay.addLayout(bot)
        self._qtimer = QTimer(self); self._qtimer.timeout.connect(self._tick)
        self._new_round()

    def _new_round(self):
        for m in self._maps:
            self.maps_grid.removeWidget(m); m.deleteLater()
        for b, _ in self._name_btns:
            self.names_grid.removeWidget(b); b.deleteLater()
        self._maps.clear(); self._name_btns.clear(); self._matched.clear()
        self._selected_name = -1; self._mistakes = 0; self._timer_val = 0
        rs = min(self._round_size, len(self._constellations))
        n_cols = 3 if rs <= 6 else 4
        idxs = list(range(len(self._constellations))); random.shuffle(idxs)
        self._round_cons = idxs[:rs]
        name_order = list(range(rs)); random.shuffle(name_order)

        for i in range(rs):
            m = MiniStarMap(); m.set_constellation(self._constellations[self._round_cons[i]])
            m.show_lines = True; ci = i
            m.clicked.connect(lambda _, ii=ci: self._on_map_click(ii))
            self.maps_grid.addWidget(m, i // n_cols, i % n_cols)
            self._maps.append(m)

        for pos, ci in enumerate(name_order):
            b = QPushButton(self._constellations[self._round_cons[ci]]["name"])
            b.setFont(QFont("Segoe UI", 11, QFont.Bold)); b.setMinimumHeight(38); b.setCheckable(True)
            orig = ci; b.clicked.connect(lambda _, o=orig: self._on_name_click(o))
            self.names_grid.addWidget(b, pos // n_cols, pos % n_cols)
            self._name_btns.append((b, orig))

        self.lbl_mistakes.setText("Mistakes: 0")
        self.lbl_inst.setText("Click a name, then click the matching star map")
        self._timer_active = True; self._qtimer.start(1000)

    def _on_name_click(self, orig_idx):
        for b, oi in self._name_btns: b.setChecked(oi == orig_idx)
        self._selected_name = orig_idx
        self.lbl_inst.setText(f"Selected: {self._constellations[orig_idx]['name']} — now click the star map")

    def _on_map_click(self, map_idx):
        if map_idx in self._matched or self._selected_name < 0: return
        if self._round_cons[map_idx] == self._selected_name:
            self._matched.add(map_idx)
            self._maps[map_idx].matched = True; self._maps[map_idx].update()
            for b, oi in self._name_btns:
                if oi == self._selected_name:
                    b.setEnabled(False); b.setChecked(False)
                    b.setStyleSheet("background:#0a3a1a;border:1px solid #20c060;color:#40ff80")
            self._selected_name = -1
            if len(self._matched) == len(self._round_cons):
                self._round_complete()
            else:
                self.lbl_inst.setText(f"Correct!  {len(self._matched)} / {len(self._round_cons)} matched")
        else:
            self._mistakes += 1; self.lbl_mistakes.setText(f"Mistakes: {self._mistakes}")
            self._maps[map_idx].flash_wrong()
            for b, oi in self._name_btns:
                if oi == self._selected_name:
                    b.setStyleSheet("background:#3a0a0a;border:1px solid #c02020;color:#ff4040")
                    QTimer.singleShot(450, lambda btn=b: btn.setStyleSheet("") if btn.isEnabled() else None)
            self.lbl_inst.setText("Wrong match — try again")

    def _round_complete(self):
        self._timer_active = False; self._qtimer.stop()
        rs = len(self._round_cons)
        self._stats.setdefault("match_history", []).append(
            {"matches": rs, "mistakes": self._mistakes, "time": self._timer_val, "time_ts": time.time()})
        save_stats(self._stats)
        acc = int(rs / (rs + self._mistakes) * 100)
        self.lbl_inst.setText(f"Round complete!  Accuracy: {acc}%  |  Time: {self._timer_val // 60}:{self._timer_val % 60:02d}")

    def _tick(self):
        if self._timer_active:
            self._timer_val += 1
            self.lbl_timer.setText(f"{self._timer_val // 60}:{self._timer_val % 60:02d}")

# ============================================================
# SETTINGS DIALOG
# ============================================================
class SettingsDialog(QDialog):
    settings_changed = Signal(dict)
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = copy.deepcopy(settings)
        self.setWindowTitle("Settings"); self.setFixedSize(520, 620)
        self.setStyleSheet(DARK_STYLE)
        lay = QVBoxLayout(self); lay.setSpacing(10)

        tabs = QTabWidget()

        # --- General tab ---
        gen = QWidget(); gl = QVBoxLayout(gen); gl.setSpacing(8)

        g1 = QGroupBox("Star Map"); g1l = QVBoxLayout(g1)
        h1 = QHBoxLayout(); h1.addWidget(QLabel("Background Stars:"))
        self.spin_bg = QSpinBox(); self.spin_bg.setRange(50, 800)
        self.spin_bg.setValue(self._settings.get("bg_star_count", 350)); h1.addWidget(self.spin_bg)
        g1l.addLayout(h1)
        h2 = QHBoxLayout(); h2.addWidget(QLabel("Glow Intensity:"))
        self.slider_glow = QSlider(Qt.Horizontal); self.slider_glow.setRange(20, 200)
        self.slider_glow.setValue(int(self._settings.get("glow_intensity", 1.0) * 100))
        self.glow_lbl = QLabel(f"{self.slider_glow.value()}%")
        self.slider_glow.valueChanged.connect(lambda v: self.glow_lbl.setText(f"{v}%"))
        h2.addWidget(self.slider_glow); h2.addWidget(self.glow_lbl)
        g1l.addLayout(h2)
        h3 = QHBoxLayout(); h3.addWidget(QLabel("Animation Speed (ms):"))
        self.spin_speed = QSpinBox(); self.spin_speed.setRange(30, 500)
        self.spin_speed.setValue(self._settings.get("animation_speed", 90)); h3.addWidget(self.spin_speed)
        g1l.addLayout(h3)
        gl.addWidget(g1)

        g2 = QGroupBox("Flashcards"); g2l = QVBoxLayout(g2)
        self.chk_auto = QCheckBox("Auto-advance after flip")
        self.chk_auto.setChecked(self._settings.get("flashcard_auto_advance", False))
        g2l.addWidget(self.chk_auto)
        h4 = QHBoxLayout(); h4.addWidget(QLabel("Auto-advance delay (s):"))
        self.spin_delay = QDoubleSpinBox(); self.spin_delay.setRange(1.0, 30.0); self.spin_delay.setSingleStep(0.5)
        self.spin_delay.setValue(self._settings.get("flashcard_auto_delay", 5.0)); h4.addWidget(self.spin_delay)
        g2l.addLayout(h4)
        gl.addWidget(g2)

        g3 = QGroupBox("Matching Game"); g3l = QVBoxLayout(g3)
        h5 = QHBoxLayout(); h5.addWidget(QLabel("Round size:"))
        self.spin_round = QSpinBox(); self.spin_round.setRange(3, 10)
        self.spin_round.setValue(self._settings.get("matching_round_size", 6)); h5.addWidget(self.spin_round)
        g3l.addLayout(h5)
        gl.addWidget(g3)
        gl.addStretch()
        tabs.addTab(gen, "General")

        # --- Appearance tab ---
        app_tab = QWidget(); al = QVBoxLayout(app_tab); al.setSpacing(8)
        g4 = QGroupBox("Theme"); g4l = QVBoxLayout(g4)
        self.chk_night = QCheckBox("Red Night Vision Mode")
        self.chk_night.setChecked(self._settings.get("night_vision", False))
        self.chk_night.toggled.connect(self._preview_night)
        g4l.addWidget(self.chk_night)
        night_info = QLabel("Night Vision uses only red light to preserve your dark adaptation for actual stargazing.")
        night_info.setWordWrap(True)
        night_info.setStyleSheet("color:#5868a0;font-size:11px")
        g4l.addWidget(night_info)
        al.addWidget(g4); al.addStretch()
        tabs.addTab(app_tab, "Appearance")

        # --- Data tab ---
        data_tab = QWidget(); dl = QVBoxLayout(data_tab); dl.setSpacing(8)
        g5 = QGroupBox("Data Files (in app directory)"); g5l = QVBoxLayout(g5)
        for fname, desc in [(os.path.basename(CONSTELLATIONS_DB), "Constellation database"),
                             (os.path.basename(STARS_DB), "Star catalog"),
                             (os.path.basename(STATS_FILE), "Your statistics & favorites"),
                             (os.path.basename(NOTES_FILE), "Your constellation notes"),
                             (os.path.basename(SETTINGS_FILE), "App settings")]:
            dl2 = QHBoxLayout()
            dl2.addWidget(QLabel(f"{fname}:")); dl2.addWidget(QLabel(desc), 1)
            g5l.addLayout(dl2)
        dl.addWidget(g5)

        g6 = QGroupBox("Import / Export"); g6l = QVBoxLayout(g6)
        btn_export = QPushButton("Export Stats to File..."); btn_export.clicked.connect(self._export_stats)
        g6l.addWidget(btn_export)
        btn_import = QPushButton("Import Stats from File..."); btn_import.clicked.connect(self._import_stats)
        g6l.addWidget(btn_import)
        dl.addWidget(g6); dl.addStretch()
        tabs.addTab(data_tab, "Data")

        lay.addWidget(tabs)

        bl = QHBoxLayout()
        ok = QPushButton("Apply"); ok.clicked.connect(self._apply); bl.addWidget(ok)
        bl.addStretch()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.close); bl.addWidget(cancel)
        lay.addLayout(bl)

    def _preview_night(self, on):
        self.setStyleSheet(NIGHT_STYLE if on else DARK_STYLE)

    def _export_stats(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Stats", "constellation_stats_export.json", "JSON (*.json)")
        if path:
            try:
                # Gather current data
                data = {
                    "stats": self.parent()._stats if hasattr(self.parent(), '_stats') else {},
                    "notes": self.parent()._notes if hasattr(self.parent(), '_notes') else {},
                    "exported": datetime.now().isoformat()
                }
                with open(path, "w") as f: json.dump(data, f, indent=2)
                QMessageBox.information(self, "Exported", f"Stats exported to:\n{path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Export failed: {e}")

    def _import_stats(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Stats", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r") as f: data = json.load(f)
                mw = self.parent()
                if "stats" in data and hasattr(mw, '_stats'):
                    mw._stats.update(data["stats"]); save_stats(mw._stats)
                if "notes" in data and hasattr(mw, '_notes'):
                    mw._notes.update(data["notes"]); save_notes(mw._notes)
                QMessageBox.information(self, "Imported", "Stats imported successfully! Restart modes to see changes.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Import failed: {e}")

    def _apply(self):
        self._settings["bg_star_count"] = self.spin_bg.value()
        self._settings["glow_intensity"] = self.slider_glow.value() / 100.0
        self._settings["animation_speed"] = self.spin_speed.value()
        self._settings["flashcard_auto_advance"] = self.chk_auto.isChecked()
        self._settings["flashcard_auto_delay"] = self.spin_delay.value()
        self._settings["matching_round_size"] = self.spin_round.value()
        self._settings["night_vision"] = self.chk_night.isChecked()
        save_settings(self._settings)
        self.settings_changed.emit(self._settings)
        self.close()

# ============================================================
# STATISTICS DIALOG (enriched)
# ============================================================
class StatsDialog(QDialog):
    def __init__(self, constellations, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Study Statistics"); self.setFixedSize(560, 600)
        self.setStyleSheet(DARK_STYLE)
        lay = QVBoxLayout(self); lay.setSpacing(12)

        t = QLabel("Study Statistics"); t.setFont(QFont("Segoe UI", 16, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); t.setAlignment(Qt.AlignCenter); lay.addWidget(t)

        tb = QTextBrowser(); tb.setFrameShape(QFrame.NoFrame)
        h = "<h3>Quiz History</h3>"
        qh = stats.get("quiz_history", [])
        if qh:
            scores = [q["score"]/q["total"]*100 for q in qh]
            by_diff = {}
            for q in qh:
                by_diff.setdefault(q.get("difficulty", "?"), []).append(q["score"]/q["total"]*100)
            by_type = {}
            for q in qh:
                by_type.setdefault(q.get("type", "identify_constellation"), []).append(q["score"]/q["total"]*100)
            h += f"<p>Games played: <b>{len(qh)}</b>  |  Average: <b>{sum(scores)/len(scores):.0f}%</b>  |  Best: <b>{max(scores):.0f}%</b></p>"
            for d in ["Easy", "Medium", "Hard"]:
                if d in by_diff:
                    ds = by_diff[d]
                    h += f"<p style='font-size:12px'>{d}: {len(ds)} games, avg {sum(ds)/len(ds):.0f}%</p>"
            h += "<p style='font-size:12px;color:#5868a0'><b>By Type:</b></p>"
            for qt, qs in by_type.items():
                h += f"<p style='font-size:11px'>{qt}: {len(qs)} games, avg {sum(qs)/len(qs):.0f}%</p>"
        else:
            h += "<p style='color:#556080'>No quiz data yet.</p>"

        h += "<h3>Matching Game</h3>"
        mh = stats.get("match_history", [])
        if mh:
            accs = [m["matches"]/(m["matches"]+m["mistakes"])*100 for m in mh]
            times = [m["time"] for m in mh]
            h += f"<p>Rounds: <b>{len(mh)}</b>  |  Avg accuracy: <b>{sum(accs)/len(accs):.0f}%</b>  |  Best: <b>{max(accs):.0f}%</b></p>"
            h += f"<p style='font-size:12px'>Avg time: {sum(times)//len(times)//60}:{sum(times)//len(times)%60:02d}  |  Best: {min(times)//60}:{min(times)%60:02d}</p>"
        else:
            h += "<p style='color:#556080'>No matching data yet.</p>"

        h += "<h3>Flashcard Mastery</h3>"
        known = set(stats.get("flashcard_known", []))
        unknown = set(stats.get("flashcard_unknown", []))
        total = len(constellations)
        h += f"<p>Known: <b>{len(known)}</b>  |  Missed: <b>{len(unknown)}</b>  |  Unseen: <b>{total - len(known) - len(unknown)}</b></p>"
        if known:
            pct = len(known) / total * 100
            bar_w = int(pct / 100 * 200)
            h += f"<p style='font-size:12px'>Mastery: <span style='color:#40ff80'>{'#' * (bar_w // 5)}{'-' * (40 - bar_w // 5)}</span> {pct:.0f}%</p>"
            h += "<p style='font-size:11px;color:#6070a0'>Known: " + ", ".join(constellations[i]["name"] for i in sorted(known) if i < len(constellations)) + "</p>"

        h += "<h3>Favorites</h3>"
        favs = set(stats.get("favorites", []))
        if favs:
            h += "<p style='font-size:12px'>" + ", ".join(constellations[i]["name"] for i in sorted(favs) if i < len(constellations)) + "</p>"
        else:
            h += "<p style='color:#556080;font-size:12px'>No favorites set.</p>"

        tb.setHtml(h); lay.addWidget(tb, 1)

        bl = QHBoxLayout()
        clr = QPushButton("Clear All Data"); clr.clicked.connect(self._clear); bl.addWidget(clr)
        bl.addStretch()
        cls = QPushButton("Close"); cls.clicked.connect(self.close); bl.addWidget(cls)
        lay.addLayout(bl)

    def _clear(self):
        mw = self.parent()
        if hasattr(mw, '_stats'):
            mw._stats = {"quiz_history": [], "match_history": [], "flashcard_known": [], "flashcard_unknown": [], "favorites": []}
            save_stats(mw._stats)
        if hasattr(mw, '_notes'):
            mw._notes = {}; save_notes(mw._notes)
        self.close()
        if hasattr(mw, '_refresh_stats'):
            mw._refresh_stats()

# ============================================================
# STAR SEARCH DIALOG
# ============================================================
class StarSearchDialog(QDialog):
    go_to_star = Signal(int)
    def __init__(self, constellations, stars_db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Star Search"); self.setFixedSize(500, 540)
        self.setStyleSheet(DARK_STYLE)
        lay = QVBoxLayout(self); lay.setSpacing(8)

        t = QLabel("Find a Star"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); t.setAlignment(Qt.AlignCenter); lay.addWidget(t)

        self.search = QLineEdit(); self.search.setPlaceholderText("Type a star name (e.g. Sirius, Rigel, Vega)...")
        self.search.textChanged.connect(self._filter); lay.addWidget(self.search)

        self.lst = QListWidget(); self.lst.currentRowChanged.connect(self._on_select)
        lay.addWidget(self.lst, 1)

        self.detail = QTextBrowser(); self.detail.setFrameShape(QFrame.NoFrame)
        self.detail.setFixedHeight(120); lay.addWidget(self.detail)

        bl = QHBoxLayout(); bl.addStretch()
        cls = QPushButton("Close"); cls.clicked.connect(self.close); bl.addWidget(cls)
        lay.addLayout(bl)

        self._all_stars = []
        for ci, c in enumerate(constellations):
            for s in c["stars"]:
                # Check if we have expanded info
                extra = {}
                for sd in stars_db:
                    if sd["name"] == s["name"]:
                        extra = sd; break
                self._all_stars.append((ci, c["name"], s, extra))
        self._filter()

    def _filter(self, txt=""):
        txt = txt.lower().strip()
        self.lst.blockSignals(True); self.lst.clear()
        for ci, cname, s, extra in self._all_stars:
            if txt and txt not in s["name"].lower(): continue
            item = QListWidgetItem(f"{s['name']}  --  {cname}")
            item.setData(Qt.UserRole, (ci, s, extra))
            spec = extra.get("spectral_type", SPECTRAL_MAP.get(s["color"], "?"))
            item.setToolTip(f"Mag: {s['mag']:.1f}  |  Spectral: {spec}")
            self.lst.addItem(item)
        self.lst.blockSignals(False)
        if self.lst.count() > 0: self.lst.setCurrentRow(0)

    def _on_select(self, row):
        if row < 0: return
        ci, s, extra = self.lst.item(row).data(Qt.UserRole)
        c_name = self._all_stars[row][1]
        spec = extra.get("spectral_type", SPECTRAL_MAP.get(s["color"], "Unknown"))
        html = f"<h3 style='margin:2px 0'>{s['name']}</h3>"
        html += f"<p style='font-size:12px;color:#7888b8;margin:2px 0'>"
        html += f"Constellation: <b>{c_name}</b><br>"
        html += f"Apparent Magnitude: <b>{s['mag']:.1f}</b><br>"
        html += f"Spectral Color: <b>{spec}</b><br>"
        if extra:
            if "distance_ly" in extra:
                html += f"Distance: <b>{extra['distance_ly']} ly</b><br>"
            if "spectral_class" in extra:
                html += f"Spectral Class: <b>{extra['spectral_class']}</b><br>"
            if "luminosity_solar" in extra:
                html += f"Luminosity: <b>{extra['luminosity_solar']:,}x Sun</b><br>"
            if "notes" in extra:
                html += f"<br>{extra['notes']}"
        html += "</p>"
        self.detail.setHtml(html)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            row = self.lst.currentRow()
            if row >= 0:
                ci, _, _ = self.lst.item(row).data(Qt.UserRole)
                self.go_to_star.emit(ci); self.close()
        else:
            super().keyPressEvent(e)

# ============================================================
# KEYBOARD SHORTCUTS DIALOG
# ============================================================
class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts"); self.setFixedSize(420, 500)
        self.setStyleSheet(DARK_STYLE)
        lay = QVBoxLayout(self)
        t = QLabel("Keyboard Shortcuts"); t.setFont(QFont("Segoe UI", 15, QFont.Bold))
        t.setStyleSheet("color:#8098e0"); t.setAlignment(Qt.AlignCenter); lay.addWidget(t)
        tb = QTextBrowser(); tb.setFrameShape(QFrame.NoFrame)
        tb.setHtml("""
        <table style="width:100%;font-size:13px;color:#c0c8e0">
        <tr><td><b>1</b></td><td>Study mode</td></tr>
        <tr><td><b>2</b></td><td>Quiz mode</td></tr>
        <tr><td><b>3</b></td><td>Flashcards mode</td></tr>
        <tr><td><b>4</b></td><td>Matching game</td></tr>
        <tr><td><b>5</b></td><td>Comparison mode</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Search constellations</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Star search dialog</td></tr>
        <tr><td><b>Ctrl+D</b></td><td>View statistics</td></tr>
        <tr><td><b>Ctrl+Shift+F</b></td><td>Toggle favorite</td></tr>
        <tr><td><b>Ctrl+,</b></td><td>Settings</td></tr>
        <tr><td><b>Backspace</b></td><td>Back to overview (Study)</td></tr>
        <tr><td><b>N</b></td><td>Next (Flashcard / Quiz)</td></tr>
        <tr><td><b>P</b></td><td>Previous (Flashcard)</td></tr>
        <tr><td><b>Space</b></td><td>Flip flashcard</td></tr>
        <tr><td><b>G</b></td><td>Mark flashcard "Got it"</td></tr>
        <tr><td><b>M</b></td><td>Mark flashcard "Missed"</td></tr>
        <tr><td><b>R</b></td><td>New round / New quiz / Reset</td></tr>
        <tr><td><b>Mouse wheel</b></td><td>Zoom star map</td></tr>
        <tr><td><b>Left drag</b></td><td>Pan star map</td></tr>
        <tr><td><b>Right click / Dbl-click</b></td><td>Reset zoom</td></tr>
        </table>""")
        lay.addWidget(tb, 1)
        cls = QPushButton("Close"); cls.clicked.connect(self.close)
        lay.addWidget(cls)


# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load data from CWD
        self._settings = load_settings()
        self._stats = load_stats()
        self._notes = load_notes()
        self._constellations = load_constellations()
        self._stars_db = load_stars_db()
        self._night_vision = self._settings.get("night_vision", False)

        self.setWindowTitle("Constellation Study App")
        self.resize(1380, 880); self.setMinimumSize(960, 620)

        central = QWidget(); self.setCentralWidget(central)
        ml = QVBoxLayout(central); ml.setContentsMargins(0, 0, 0, 0); ml.setSpacing(0)

        # Top bar
        topbar = QWidget(); topbar.setFixedHeight(52)
        topbar.setStyleSheet("background:#06061a;border-bottom:1px solid #14143a")
        tbl = QHBoxLayout(topbar); tbl.setContentsMargins(12, 0, 12, 0)
        ic = QLabel("*"); ic.setFont(QFont("Segoe UI", 18)); ic.setStyleSheet("background:transparent;color:#90a8ff")
        tbl.addWidget(ic)
        an = QLabel("Constellation Study"); an.setFont(QFont("Segoe UI", 14, QFont.Bold))
        an.setStyleSheet("color:#7080c0;background:transparent"); tbl.addWidget(an)
        tbl.addStretch()

        self.mode_btns = []
        for text, idx in [("Study", 0), ("Quiz", 1), ("Cards", 2), ("Match", 3), ("Compare", 4)]:
            b = QPushButton(text); b.setCheckable(True); b.setFixedHeight(34)
            b.clicked.connect(lambda _, i=idx: self._switch(i))
            tbl.addWidget(b); self.mode_btns.append(b)
        self.mode_btns[0].setChecked(True)
        tbl.addSpacing(8)

        for text, slot in [("*", self._toggle_fav), ("Search", self._star_search),
                           ("Stats", self._show_stats), ("Keys", self._show_shortcuts),
                           ("Settings", self._show_settings)]:
            b = QPushButton(text); b.setFixedSize(40, 34)
            b.clicked.connect(slot); tbl.addWidget(b)
        ml.addWidget(topbar)

        # Status bar
        self.statusbar = QWidget(); self.statusbar.setFixedHeight(24)
        self.statusbar.setStyleSheet("background:#04041a;border-top:1px solid #10102a")
        sbl = QHBoxLayout(self.statusbar); sbl.setContentsMargins(12, 0, 12, 0)
        self.lbl_status = QLabel(""); self.lbl_status.setStyleSheet("color:#4858a0;font-size:11px;background:transparent")
        sbl.addWidget(self.lbl_status); sbl.addStretch()
        self.lbl_count = QLabel(f"{len(self._constellations)} constellations  |  {sum(len(c['stars']) for c in self._constellations)} stars  |  {len(self._stars_db)} cataloged stars")
        self.lbl_count.setStyleSheet("color:#3848a0;font-size:11px;background:transparent")
        sbl.addWidget(self.lbl_count)
        ml.addWidget(self.statusbar)

        # Stack
        self.stack = QStackedWidget()
        self.study = StudyMode(self._constellations, self._stats, self._notes, self._settings)
        self.quiz = QuizMode(self._constellations, self._stars_db, self._stats, self._settings)
        self.flashcards = FlashcardMode(self._constellations, self._stats, self._settings)
        self.match = MatchGame(self._constellations, self._stats, self._settings)
        self.comparison = ComparisonMode(self._constellations)
        self.stack.addWidget(self.study)
        self.stack.addWidget(self.quiz)
        self.stack.addWidget(self.flashcards)
        self.stack.addWidget(self.match)
        self.stack.addWidget(self.comparison)
        ml.addWidget(self.stack)
        self._update_status()

        # Build overview
        self.study.overview.build(self._constellations)

        # Apply night vision if set
        if self._night_vision:
            self._apply_night_vision(True)

    def _switch(self, idx):
        if idx < self.stack.count():
            self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.mode_btns): b.setChecked(i == idx)
        self._update_status()
        if idx == 1: self.quiz._new_quiz()
        elif idx == 3: self.match._new_round()

    def _update_status(self):
        msgs = ["Study - Browse, search, and learn constellations",
                "Quiz - Test your recognition skills",
                "Flashcards - Flip cards to memorize star patterns",
                "Match - Match names to star maps against the clock",
                "Compare - Side-by-side constellation comparison"]
        ci = min(self.stack.currentIndex(), len(msgs) - 1)
        self.lbl_status.setText(msgs[ci])

    def _toggle_fav(self):
        if self.stack.currentIndex() == 0:
            self.study.toggle_favorite()

    def _star_search(self):
        dlg = StarSearchDialog(self._constellations, self._stars_db, self)
        dlg.go_to_star.connect(self._go_to_constellation_from_search)
        dlg.exec()

    def _go_to_constellation_from_search(self, idx):
        self._switch(0)
        self.study._go_to_constellation(idx)

    def _show_stats(self):
        StatsDialog(self._constellations, self._stats, self).exec()

    def _show_shortcuts(self):
        ShortcutsDialog(self).exec()

    def _show_settings(self):
        dlg = SettingsDialog(self._settings, self)
        dlg.settings_changed.connect(self._on_settings_changed)
        dlg.exec()

    def _on_settings_changed(self, new_settings):
        self._settings = new_settings
        nv = self._settings.get("night_vision", False)
        self._apply_night_vision(nv)
        # Refresh overview
        self.study.overview.build(self._constellations)
        self.study._filter()

    def _apply_night_vision(self, on):
        self._night_vision = on
        self.setStyleSheet(NIGHT_STYLE if on else DARK_STYLE)
        pal = app_palette(on)
        QApplication.instance().setPalette(pal)
        # Update star maps
        for w in [self.study.star_map, self.quiz.star_map, self.flashcards.cmap,
                  self.comparison.map_left, self.comparison.map_right]:
            w.night_vision = on; w.update()

    def _refresh_stats(self):
        self.study._favorites = set(self._stats.get("favorites", []))
        self.study._filter()
        self.study.overview.build(self._constellations)
        self.flashcards._known = set(self._stats.get("flashcard_known", []))
        self.flashcards._unknown = set(self._stats.get("flashcard_unknown", []))
        self.flashcards._update_stats()

    def keyPressEvent(self, e):
        k = e.key(); m = e.modifiers()
        if k == Qt.Key_1 and not m: self._switch(0)
        elif k == Qt.Key_2 and not m: self._switch(1)
        elif k == Qt.Key_3 and not m: self._switch(2)
        elif k == Qt.Key_4 and not m: self._switch(3)
        elif k == Qt.Key_5 and not m: self._switch(4)
        elif k == Qt.Key_F and m & Qt.ControlModifier and not (m & Qt.ShiftModifier):
            if self.stack.currentIndex() == 0:
                self.study.search.setFocus(); self.study.search.selectAll()
        elif k == Qt.Key_F and m & Qt.ControlModifier and m & Qt.ShiftModifier:
            self._toggle_fav()
        elif k == Qt.Key_S and m & Qt.ControlModifier:
            self._star_search()
        elif k == Qt.Key_D and m & Qt.ControlModifier:
            self._show_stats()
        elif k == Qt.Key_Comma and m & Qt.ControlModifier:
            self._show_settings()
        elif k == Qt.Key_Backspace and not m:
            if self.stack.currentIndex() == 0: self.study._go_overview()
        elif k == Qt.Key_N and not m:
            if self.stack.currentIndex() == 1: self.quiz._next()
            elif self.stack.currentIndex() == 2: self.flashcards._next_card()
        elif k == Qt.Key_P and not m:
            if self.stack.currentIndex() == 2: self.flashcards._prev()
        elif k == Qt.Key_Space and not m:
            if self.stack.currentIndex() == 2: self.flashcards._flip(); e.accept(); return
        elif k == Qt.Key_G and not m:
            if self.stack.currentIndex() == 2: self.flashcards._mark_known()
        elif k == Qt.Key_M and not m:
            if self.stack.currentIndex() == 2: self.flashcards._mark_unknown()
        elif k == Qt.Key_R and not m:
            if self.stack.currentIndex() == 1: self.quiz._new_quiz()
            elif self.stack.currentIndex() == 2: self.flashcards._reset()
            elif self.stack.currentIndex() == 3: self.match._new_round()
        else:
            super().keyPressEvent(e)

    def closeEvent(self, e):
        # Save notes before closing
        self.study.info.save_current_note()
        save_notes(self._notes)
        save_stats(self._stats)
        save_settings(self._settings)
        super().closeEvent(e)


def app_palette(night_vision=False):
    if night_vision:
        p = QApplication.instance().palette()
        p.setColor(p.ColorRole.Window, QColor(26, 0, 0))
        p.setColor(p.ColorRole.WindowText, QColor(255, 128, 128))
        p.setColor(p.ColorRole.Base, QColor(32, 0, 0))
        p.setColor(p.ColorRole.Text, QColor(255, 128, 128))
        p.setColor(p.ColorRole.Button, QColor(48, 0, 0))
        p.setColor(p.ColorRole.ButtonText, QColor(255, 100, 100))
        p.setColor(p.ColorRole.Highlight, QColor(106, 0, 0))
        p.setColor(p.ColorRole.HighlightedText, QColor(255, 200, 200))
        p.setColor(p.ColorRole.ToolTipBase, QColor(50, 0, 0))
        p.setColor(p.ColorRole.ToolTipText, QColor(255, 150, 150))
    else:
        p = QApplication.instance().palette()
        p.setColor(p.ColorRole.Window, QColor(8, 8, 24))
        p.setColor(p.ColorRole.WindowText, QColor(192, 200, 224))
        p.setColor(p.ColorRole.Base, QColor(12, 12, 40))
        p.setColor(p.ColorRole.Text, QColor(192, 200, 224))
        p.setColor(p.ColorRole.Button, QColor(18, 18, 58))
        p.setColor(p.ColorRole.ButtonText, QColor(144, 168, 255))
        p.setColor(p.ColorRole.Highlight, QColor(26, 42, 106))
        p.setColor(p.ColorRole.HighlightedText, QColor(220, 230, 255))
        p.setColor(p.ColorRole.ToolTipBase, QColor(12, 12, 50))
        p.setColor(p.ColorRole.ToolTipText, QColor(200, 210, 240))
    return p


# ============================================================
# ENTRY POINT
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_STYLE)
    pal = app_palette()
    app.setPalette(pal)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()