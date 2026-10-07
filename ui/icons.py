"""Drawn UI icons and loaders for the bundled logo images (ui/assets)."""
import sys
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF


def make_icon(kind, color="#8b97b0", size=18):
    """Draws a small icon on an 18x18 design grid, scaled to `size` at 2x for sharp HiDPI."""
    scale = 2
    pm = QPixmap(size * scale, size * scale)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(size * scale / 18.0, size * scale / 18.0)
    pen = QPen(QColor(color), 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    if kind == "search":
        p.drawEllipse(QRectF(2.5, 2.5, 9, 9))
        p.drawLine(QPointF(11, 11), QPointF(15.5, 15.5))
    elif kind == "download":
        p.drawLine(QPointF(9, 2.5), QPointF(9, 11.5))
        p.drawPolyline(QPolygonF([QPointF(5, 8), QPointF(9, 12), QPointF(13, 8)]))
        p.drawLine(QPointF(3.5, 15.5), QPointF(14.5, 15.5))
    elif kind == "key":
        p.drawEllipse(QRectF(2.5, 8, 6, 6))
        p.drawLine(QPointF(8, 9), QPointF(15, 2.5))
        p.drawLine(QPointF(12.5, 5), QPointF(14.5, 7))
    elif kind == "play":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawPolygon(QPolygonF([QPointF(5, 2.5), QPointF(15, 9), QPointF(5, 15.5)]))
    elif kind == "stop":
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(color))
        p.drawRoundedRect(QRectF(4, 4, 10, 10), 2, 2)
    elif kind == "back":
        p.drawLine(QPointF(15, 9), QPointF(3.5, 9))
        p.drawPolyline(QPolygonF([QPointF(8.5, 4), QPointF(3.5, 9), QPointF(8.5, 14)]))
    elif kind == "left":
        p.drawPolyline(QPolygonF([QPointF(11, 3.5), QPointF(5.5, 9), QPointF(11, 14.5)]))
    elif kind == "right":
        p.drawPolyline(QPolygonF([QPointF(7, 3.5), QPointF(12.5, 9), QPointF(7, 14.5)]))
    elif kind == "copy":
        p.drawRoundedRect(QRectF(6, 6, 9, 9), 2, 2)
        p.drawPolyline(QPolygonF([QPointF(12, 3.5), QPointF(4.5, 3.5), QPointF(3, 5), QPointF(3, 12)]))
    elif kind == "external":
        p.drawPolyline(QPolygonF([QPointF(7.5, 3.5), QPointF(3.5, 3.5), QPointF(3.5, 14.5), QPointF(14.5, 14.5), QPointF(14.5, 10.5)]))
        p.drawLine(QPointF(8, 10), QPointF(15, 3))
        p.drawPolyline(QPolygonF([QPointF(10.5, 3), QPointF(15, 3), QPointF(15, 7.5)]))
    elif kind == "x":
        p.drawLine(QPointF(4.5, 4.5), QPointF(13.5, 13.5))
        p.drawLine(QPointF(13.5, 4.5), QPointF(4.5, 13.5))
    elif kind == "check":
        p.drawPolyline(QPolygonF([QPointF(3.5, 9.5), QPointF(7.5, 13.5), QPointF(14.5, 5)]))
    elif kind == "alert":
        p.drawLine(QPointF(9, 4), QPointF(9, 10))
        p.drawPoint(QPointF(9, 13.5))
    elif kind == "info":
        p.drawLine(QPointF(9, 8), QPointF(9, 14))
        p.drawPoint(QPointF(9, 4.5))
    p.end()
    pm.setDevicePixelRatio(scale)
    return QIcon(pm)


# Inside a PyInstaller bundle the files live under sys._MEIPASS; from source they sit next to this file.
_BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
ASSETS = _BASE / "ui" / "assets"


def _load_logo(filename, width=None, height=None):
    """Loads a bundled logo PNG scaled to a logical size, sharp on HiDPI screens."""
    scale = 2
    pm = QPixmap(str(ASSETS / filename))
    if pm.isNull():
        return pm
    if height is not None:
        pm = pm.scaledToHeight(height * scale, Qt.TransformationMode.SmoothTransformation)
    else:
        pm = pm.scaledToWidth(width * scale, Qt.TransformationMode.SmoothTransformation)
    pm.setDevicePixelRatio(scale)
    return pm


def make_logo(size=28):
    """Square icon-only logo (sidebar, window icon)."""
    return _load_logo("logo_mark.png", width=size)


def make_full_logo(height=190):
    """Full logo with the TeleFilter wordmark (sign-in screen)."""
    return _load_logo("logo_full.png", height=height)
