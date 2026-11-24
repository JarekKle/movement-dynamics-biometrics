from PyQt6.QtGui import QPalette, QColor

COLORS = {
    "text": "#dcdcdc",
    "window": "#1e1f22",
    "border": "#3c3f45",
    "input": "#16171a",
    "accent": "#3d8bd9",
    "panel": "#2b2d31",
    "muted": "#8a8d93",
}

STYLE_SHEET = f"""
QWidget {{ font-size: 10pt; }}

QPushButton {{
    background: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 5px 12px;
    min-height: 1.6em;
}}
QPushButton:hover    {{ background: #34373c; border-color: {COLORS['accent']}; }}
QPushButton:pressed  {{ background: {COLORS['accent']}; }}
QPushButton:disabled {{ color: {COLORS['muted']}; background: #232427; border-color: #2c2e32; }}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    background: {COLORS['input']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 3px;
}}

QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    margin-top: 1.2em;
    padding: 6px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; color: {COLORS['muted']}; }}

QLabel#cameraView {{ background: #000; border: 1px solid {COLORS['border']}; color: {COLORS['muted']}; }}
QTextEdit#featuresView {{ font-family: Consolas, "Courier New", monospace; }}
QLabel#statusLabel {{ color: {COLORS['muted']}; padding: 2px 4px; }}
QLabel#movementNameLabel {{ font-size: 13pt; font-weight: bold; padding: 0 8px; }}
"""


def apply_dark_theme(app):
    app.setStyle("Fusion")

    p = QPalette()
    c = {k: QColor(v) for k, v in COLORS.items()}
    R = QPalette.ColorRole
    p.setColor(R.Text, c["text"])
    p.setColor(R.ButtonText, c["text"])
    p.setColor(R.WindowText, c["text"])
    p.setColor(R.ToolTipText, c["text"])
    p.setColor(R.Window, c["window"])
    p.setColor(R.Base, c["input"])
    p.setColor(R.Highlight, c["accent"])
    p.setColor(R.ToolTipBase, c["panel"])
    p.setColor(R.AlternateBase, c["panel"])
    p.setColor(R.Button, c["panel"])
    p.setColor(R.HighlightedText, QColor("#ffffff"))
    for role in (R.WindowText, R.Text, R.ButtonText):
        p.setColor(QPalette.ColorGroup.Disabled, role, c["muted"])

    app.setPalette(p)
    app.setStyleSheet(STYLE_SHEET)