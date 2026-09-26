"""
ui/theme.py

GILLUX ka color palette aur reusable stylesheet ek hi jagah.
Agriculture/fertilizer business ke liye green + earthy tone use kar rahe hain.
"""

COLOR_PRIMARY = "#1B5E20"        # deep green — branding, buttons
COLOR_PRIMARY_LIGHT = "#2E7D32"  # hover states
COLOR_SIDEBAR_BG = "#F1F8E9"     # halka green sidebar background
COLOR_SIDEBAR_SELECTED = "#C8E6C9"
COLOR_TEXT = "#212121"
COLOR_TEXT_MUTED = "#666666"
COLOR_BORDER = "#DDDDDD"
COLOR_WHITE = "#FFFFFF"
COLOR_DANGER = "#C62828"


def sidebar_stylesheet() -> str:
    return f"""
        QListWidget {{
            background-color: {COLOR_SIDEBAR_BG};
            border: none;
            outline: none;
            font-size: 14px;
            padding-top: 10px;
        }}
        QListWidget::item {{
            padding: 12px 20px;
            color: {COLOR_TEXT};
        }}
        QListWidget::item:selected {{
            background-color: {COLOR_SIDEBAR_SELECTED};
            color: {COLOR_PRIMARY};
            font-weight: bold;
            border-left: 4px solid {COLOR_PRIMARY};
        }}
        QListWidget::item:hover {{
            background-color: {COLOR_SIDEBAR_SELECTED};
        }}
    """


def header_stylesheet() -> str:
    return f"""
        background-color: {COLOR_PRIMARY};
        color: {COLOR_WHITE};
    """


def logout_button_stylesheet() -> str:
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {COLOR_WHITE};
            border: 1px solid {COLOR_WHITE};
            padding: 5px 14px;
            border-radius: 4px;
        }}
        QPushButton:hover {{
            background-color: {COLOR_DANGER};
            border-color: {COLOR_DANGER};
        }}
    """

def primary_button_stylesheet() -> str:
    """Har jagah 'Save'/'Add'/'+' jaisi primary action buttons ke liye reusable style."""
    return f"""
        QPushButton {{
            background-color: {COLOR_PRIMARY};
            color: {COLOR_WHITE};
            padding: 8px 18px;
            font-weight: bold;
            border-radius: 6px;
            border: none;
        }}
        QPushButton:hover {{
            background-color: {COLOR_PRIMARY_LIGHT};
        }}
        QPushButton:pressed {{
            background-color: #144D18;
        }}
    """


def secondary_button_stylesheet() -> str:
    """Kam-important actions (Cancel, Export, Reset waghera) ke liye."""
    return f"""
        QPushButton {{
            background-color: {COLOR_WHITE};
            color: {COLOR_PRIMARY};
            padding: 7px 16px;
            font-weight: bold;
            border-radius: 6px;
            border: 1px solid {COLOR_PRIMARY};
        }}
        QPushButton:hover {{
            background-color: {COLOR_SIDEBAR_SELECTED};
        }}
    """


def empty_state_label_stylesheet() -> str:
    return f"""
        color: {COLOR_TEXT_MUTED};
        font-size: 13px;
        padding: 30px;
    """


# Sidebar section icons — Unicode symbols, koi image asset zaroori nahi
SECTION_ICONS = {
    "Dashboard": "🏠",
    "Stock": "🌾",
    "Khaata": "📖",
    "Sales & Accounts": "💰",
    "Reports": "📊",
    "Settings": "⚙️",
}

def fix_spinbox_rtl(spinbox):
    """
    RTL app mein QDoubleSpinBox ke number aur uske +/- arrows aapas mein
    mix ho jate hain. Ye function number ko hamesha left-to-right (normal)
    tareeqe se dikhata hai aur text ko right-align karta hai — taake
    number aasani se parha ja sake aur arrows apni sahi jagah (dayen)
    par rahein.
    """
    from PySide6.QtCore import Qt
    spinbox.setLayoutDirection(Qt.LeftToRight)
    spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)