from PySide6.QtWidgets import QApplication

THEMES = {
    "light": dict(bg="#f3f3f6", panel="#ffffff", text="#1d1d22", sub="#70707c",
                  accent="#5566f0", accent_hover="#4452d8", on_accent="#ffffff",
                  border="#dcdce3", canvas="#e3e3e8", hover="#ebebf1", handle="#c3c3cc"),
    "dark":  dict(bg="#16161a", panel="#1f1f25", text="#e8e8ee", sub="#9a9aa8",
                  accent="#8190ff", accent_hover="#98a4ff", on_accent="#10101a",
                  border="#2f2f38", canvas="#0e0e11", hover="#2a2a33", handle="#3b3b47"),
}
THEME_ORDER = ["light", "dark"]
THEME_LABELS = {"light": "Thème clair", "dark": "Thème nuit"}


def make_qss(t: dict, fs: int = 10) -> str:
    return f"""
* {{ font-family: "Segoe UI", "SF Pro Text", "Inter", "Noto Sans", sans-serif; font-size: {fs}pt; }}
QMainWindow, QDialog, QMessageBox, QInputDialog {{ background: {t['bg']}; color: {t['text']}; }}
QLabel {{ color: {t['text']}; background: transparent; }}
QLabel#h1 {{ font-size: 20pt; font-weight: 600; }}
QLabel#h2 {{ font-size: 11pt; font-weight: 600; color: {t['accent']}; }}
QLabel#muted {{ color: {t['sub']}; }}
QLabel#empty {{ color: {t['sub']}; font-size: 12pt; }}

#libpage {{ background: {t['bg']}; }}
QListWidget#library {{ background: transparent; border: none; outline: 0; }}
QLabel#pageview {{ background: {t['canvas']}; }}
QScrollArea#pagescroll {{ background: {t['canvas']}; border: none; }}

QToolTip {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; padding: 4px 6px; }}

QPushButton {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']};
               border-radius: 8px; padding: 7px 14px; }}
QPushButton:hover {{ background: {t['hover']}; }}
QPushButton#primary {{ background: {t['accent']}; border-color: {t['accent']}; color: {t['on_accent']}; font-weight: 600; }}
QPushButton#primary:hover {{ background: {t['accent_hover']}; border-color: {t['accent_hover']}; }}

QLineEdit {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']};
             border-radius: 8px; padding: 6px 10px; selection-background-color: {t['accent']}; }}
QLineEdit:focus {{ border-color: {t['accent']}; }}

QComboBox {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']};
             border-radius: 8px; padding: 6px 10px; }}
QComboBox::drop-down {{ border: none; width: 22px; }}
QComboBox QAbstractItemView {{ background: {t['panel']}; color: {t['text']};
             border: 1px solid {t['border']}; selection-background-color: {t['hover']}; selection-color: {t['accent']}; }}

QCheckBox {{ color: {t['text']}; spacing: 8px; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {t['handle']}; border-radius: 4px; background: {t['panel']}; }}
QCheckBox::indicator:checked {{ background: {t['accent']}; border-color: {t['accent']}; }}
QSpinBox {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 5px 8px; }}
QSpinBox:disabled {{ color: {t['sub']}; }}

QToolBar {{ background: {t['panel']}; border: none; border-bottom: 1px solid {t['border']};
            spacing: 4px; padding: 6px 10px; }}
QToolBar QLineEdit {{ padding: 4px 8px; }}
QToolButton {{ background: transparent; color: {t['text']}; border: none; border-radius: 8px; padding: 6px 11px; }}
QToolButton:hover {{ background: {t['hover']}; }}
QToolButton:checked {{ background: {t['hover']}; color: {t['accent']}; }}
QToolButton:disabled {{ color: {t['sub']}; }}
QToolButton::menu-indicator {{ image: none; }}
QToolButton#nav {{ font-size: 16pt; padding: 0px 12px 3px 12px; }}

QWidget#bottombar {{ background: {t['panel']}; border-top: 1px solid {t['border']}; }}

QSlider::groove:horizontal {{ height: 4px; background: {t['border']}; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {t['accent']}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {t['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }}

QMenu {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 8px; padding: 6px; }}
QMenu::item {{ padding: 7px 24px 7px 14px; border-radius: 6px; }}
QMenu::item:selected {{ background: {t['hover']}; }}
QMenu::item:disabled {{ color: {t['sub']}; }}
QMenu::separator {{ height: 1px; background: {t['border']}; margin: 6px 8px; }}

QDockWidget {{ color: {t['text']}; }}
QDockWidget::title {{ background: {t['panel']}; padding: 9px 12px; border-bottom: 1px solid {t['border']}; }}
QTreeWidget {{ background: {t['panel']}; color: {t['text']}; border: none; outline: 0; }}
QTreeWidget::item {{ padding: 5px 4px; }}
QTreeWidget::item:hover {{ background: {t['hover']}; }}
QTreeWidget::item:selected {{ background: {t['hover']}; color: {t['accent']}; }}

QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {t['handle']}; border-radius: 4px; min-height: 30px; }}
QScrollBar::handle:horizontal {{ background: {t['handle']}; border-radius: 4px; min-width: 30px; }}
QScrollBar::handle:hover {{ background: {t['sub']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
"""


def apply(name: str, font_size: int = 10):
    QApplication.instance().setStyleSheet(make_qss(THEMES[name], int(font_size)))
