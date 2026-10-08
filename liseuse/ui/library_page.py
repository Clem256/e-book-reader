from pathlib import Path

from PySide6.QtCore import Qt, QSize, QRectF, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QListWidget, QListWidgetItem, QListView, QStackedWidget, QFrame, QMenu,
    QFileDialog, QInputDialog, QStyledItemDelegate, QStyle,
)

from ..config import CARD_W, CARD_H
from ..core.pdf_tools import cover_path
from .theme import THEMES

COVER_ROLE = Qt.UserRole + 1
INFO_ROLE = Qt.UserRole + 2


class BookDelegate(QStyledItemDelegate):
    def __init__(self, theme_fn, parent=None):
        super().__init__(parent)
        self.theme = theme_fn

    def sizeHint(self, option, index):
        return QSize(CARD_W, CARD_H)

    def paint(self, p, opt, idx):
        t = self.theme()
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        card = QRectF(opt.rect).adjusted(6, 6, -6, -6)
        hovered = bool(opt.state & QStyle.State_MouseOver)
        selected = bool(opt.state & QStyle.State_Selected)
        p.setPen(QPen(QColor(t["accent"] if selected else t["border"]), 2 if selected else 1))
        p.setBrush(QColor(t["hover"] if hovered else t["panel"]))
        p.drawRoundedRect(card, 12, 12)

        inner = card.adjusted(10, 10, -10, -10)
        box = QRectF(inner.x(), inner.y(), inner.width(), 190)

        pm = idx.data(COVER_ROLE)
        if pm is not None and not pm.isNull():
            sz = pm.size().scaled(box.size().toSize(), Qt.KeepAspectRatio)
            target = QRectF(box.center().x() - sz.width() / 2,
                            box.center().y() - sz.height() / 2,
                            sz.width(), sz.height())
            path = QPainterPath()
            path.addRoundedRect(target, 6, 6)
            p.save()
            p.setClipPath(path)
            p.drawPixmap(target, pm, QRectF(pm.rect()))
            p.restore()
            p.setPen(QPen(QColor(0, 0, 0, 45), 1))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(target, 6, 6)
        else:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(t["border"]))
            p.drawRoundedRect(box.adjusted(30, 0, -30, 0), 6, 6)
            p.setPen(QColor(t["sub"]))
            p.drawText(box, Qt.AlignCenter, "PDF")

        f = QFont(opt.font)
        f.setBold(True)
        f.setPointSizeF(10)
        p.setFont(f)
        p.setPen(QColor(t["text"]))
        title_rect = QRectF(inner.x(), box.bottom() + 8, inner.width(), 38)
        p.save()
        p.setClipRect(title_rect)
        p.drawText(title_rect, Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
                   idx.data(Qt.DisplayRole) or "")
        p.restore()

        info = idx.data(INFO_ROLE) or {}
        pages, page = info.get("pages", 0), info.get("page", 0)
        frac = ((page + 1) / pages) if (pages and page > 0) else 0.0
        bar = QRectF(inner.x(), card.bottom() - 30, inner.width(), 4)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(t["border"]))
        p.drawRoundedRect(bar, 2, 2)
        if frac > 0:
            p.setBrush(QColor(t["accent"]))
            p.drawRoundedRect(QRectF(bar.x(), bar.y(), bar.width() * min(frac, 1), bar.height()), 2, 2)

        f2 = QFont(opt.font)
        f2.setPointSizeF(8.5)
        p.setFont(f2)
        p.setPen(QColor(t["sub"]))
        label = f"p. {page + 1}/{pages} · {int(frac * 100)} %" if frac > 0 else \
            (f"{pages} pages · nouveau" if pages else "nouveau")
        p.drawText(QRectF(inner.x(), bar.bottom() + 4, inner.width(), 16),
                   Qt.AlignLeft | Qt.AlignVCenter, label)
        p.restore()


