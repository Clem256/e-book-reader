from pathlib import Path

APP_DIR = Path(__file__).resolve().parent / "saved_data"
CACHE_DIR = APP_DIR / "covers"
DATA_FILE = APP_DIR / "data.json"
APP_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

PAGE_MARGIN = 22
CARD_W, CARD_H = 184, 300

THEME_NAMES = ("light", "dark")

SORT_RECENT, SORT_TITLE, SORT_PROGRESS = 0, 1, 2

DEFAULTS = {
    "theme": "dark", "double": False, "fit_mode": "page", "zoom": 1.2,
    "sort": SORT_RECENT, "geometry": "",
    "font_size": 10,
    "shadow": True,
    "rtl": False,
    "click_nav": True,
    "click_zone": 30,
    "wheel_turns": True,
    "zoom_step": 15,
    "hide_chrome_on_open": False,
    "reopen_last": False,
}
