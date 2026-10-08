import time

from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtWidgets import QLabel, QScrollArea


class PageView(QLabel):
    clicked = Signal(QPointF)
    panned = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._press = None
        self._last = None
        self._moved = False

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press = e.globalPosition().toPoint()
            self._last = self._press
            self._moved = False

    def mouseMoveEvent(self, e):
        if self._press is None:
            return
        g = e.globalPosition().toPoint()
        if (g - self._press).manhattanLength() > 5:
            self._moved = True
        if self._moved:
            d = g - self._last
            self.panned.emit(d.x(), d.y())
        self._last = g

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._press is not None and not self._moved:
            self.clicked.emit(e.globalPosition())
        self._press = None


class PageScroll(QScrollArea):
    pageRequested = Signal(int)    # +1 / -1
    zoomRequested = Signal(int)    # +1 / -1
    resized = Signal()

    def __init__(self):
        super().__init__()
        self._acc = 0
        self._last = 0.0
        self._flip = 0.0
        self.wheel_turns = True

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.resized.emit()

    def wheelEvent(self, e):
        dy = e.angleDelta().y()
        if dy == 0:
            return super().wheelEvent(e)
        if e.modifiers() & Qt.ControlModifier:
            self.zoomRequested.emit(1 if dy > 0 else -1)
            e.accept()
            return
        sb = self.verticalScrollBar()
        free = sb.maximum() == 0
        at_edge = (dy < 0 and sb.value() >= sb.maximum()) or (dy > 0 and sb.value() <= sb.minimum())
        if (free or at_edge) and self.wheel_turns:
            now = time.monotonic()
            if now - self._last > 0.4:
                self._acc = 0
            self._last = now
            self._acc += dy
            need = 120 if free else 240
            if abs(self._acc) >= need and now - self._flip > 0.3:
                self.pageRequested.emit(-1 if self._acc > 0 else 1)
                self._acc = 0
                self._flip = now
            e.accept()
            return
        self._acc = 0
        super().wheelEvent(e)
