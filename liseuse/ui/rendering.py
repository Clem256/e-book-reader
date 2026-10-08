import pymupdf
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor


def pix_to_qimage(pix: pymupdf.Pixmap) -> QImage:
    return QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888).copy()


def page_to_image(page, scale: float, dpr: float) -> QImage:
    mat = pymupdf.Matrix(scale * dpr, scale * dpr)
    img = pix_to_qimage(page.get_pixmap(matrix=mat, alpha=False))
    img = img.convertToFormat(QImage.Format_RGB32)
    img.setDevicePixelRatio(dpr)
    return img


def compose_spread(imgs: list, dpr: float, margin: int, shadow: bool) -> QPixmap:
    w = sum(i.width() for i in imgs) / dpr
    h = max(i.height() for i in imgs) / dpr
    pm = QPixmap(int(round((w + 2 * margin) * dpr)), int(round((h + 2 * margin) * dpr)))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)

    qp = QPainter(pm)
    qp.setRenderHint(QPainter.Antialiasing)
    qp.setPen(Qt.NoPen)
    qp.setBrush(QColor(0, 0, 0, 5))
    page_rect = QRectF(margin, margin, w, h)
    for k in range(10 if shadow else 0, 0, -1):
        qp.drawRoundedRect(page_rect.adjusted(-k, -k + 3, k, k + 3), 3 + k, 3 + k)
    x = float(margin)
    for i in imgs:
        qp.drawImage(QPointF(x, margin + (h - i.height() / dpr) / 2), i)
        x += i.width() / dpr
    qp.end()
    return pm
