import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .core.library import Library
from .core.settings import Settings
from .core.storage import Storage
from .ui.main_window import MainWindow

import os
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland.textinput=false")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Liseuse")

    storage = Storage()
    settings = Settings(storage)
    library = Library(storage)

    win = MainWindow(storage, settings, library)
    win.show()

    if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
        win.open_book(sys.argv[1])
    elif settings["reopen_last"]:
        last = library.last_opened()
        if last:
            win.open_book(last)
    sys.exit(app.exec())
