from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QSlider, QLabel, QFrame,
)

from ..config import PAGE_MARGIN
from ..core.reader_state import compute_scale
from .page_widgets import PageView, PageScroll
from .rendering import page_to_image, compose_spread


class ReaderPage(QWidget):
    pageChanged = Signal(int)
    chromeToggleRequested = Signal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.state = None
        self.cur_scale = 1.0

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.setInterval(80)
        self.resize_timer.timeout.connect(lambda: self.render(keep=True))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.view = PageView()
        self.view.setObjectName("pageview")
        self.view.clicked.connect(self._on_click)
        self.view.panned.connect(self._on_pan)

        self.scroll = PageScroll()
        self.scroll.setObjectName("pagescroll")
        self.scroll.setWidget(self.view)
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignCenter)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.wheel_turns = settings["wheel_turns"]
        self.scroll.pageRequested.connect(self.turn)
        self.scroll.zoomRequested.connect(self.zoom)
        self.scroll.resized.connect(self.resize_timer.start)
        lay.addWidget(self.scroll, 1)

        lay.addWidget(self._build_bottom_bar())
        settings.changed.connect(self._on_setting)

    def _build_bottom_bar(self):
        self.bottom = QWidget()
        self.bottom.setObjectName("bottombar")
        self.bottom.setAttribute(Qt.WA_StyledBackground, True)
        bl = QHBoxLayout(self.bottom)
        bl.setContentsMargins(16, 8, 16, 8)
        bl.setSpacing(12)

        def nav_button(text, tip, slot):
            b = QToolButton()
            b.setObjectName("nav")
            b.setText(text)
            b.setToolTip(tip)
            b.setFocusPolicy(Qt.NoFocus)
            b.clicked.connect(lambda: slot())
            return b

        self.btn_prev = nav_button("‹", "Page précédente", self.prev_page)
        self.btn_next = nav_button("›", "Page suivante", self.next_page)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setTracking(False)
        self.slider.valueChanged.connect(lambda v: self.go(v - 1))
        self.slider.sliderMoved.connect(self._preview_slider)

        self.page_label = QLabel()
        self.page_label.setObjectName("muted")
        self.page_label.setMinimumWidth(110)
        self.page_label.setAlignment(Qt.AlignCenter)

        lock = QLabel("🔒 Sans JavaScript")
        lock.setObjectName("muted")
        lock.setToolTip("Les pages sont rendues en images : aucun script du PDF n'est exécuté.")

        bl.addWidget(self.btn_prev)
        bl.addWidget(self.slider, 1)
        bl.addWidget(self.btn_next)
        bl.addWidget(self.page_label)
        bl.addWidget(lock)
        return self.bottom

    @property
    def reading(self) -> bool:
        return self.state is not None

    def open(self, state):
        self.close_book()
        self.state = state
        state.double = self.settings["double"]
        state.page = state.normalize(state.page)
        self.render()
        self.pageChanged.emit(state.page)

    def close_book(self):
        if self.state:
            self.state.close()
            self.state = None

    def focus_view(self):
        self.scroll.setFocus()

    def set_bar_visible(self, on: bool):
        self.bottom.setVisible(on)

    def _on_setting(self, key, value):
        if key == "wheel_turns":
            self.scroll.wheel_turns = value
        if not self.reading:
            return
        if key == "fit_mode":
            self.render(keep=(value == "zoom"))
        elif key == "double":
            self.state.double = value
            self.state.page = self.state.normalize(self.state.page)
            self.render()
            self.pageChanged.emit(self.state.page)
        elif key in ("rtl", "shadow"):
            self.render(keep=True)
        elif key == "zoom" and self.settings["fit_mode"] == "zoom":
            self.render(keep=True)

    def go(self, p):
        if not self.reading:
            return
        self.state.go(p)
        self.render()
        self.pageChanged.emit(self.state.page)

    def next_page(self):
        if self.reading:
            self.go(self.state.next_index())

    def prev_page(self):
        if self.reading:
            self.go(self.state.prev_index())

    def turn(self, direction):
        (self.next_page if direction > 0 else self.prev_page)()

    def _preview_slider(self, v):
        self.page_label.setText(f"{v} / {self.state.page_count}")

    def zoom(self, direction):
        if not self.reading:
            return
        s = self.settings
        step = 1 + s["zoom_step"] / 100
        factor = step if direction > 0 else 1 / step
        base = s["zoom"] if s["fit_mode"] == "zoom" else self.cur_scale
        new_zoom = max(0.2, min(6.0, base * factor))
        s.set("zoom", new_zoom, notify=False)
        if s["fit_mode"] != "zoom":
            s.set("fit_mode", "zoom")
        else:
            self.render(keep=True)

    def _on_click(self, gpos):
        s = self.settings
        vp = self.scroll.viewport()
        x = vp.mapFromGlobal(gpos.toPoint()).x() / max(1, vp.width())
        if s["click_nav"]:
            z = s["click_zone"] / 100
            if x < z:
                (self.next_page if s["rtl"] else self.prev_page)()
                return
            if x > 1 - z:
                (self.prev_page if s["rtl"] else self.next_page)()
                return
        self.chromeToggleRequested.emit()

    def _on_pan(self, dx, dy):
        h, v = self.scroll.horizontalScrollBar(), self.scroll.verticalScrollBar()
        h.setValue(h.value() - dx)
        v.setValue(v.value() - dy)

    def render(self, keep=False):
        if not self.reading:
            return
        s = self.settings
        pages = self.state.pages()
        total_w = sum(p.rect.width for p in pages)
        max_h = max(p.rect.height for p in pages)

        M = PAGE_MARGIN
        scale = compute_scale(s["fit_mode"], s["zoom"],
                              max(60, self.scroll.width() - 2 * M),
                              max(60, self.scroll.height() - 2 * M),
                              total_w, max_h)
        self.cur_scale = scale

        dpr = self.devicePixelRatioF()
        imgs = [page_to_image(p, scale, dpr) for p in pages]
        if s["rtl"] and len(imgs) > 1:
            imgs.reverse()
        pm = compose_spread(imgs, dpr, M, s["shadow"])

        hs = self.scroll.horizontalScrollBar().value()
        vs = self.scroll.verticalScrollBar().value()
        self.view.setPixmap(pm)
        self.view.adjustSize()
        if keep:
            QTimer.singleShot(0, lambda: (self.scroll.horizontalScrollBar().setValue(hs),
                                          self.scroll.verticalScrollBar().setValue(vs)))
        else:
            self.scroll.verticalScrollBar().setValue(0)
            self.scroll.horizontalScrollBar().setValue(0)
        self._update_bar()

    def _update_bar(self):
        st = self.state
        n = st.page_count
        self.page_label.setText(f"{' – '.join(str(i + 1) for i in st.spread())} / {n}")
        self.slider.blockSignals(True)
        self.slider.setRange(1, max(1, n))
        self.slider.setValue(st.page + 1)
        self.slider.blockSignals(False)
        self.btn_prev.setEnabled(st.has_prev())
        self.btn_next.setEnabled(st.has_next())
