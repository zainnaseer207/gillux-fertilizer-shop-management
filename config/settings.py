"""
config/settings.py

Ye file application-wide constants rakhti hai jo baad ke phases mein
poore project mein use hongi (database path, app name, version waghera).

Isko ek "single source of truth" samjhein — agar kal database ka
location change karna ho, sirf yahan ek line change karni hogi,
baaki poore project mein kahin edit nahi karna padega.
"""

import os

# Project root folder ka absolute path (jahan ye config folder hai, uske parent mein)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database file ka path (Phase 2 mein isko SQLAlchemy connect karega)
DATABASE_PATH = os.path.join(BASE_DIR, "data", "gillux.db")

# App branding
APP_NAME = "GILLUX"
APP_SUBTITLE = "Fertilizer Shop Management System"
APP_VERSION = "0.1.0"  # Phase 1 version

# Window default size
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 650