class LibraryPage(QWidget):
    openRequested = Signal(str)
    exportRequested = Signal(str)
    settingsRequested = Signal()

    def __init__(self, library, settings):
        super().__init__()
        self.library = library
        self.settings = settings
        self._covers = {}

        self.setObjectName("libpage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 12)
        root.setSpacing(16)
        root.addLayout(self._build_header())

        self.lib = QListWidget()
        self.lib.setObjectName("library")
        self.lib.setViewMode(QListView.IconMode)
        self.lib.setResizeMode(QListWidget.Adjust)
        self.lib.setMovement(QListView.Static)
        self.lib.setUniformItemSizes(True)
        self.lib.setGridSize(QSize(CARD_W, CARD_H))
        self.lib.setSpacing(0)
        self.lib.setMouseTracking(True)
        self.lib.setFrameShape(QFrame.NoFrame)
        self.lib.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lib.setItemDelegate(BookDelegate(lambda: THEMES[self.settings["theme"]]))
        self.lib.itemActivated.connect(lambda it: self.openRequested.emit(it.data(Qt.UserRole)))
        self.lib.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lib.customContextMenuRequested.connect(self._menu)

        self.empty_label = QLabel(alignment=Qt.AlignCenter)
        self.empty_label.setObjectName("empty")

        self.stack = QStackedWidget()
        self.stack.addWidget(self.lib)
        self.stack.addWidget(self.empty_label)
        root.addWidget(self.stack, 1)

        self.settings.changed.connect(self._on_setting)

    def _build_header(self):
        head = QHBoxLayout()
        head.setSpacing(10)
        title = QLabel("Bibliothèque")
        title.setObjectName("h1")
        self.count_label = QLabel()
        self.count_label.setObjectName("muted")
        head.addWidget(title)
        head.addWidget(self.count_label, 0, Qt.AlignBottom)
        head.addStretch(1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(220)
        self.search.textChanged.connect(lambda _: self.refresh())

        self.sort = QComboBox()
        self.sort.addItems(["Récemment lus", "Titre (A → Z)", "Progression"])
        self.sort.setCurrentIndex(int(self.settings["sort"]))
        self.sort.currentIndexChanged.connect(self._on_sort)

        b_files = QPushButton("＋  Ajouter des PDF")
        b_files.setObjectName("primary")
        b_files.setCursor(Qt.PointingHandCursor)
        b_files.clicked.connect(lambda: self.add_files())
        b_folder = QPushButton("Ajouter un dossier")
        b_folder.setCursor(Qt.PointingHandCursor)
        b_folder.clicked.connect(lambda: self.add_folder())
        b_set = QPushButton("⚙")
        b_set.setToolTip("Paramètres  (Ctrl+,)")
        b_set.setCursor(Qt.PointingHandCursor)
        b_set.clicked.connect(lambda: self.settingsRequested.emit())

        for w in (self.search, self.sort, b_folder, b_files, b_set):
            head.addWidget(w)
        return head

    def _on_setting(self, key, _value):
        if key == "theme":
            self.lib.viewport().update()

    def _on_sort(self, i):
        self.settings.set("sort", i)
        self.refresh()

    def _cover(self, path):
        if path not in self._covers:
            cp = cover_path(path)
            self._covers[path] = QPixmap(str(cp)) if cp else None
        return self._covers[path]

    def reload_covers(self):
        self._covers.clear()
        self.refresh()

    def refresh(self):
        self.lib.clear()
        entries = self.library.entries(self.sort.currentIndex(), self.search.text())
        for path, info in entries:
            item = QListWidgetItem(info.get("title", Path(path).stem))
            item.setData(Qt.UserRole, path)
            item.setData(INFO_ROLE, {"page": info.get("page", 0), "pages": info.get("pages", 0)})
            item.setData(COVER_ROLE, self._cover(path))
            item.setToolTip(path)
            self.lib.addItem(item)
        total = self.library.count()
        self.count_label.setText(f"{total} livre(s)")
        self.empty_label.setText(
            "Aucun résultat." if total
            else "Votre bibliothèque est vide.\n\nGlissez-déposez des PDF ici\nou utilisez « Ajouter des PDF ».")
        self.stack.setCurrentIndex(0 if entries else 1)


    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Ajouter des PDF", "", "PDF (*.pdf)")
        for f in files:
            self.library.register(f)
        if files:
            self.refresh()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            for f in sorted(Path(folder).rglob("*.pdf")):
                self.library.register(str(f))
            self.refresh()

    def _menu(self, pos):
        item = self.lib.itemAt(pos)
        if not item:
            return
        path = item.data(Qt.UserRole)
        m = QMenu(self)
        m.addAction("Ouvrir", lambda: self.openRequested.emit(path))
        m.addAction("Renommer…", lambda: self._rename(path))
        m.addAction("Exporter une version nettoyée…", lambda: self.exportRequested.emit(path))
        m.addSeparator()
        m.addAction("Marquer comme non lu", lambda: self._reset(path))
        m.addAction("Retirer de la bibliothèque", lambda: self._remove(path))
        m.exec(self.lib.mapToGlobal(pos))

    def _rename(self, path):
        new, ok = QInputDialog.getText(self, "Renommer", "Titre :", QLineEdit.Normal,
                                       self.library.title(path))
        if ok and new.strip():
            self.library.rename(path, new.strip())
            self.refresh()

    def _reset(self, path):
        self.library.reset_progress(path)
        self.refresh()

    def _remove(self, path):
        self.library.remove(path)
        self.refresh()
