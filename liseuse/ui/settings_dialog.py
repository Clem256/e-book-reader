from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QComboBox, QCheckBox,
    QSpinBox, QPushButton, QMessageBox,
)


class SettingsDialog(QDialog):
    clearCacheRequested = Signal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Paramètres")
        self.setMinimumWidth(480)
        self.ctrl = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 20)
        root.setSpacing(10)

        f = self._section(root, "Apparence")
        self._combo(f, "theme", "Thème", [("Clair", "light"), ("Nuit", "dark")])
        self._spin(f, "font_size", "Taille du texte", 8, 16, " pt")
        self._check(f, "shadow", "Ombre autour de la page")

        f = self._section(root, "Lecture")
        self._combo(f, "fit_mode", "Ajustement",
                    [("À la page", "page"), ("À la largeur", "width"), ("Zoom libre", "zoom")])
        self._check(f, "double", "Double page")
        self._check(f, "rtl", "Lecture de droite à gauche (manga)")
        self._spin(f, "zoom_step", "Pas de zoom", 5, 50, " %")
        self._check(f, "hide_chrome_on_open", "Masquer les barres à l'ouverture d'un livre")

        f = self._section(root, "Navigation")
        self._check(f, "click_nav", "Clic sur les bords de la page pour tourner")
        self._spin(f, "click_zone", "Largeur des zones de clic", 10, 45, " %")
        self._check(f, "wheel_turns", "La molette change de page")
        self.ctrl["click_nav"][0].toggled.connect(self.ctrl["click_zone"][0].setEnabled)

        f = self._section(root, "Général")
        self._check(f, "reopen_last", "Rouvrir le dernier livre au démarrage")
        b_cache = QPushButton("Vider le cache des couvertures")
        b_cache.clicked.connect(self.clearCacheRequested.emit)
        f.addRow(b_cache)

        root.addSpacing(8)
        row = QHBoxLayout()
        b_reset = QPushButton("Réinitialiser")
        b_reset.clicked.connect(self._reset)
        b_close = QPushButton("Fermer")
        b_close.setObjectName("primary")
        b_close.setDefault(True)
        b_close.clicked.connect(self.accept)
        row.addWidget(b_reset)
        row.addStretch(1)
        row.addWidget(b_close)
        root.addLayout(row)

        self._load()

    def _section(self, root, title):
        lbl = QLabel(title)
        lbl.setObjectName("h2")
        root.addSpacing(6)
        root.addWidget(lbl)
        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft)
        root.addLayout(form)
        return form

    def _combo(self, form, key, label, items):
        w = QComboBox()
        for text, value in items:
            w.addItem(text, value)
        w.currentIndexChanged.connect(lambda i, k=key, w=w: self.settings.set(k, w.itemData(i)))
        form.addRow(label, w)
        self.ctrl[key] = (w, "combo")

    def _check(self, form, key, text):
        w = QCheckBox(text)
        w.toggled.connect(lambda on, k=key: self.settings.set(k, bool(on)))
        form.addRow(w)
        self.ctrl[key] = (w, "check")

    def _spin(self, form, key, label, lo, hi, suffix):
        w = QSpinBox()
        w.setRange(lo, hi)
        w.setSuffix(suffix)
        w.valueChanged.connect(lambda v, k=key: self.settings.set(k, int(v)))
        form.addRow(label, w)
        self.ctrl[key] = (w, "spin")

    def _load(self):
        s = self.settings
        for key, (w, kind) in self.ctrl.items():
            w.blockSignals(True)
            if kind == "combo":
                w.setCurrentIndex(max(0, w.findData(s[key])))
            elif kind == "check":
                w.setChecked(bool(s[key]))
            else:
                w.setValue(int(s[key]))
            w.blockSignals(False)
        self.ctrl["click_zone"][0].setEnabled(bool(s["click_nav"]))

    def _reset(self):
        if QMessageBox.question(self, "Réinitialiser",
                                "Remettre tous les paramètres par défaut ?") != QMessageBox.Yes:
            return
        self.settings.reset(list(self.ctrl))
        self._load()
