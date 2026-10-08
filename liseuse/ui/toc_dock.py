from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem


class TocDock(QDockWidget):
    pageRequested = Signal(int)

    def __init__(self, parent=None):
        super().__init__("Sommaire", parent)
        self.setObjectName("tocdock")
        self.setFeatures(QDockWidget.DockWidgetClosable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(250)
        self.tree.itemClicked.connect(self._on_click)
        self.setWidget(self.tree)

    def load(self, entries):
        self.tree.clear()
        if not entries:
            it = QTreeWidgetItem(["Aucun sommaire dans ce PDF"])
            it.setFlags(Qt.NoItemFlags)
            self.tree.addTopLevelItem(it)
            return
        stack = []
        for lvl, title, page in entries:
            it = QTreeWidgetItem([title])
            it.setData(0, Qt.UserRole, page)
            it.setToolTip(0, f"Page {page + 1}")
            while stack and stack[-1][0] >= lvl:
                stack.pop()
            if stack:
                stack[-1][1].addChild(it)
            else:
                self.tree.addTopLevelItem(it)
            stack.append((lvl, it))
        self.tree.expandToDepth(0)

    def _on_click(self, item, _col):
        p = item.data(0, Qt.UserRole)
        if p is not None:
            self.pageRequested.emit(int(p))
