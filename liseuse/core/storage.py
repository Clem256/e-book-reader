import json

from PySide6.QtCore import QTimer

from ..config import DATA_FILE


class Storage:
    SAVE_DELAY_MS = 600

    def __init__(self, path=DATA_FILE):
        self.path = path
        self.data = {"settings": {}, "books": {}}
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(self.SAVE_DELAY_MS)
        self._timer.timeout.connect(self.flush)
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        st = loaded.get("settings", {})

        if "theme" not in st and "night" in st:
            st["theme"] = "dark" if st["night"] else "light"
        if "fit_mode" not in st and "fit" in st:
            st["fit_mode"] = "page" if st["fit"] else "zoom"
        self.data["settings"] = st
        self.data["books"] = loaded.get("books", {})

    def schedule_save(self):
        self._timer.start()

    def flush(self):
        self._timer.stop()
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
