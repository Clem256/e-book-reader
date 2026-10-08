from PySide6.QtCore import QObject, Signal

from ..config import DEFAULTS, THEME_NAMES


class Settings(QObject):
    changed = Signal(str, object)

    def __init__(self, storage):
        super().__init__()
        self._storage = storage
        merged = dict(DEFAULTS)
        merged.update(storage.data["settings"])
        if merged["theme"] not in THEME_NAMES:
            merged["theme"] = DEFAULTS["theme"]
        storage.data["settings"] = merged
        self._d = merged

    def __getitem__(self, key):
        return self._d[key]

    def get(self, key, default=None):
        return self._d.get(key, default)

    def set(self, key, value, notify=True):
        if self._d.get(key) == value:
            return
        self._d[key] = value
        self._storage.schedule_save()
        if notify:
            self.changed.emit(key, value)

    def reset(self, keys):
        for k in keys:
            self.set(k, DEFAULTS[k])
