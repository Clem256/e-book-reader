from pathlib import Path

from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QToolBar, QToolButton, QMenu, QLineEdit, QWidget,
    QSizePolicy, QMessageBox, QInputDialog, QFileDialog,
)

from ..core import pdf_tools
from ..core.reader_state import ReaderState
from . import theme
from .library_page import LibraryPage
from .reader_page import ReaderPage
from .settings_dialog import SettingsDialog
from .toc_dock import TocDock


class MainWindow(QMainWindow):
    def __init__(self, storage, settings, library):
        super().__init__()
        self.setWindowTitle("Liseuse")
        self.resize(1100, 820)
        self.setAcceptDrops(True)
        self.storage, self.settings, self.library = storage, settings, library
        self.path = None
        self.chrome = True

        self.lib_page = LibraryPage(library, settings)
        self.reader = ReaderPage(settings)
        self.toc_dock = TocDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.toc_dock)
        self.toc_dock.hide()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.lib_page)
        self.stack.addWidget(self.reader)
        self.setCentralWidget(self.stack)

        self.lib_page.openRequested.connect(self.open_book)
        self.lib_page.exportRequested.connect(self.export_clean)
        self.lib_page.settingsRequested.connect(self.open_settings)
        self.reader.pageChanged.connect(self._on_page_changed)
        self.reader.chromeToggleRequested.connect(lambda: self.set_chrome(not self.chrome))
        self.toc_dock.pageRequested.connect(self.reader.go)
        settings.changed.connect(self._on_setting)

        self._build_actions()
        g = settings["geometry"]
        if g:
            self.restoreGeometry(QByteArray.fromBase64(g.encode()))
        self.apply_theme()
        self.show_library()

    def _act(self, text, slot, shortcut=None, checkable=False, checked=False, tip=None):
        a = QAction(text, self)
        keys = []
        if shortcut:
            keys = shortcut if isinstance(shortcut, list) else [shortcut]
            a.setShortcuts([QKeySequence(k) for k in keys])
        if checkable:
            a.setCheckable(True)
            a.setChecked(checked)
            a.toggled.connect(slot)
        else:
            a.triggered.connect(lambda _=False: slot())
        if tip or keys:
            a.setToolTip(f"{tip or text}" + (f"  ({keys[0]})" if keys else ""))
        self.addAction(a)
        return a

    def _build_actions(self):
        s, r = self.settings, self.reader
        self.a_back = self._act("←  Bibliothèque", self.back, "Escape", tip="Retour à la bibliothèque")
        self.a_prev = self._act("Page précédente", r.prev_page)
        self.a_next = self._act("Page suivante", r.next_page)
        self.a_first = self._act("Première page", lambda: r.go(0), "Home")
        self.a_last = self._act("Dernière page", lambda: r.go(10**9), "End")
        self.a_zin = self._act("+", lambda: r.zoom(1), ["Ctrl++", "Ctrl+="], tip="Zoom avant")
        self.a_zout = self._act("−", lambda: r.zoom(-1), "Ctrl+-", tip="Zoom arrière")

        self.a_fit_page = self._act("Ajuster à la page", lambda on: self._on_fit_toggled("page", on),
                                    "F", True, s["fit_mode"] == "page")
        self.a_fit_width = self._act("Ajuster à la largeur", lambda on: self._on_fit_toggled("width", on),
                                     "W", True, s["fit_mode"] == "width")
        self.a_double = self._act("Double page", lambda on: s.set("double", on), "D", True, s["double"])

        self.theme_actions = {}
        for key in theme.THEME_ORDER:
            self.theme_actions[key] = self._act(theme.THEME_LABELS[key],
                                                lambda on, k=key: self._on_theme_toggled(k, on),
                                                None, True, s["theme"] == key)
        self.a_cycle = self._act("Changer de thème", self.cycle_theme, "N")

        self.a_full = self._act("Plein écran", self.toggle_full, "F11")
        self.a_settings = self._act("Paramètres…", self.open_settings, "Ctrl+,")
        self.a_clean = self._act("Exporter une version nettoyée…", self.export_clean_current, "Ctrl+E")

        self.a_toc = self.toc_dock.toggleViewAction()
        self.a_toc.setText("☷  Sommaire")
        self.a_toc.setShortcut(QKeySequence("T"))
        self.a_toc.setToolTip("Sommaire  (T)")
        self.addAction(self.a_toc)

        self.reader_actions = [self.a_back, self.a_prev, self.a_next, self.a_first, self.a_last,
                               self.a_zin, self.a_zout, self.a_fit_page, self.a_fit_width,
                               self.a_double, self.a_clean, self.a_toc]

        menu = QMenu(self)
        for a in (self.a_fit_page, self.a_fit_width, self.a_double):
            menu.addAction(a)
        menu.addSeparator()
        for k in theme.THEME_ORDER:
            menu.addAction(self.theme_actions[k])
        menu.addSeparator()
        menu.addAction(self.a_full)
        menu.addAction(self.a_clean)
        menu.addSeparator()
        menu.addAction(self.a_settings)

        opt = QToolButton()
        opt.setText("⚙  Affichage")
        opt.setPopupMode(QToolButton.InstantPopup)
        opt.setMenu(menu)

        self.goto_edit = QLineEdit()
        self.goto_edit.setPlaceholderText("Page…")
        self.goto_edit.setToolTip("Aller à la page (Entrée)")
        self.goto_edit.setMaximumWidth(90)
        self.goto_edit.returnPressed.connect(self._goto_from_edit)

        tb = QToolBar("Barre")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(tb)
        tb.addAction(self.a_back)
        tb.addAction(self.a_toc)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)
        tb.addWidget(self.goto_edit)
        tb.addAction(self.a_zout)
        tb.addAction(self.a_zin)
        tb.addWidget(opt)
        self.toolbar = tb

        self.apply_keys()
        self._sync_actions()

    def apply_keys(self):
        rtl = self.settings["rtl"]
        prev = ["Right" if rtl else "Left", "PgUp", "Backspace"]
        nxt = ["Left" if rtl else "Right", "PgDown", "Space"]
        self.a_prev.setShortcuts([QKeySequence(k) for k in prev])
        self.a_next.setShortcuts([QKeySequence(k) for k in nxt])

    def _on_fit_toggled(self, mode, on):
        if on:
            self.settings.set("fit_mode", mode)
        self._sync_actions()

    def _on_theme_toggled(self, key, on):
        if on:
            self.settings.set("theme", key)
        self._sync_actions()

    def _sync_actions(self):
        s = self.settings
        states = [(self.a_fit_page, s["fit_mode"] == "page"),
                  (self.a_fit_width, s["fit_mode"] == "width"),
                  (self.a_double, bool(s["double"]))]
        states += [(a, s["theme"] == k) for k, a in self.theme_actions.items()]
        for a, checked in states:
            a.blockSignals(True)
            a.setChecked(checked)
            a.blockSignals(False)

    def _on_setting(self, key, _value):
        if key in ("theme", "font_size"):
            self.apply_theme()
        elif key == "rtl":
            self.apply_keys()
        if key in ("theme", "fit_mode", "double"):
            self._sync_actions()

    def apply_theme(self):
        theme.apply(self.settings["theme"], self.settings["font_size"])
        self.lib_page.lib.viewport().update()

    def cycle_theme(self):
        cur = self.settings["theme"]
        order = theme.THEME_ORDER
        self.settings.set("theme", order[(order.index(cur) + 1) % len(order)])

    @property
    def reading(self) -> bool:
        return self.path is not None and self.stack.currentWidget() is self.reader

    def show_library(self):
        self.reader.close_book()
        self.path = None
        self.storage.flush()
        self.stack.setCurrentWidget(self.lib_page)
        self.toolbar.hide()
        self.toc_dock.hide()
        for a in self.reader_actions:
            a.setEnabled(False)
        self.setWindowTitle("Liseuse")
        self.lib_page.refresh()

    def open_book(self, path: str):
        try:
            doc = pdf_tools.open_document(path)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible d'ouvrir le fichier :\n{e}")
            return
        if doc.needs_pass:
            pwd, ok = QInputDialog.getText(self, "PDF protégé", "Mot de passe :", QLineEdit.Password)
            if not ok or not doc.authenticate(pwd):
                doc.close()
                QMessageBox.warning(self, "Erreur", "Mot de passe incorrect.")
                return

        self.path = self.library.register(path)
        self.library.mark_opened(self.path, doc.page_count)
        saved = self.library.info(self.path).get("page", 0)
        state = ReaderState(doc, page=min(saved, doc.page_count - 1),
                            double=self.settings["double"])

        self.toc_dock.load(state.toc())
        self.stack.setCurrentWidget(self.reader)
        for a in self.reader_actions:
            a.setEnabled(True)
        self.set_chrome(not self.isFullScreen() and not self.settings["hide_chrome_on_open"])
        self.setWindowTitle(f"{self.library.title(self.path)} — Liseuse")
        self.reader.open(state)
        self.reader.focus_view()

    def _on_page_changed(self, page):
        if self.path:
            self.library.set_page(self.path, page)

    def back(self):
        if self.isFullScreen():
            self.toggle_full()
        else:
            self.show_library()

    def _goto_from_edit(self):
        txt = self.goto_edit.text().strip()
        if self.reading and txt.isdigit():
            self.reader.go(int(txt) - 1)
        self.goto_edit.clear()
        self.reader.focus_view()


    def set_chrome(self, on: bool):
        self.chrome = on
        in_reader = self.stack.currentWidget() is self.reader
        self.toolbar.setVisible(on and in_reader)
        self.reader.set_bar_visible(on)

    def toggle_full(self):
        if self.isFullScreen():
            self.showNormal()
            self.set_chrome(True)
        else:
            self.showFullScreen()
            self.set_chrome(False)

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        dlg.clearCacheRequested.connect(self.clear_cache)
        dlg.exec()

    def clear_cache(self):
        pdf_tools.clear_cover_cache()
        self.lib_page.reload_covers()
        QMessageBox.information(self, "Terminé", "Cache des couvertures vidé.")

    def export_clean_current(self):
        if self.reading:
            self.export_clean(self.path)

    def export_clean(self, path):
        default = str(Path(path).with_name(Path(path).stem + "_clean.pdf"))
        dst, _ = QFileDialog.getSaveFileName(self, "Enregistrer la version nettoyée",
                                             default, "PDF (*.pdf)")
        if not dst:
            return
        try:
            pdf_tools.clean_copy(path, dst)
            QMessageBox.information(self, "Terminé",
                                    "Version nettoyée enregistrée (JavaScript, fichiers joints "
                                    "et actions automatiques retirés).")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() and any(u.toLocalFile().lower().endswith(".pdf")
                                          for u in e.mimeData().urls()):
            e.acceptProposedAction()

    def dropEvent(self, e):
        files = [u.toLocalFile() for u in e.mimeData().urls()
                 if u.toLocalFile().lower().endswith(".pdf")]
        for f in files:
            self.library.register(f)
        if not files:
            return
        if len(files) == 1:
            self.open_book(files[0])
        else:
            self.show_library()

    def closeEvent(self, e):
        self.settings.set("geometry", bytes(self.saveGeometry().toBase64()).decode())
        self.storage.flush()
        super().closeEvent(e)
