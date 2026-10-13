import sys
import os
import boto3
import botocore
from datetime import datetime, timedelta


def _resource_path(relative_path):
    """Resolve path to a bundled resource (works for PyInstaller and dev)."""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QMessageBox,
    QSizePolicy, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QPen, QBrush, QPainterPath

DARK_STYLESHEET = """
    * {
        font-size: 11pt;
    }
    QLabel#header {
        font-size: 17pt;
        font-weight: bold;
    }
    QLabel#subheader {
        font-size: 14pt;
        font-weight: bold;
    }
    QMainWindow, QWidget {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }
    QLabel {
        color: #e0e0e0;
    }
    QLineEdit {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 3px;
    }
    QPushButton {
        background-color: #1a73e8;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1565c0;
    }
    QPushButton:pressed {
        background-color: #0d47a1;
    }
    QPushButton:disabled {
        background-color: #555;
        color: #888;
    }
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #555;
        border-radius: 4px;
        text-align: center;
        color: #e0e0e0;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 3px;
    }
    QCheckBox {
        color: #e0e0e0;
        spacing: 6px;
    }
    QPushButton#themeBtn {
        background-color: transparent;
        border: 1px solid #555;
        border-radius: 17px;
        font-size: 20pt;
    }
    QPushButton#themeBtn:hover {
        background-color: #333;
    }
    QPushButton#mapToggleBtn {
        font-size: 10pt;
        font-weight: bold;
        border: 1px solid #555;
        border-radius: 4px;
        background-color: transparent;
        color: #e0e0e0;
    }
    QPushButton#mapToggleBtn:hover {
        background-color: #333;
    }
"""

LIGHT_STYLESHEET = """
    * {
        font-size: 11pt;
    }
    QLabel#header {
        font-size: 17pt;
        font-weight: bold;
    }
    QLabel#subheader {
        font-size: 14pt;
        font-weight: bold;
    }
    QMainWindow, QWidget {
        background-color: #f5f5f5;
        color: #212121;
    }
    QLabel {
        color: #212121;
    }
    QLineEdit {
        background-color: #ffffff;
        color: #212121;
        border: 1px solid #bbb;
        border-radius: 4px;
        padding: 3px;
    }
    QPushButton {
        background-color: #1a73e8;
        color: #ffffff;
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1565c0;
    }
    QPushButton:pressed {
        background-color: #0d47a1;
    }
    QPushButton:disabled {
        background-color: #ccc;
        color: #888;
    }
    QProgressBar {
        background-color: #e0e0e0;
        border: 1px solid #bbb;
        border-radius: 4px;
        text-align: center;
        color: #212121;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
        border-radius: 3px;
    }
    QCheckBox {
        color: #212121;
        spacing: 6px;
    }
    QPushButton#themeBtn {
        background-color: transparent;
        border: 1px solid #bbb;
        border-radius: 17px;
        font-size: 20pt;
    }
    QPushButton#themeBtn:hover {
        background-color: #ddd;
    }
    QPushButton#mapToggleBtn {
        font-size: 10pt;
        font-weight: bold;
        border: 1px solid #bbb;
        border-radius: 4px;
        background-color: transparent;
        color: #212121;
    }
    QPushButton#mapToggleBtn:hover {
        background-color: #ddd;
    }
"""

RADAR_SITES = {
    "KABR": (45.4558, -98.4131),
    "KABX": (35.1497, -106.8239),
    "KAKQ": (36.9839, -77.0078),
    "KAMA": (35.2334, -101.7092),
    "KAMX": (25.6111, -80.4128),
    "KAPX": (44.9072, -84.7197),
    "KARX": (43.8228, -91.1914),
    "KATX": (48.1944, -122.4958),
    "KBBX": (39.4961, -121.6317),
    "KBGM": (42.1997, -75.9847),
    "KBHX": (40.4986, -124.2919),
    "KBIS": (46.7708, -100.7606),
    "KBLX": (45.8536, -108.6068),
    "KBMX": (33.1722, -86.7697),
    "KBOX": (41.9556, -71.1375),
    "KBRO": (25.9161, -97.4189),
    "KBUF": (42.9486, -78.7369),
    "KBYX": (24.5975, -81.7033),
    "KCAE": (33.9486, -81.1186),
    "KCBW": (46.0392, -67.8067),
    "KCBX": (43.4908, -116.2356),
    "KCCX": (40.9228, -78.0039),
    "KCLE": (41.4131, -81.8597),
    "KCLX": (32.6556, -81.0422),
    "KCRP": (27.7842, -97.5111),
    "KCXX": (44.5111, -73.1667),
    "KCYS": (41.1519, -104.8061),
    "KDAX": (38.5011, -121.6778),
    "KDDC": (37.7608, -99.9686),
    "KDFX": (29.2728, -100.2803),
    "KDGX": (32.2797, -89.9844),
    "KDIX": (39.9469, -74.4108),
    "KDLH": (46.8369, -92.2097),
    "KDMX": (41.7311, -93.7228),
    "KDOX": (38.8256, -75.4400),
    "KDTX": (42.6997, -83.4717),
    "KDVN": (41.6114, -90.5808),
    "KDYX": (32.5386, -99.2542),
    "KEAX": (38.8103, -94.2644),
    "KEMX": (31.8936, -110.6303),
    "KENX": (42.5864, -74.0639),
    "KEOX": (31.4606, -85.4592),
    "KEPZ": (31.8731, -106.6981),
    "KESX": (35.7011, -114.8917),
    "KEVX": (30.5644, -85.9214),
    "KEWX": (29.7039, -98.0286),
    "KEYX": (35.0978, -117.5608),
    "KFCX": (37.0242, -80.2742),
    "KFDR": (34.3622, -98.9764),
    "KFDX": (34.6342, -103.6189),
    "KFFC": (33.3636, -84.5658),
    "KFSD": (43.5878, -96.7292),
    "KFSX": (34.5744, -111.1983),
    "KFTG": (39.7867, -104.5458),
    "KFWS": (32.5731, -97.3028),
    "KGGW": (48.2064, -106.6253),
    "KGJX": (39.0619, -108.2139),
    "KGLD": (39.3667, -101.7004),
    "KGRB": (44.4986, -88.1111),
    "KGRK": (30.7217, -97.3831),
    "KGRR": (42.8939, -85.5447),
    "KGSP": (34.8833, -82.2200),
    "KGWX": (33.8967, -88.3289),
    "KGYX": (43.8914, -70.2564),
    "KHDX": (33.0769, -106.1200),
    "KHGX": (29.4719, -95.0792),
    "KHNX": (36.3142, -119.6311),
    "KHPX": (36.7369, -87.2847),
    "KHTX": (34.9306, -86.0833),
    "KICT": (37.6544, -97.4431),
    "KICX": (37.5911, -112.8622),
    "KILN": (39.4203, -83.8217),
    "KILX": (40.1506, -89.3369),
    "KIND": (39.7075, -86.2803),
    "KINX": (36.1750, -95.5644),
    "KIWA": (33.2892, -111.6700),
    "KIWX": (41.3586, -85.7000),
    "KJAX": (30.4847, -81.7019),
    "KJGX": (32.6753, -83.3511),
    "KJKL": (37.5908, -83.3131),
    "KLBB": (33.6542, -101.8142),
    "KLCH": (30.1253, -93.2156),
    "KLGX": (47.1158, -124.1069),
    "KLIX": (30.3367, -89.8256),
    "KLNX": (41.9578, -100.5764),
    "KLOT": (41.6044, -88.0847),
    "KLRX": (40.7397, -116.8025),
    "KLSX": (38.6986, -90.6828),
    "KLTX": (33.9894, -78.4292),
    "KLWX": (38.9753, -77.4778),
    "KLZK": (34.8364, -92.2622),
    "KMAF": (31.9433, -102.1894),
    "KMAX": (42.0811, -122.7172),
    "KMBX": (48.3925, -100.8644),
    "KMHX": (34.7761, -76.8764),
    "KMKX": (42.9678, -88.5506),
    "KMLB": (28.1131, -80.6542),
    "KMOB": (30.6794, -88.2397),
    "KMPX": (44.8489, -93.5653),
    "KMQT": (46.5311, -87.5486),
    "KMRX": (36.1686, -83.4017),
    "KMSX": (47.0411, -113.9864),
    "KMTX": (41.2628, -112.4478),
    "KMUX": (37.1553, -121.8983),
    "KMVX": (47.5278, -97.3256),
    "KMXX": (32.5367, -85.7897),
    "KNKX": (32.9189, -117.0419),
    "KNQA": (35.3447, -89.8733),
    "KOAX": (41.3203, -96.3667),
    "KOHX": (36.2472, -86.5625),
    "KOKX": (40.8656, -72.8639),
    "KOTX": (47.6803, -117.6267),
    "KPAH": (37.0683, -88.7719),
    "KPBZ": (40.5317, -80.0186),
    "KPDT": (45.6906, -118.8529),
    "KPOE": (31.1556, -92.9758),
    "KPUX": (38.4597, -104.1814),
    "KRAX": (35.6653, -78.4897),
    "KRGX": (39.7542, -119.4622),
    "KRIW": (43.0661, -108.4772),
    "KRLX": (38.3111, -81.7228),
    "KRTX": (45.7150, -122.9653),
    "KSFX": (43.1058, -112.6861),
    "KSGF": (37.2353, -93.4006),
    "KSHV": (32.4508, -93.8414),
    "KSJT": (31.3714, -100.4925),
    "KSMX": (34.3078, -120.5750),  # NOTE: actual Santa Maria, CA radar coords
    "KSOX": (33.8178, -117.6358),
    "KSRX": (35.2906, -94.3619),
    "KTBW": (27.7056, -82.4017),
    "KTLX": (35.3331, -97.2778),
    "KTWX": (38.9969, -96.2325),
    "KTYX": (43.7558, -75.6800),
    "KUDX": (44.1247, -102.8297),
    "KUEX": (40.3208, -98.4419),
    "KVAX": (30.8903, -83.0019),
    "KVBX": (34.8383, -120.3975),
    "KVNX": (36.7408, -98.1278),
    "KVTX": (34.4117, -119.1794),
    "KVWX": (38.2603, -87.7247),
    "KYUX": (32.4953, -114.6567),
    "LPLA": (38.7303, -27.3222),
    "PABC": (60.7919, -161.8764),
    "PACG": (56.8528, -135.5292),
    "PAEC": (64.5114, -165.2950),
    "PAHG": (60.7258, -151.3514),
    "PAIH": (59.4614, -146.3028),
    "PAKC": (58.6794, -156.6292),
    "PAPD": (65.0350, -147.5014),
    "PHKI": (21.8939, -159.5522),
    "PHKM": (20.1256, -155.7781),
    "PHMO": (21.1328, -157.1803),
    "PHWA": (19.0950, -155.5689),
    "TJUA": (18.1156, -66.0781),
}

import math


def _make_sun_icon(size=64):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    cx, cy = size / 2, size / 2
    r_core = size * 0.18
    ray_inner = size * 0.26
    ray_outer = size * 0.42
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#FDB813")))
    p.drawEllipse(QPointF(cx, cy), r_core, r_core)
    pen = QPen(QColor("#FDB813"), size * 0.07, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    for i in range(8):
        angle = math.radians(i * 45)
        x1 = cx + ray_inner * math.cos(angle)
        y1 = cy + ray_inner * math.sin(angle)
        x2 = cx + ray_outer * math.cos(angle)
        y2 = cy + ray_outer * math.sin(angle)
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    p.end()
    return QIcon(pixmap)


def _make_moon_icon(size=64):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    cx, cy = size / 2, size / 2
    r = size * 0.38
    path = QPainterPath()
    path.addEllipse(QPointF(cx, cy), r, r)
    cutout = QPainterPath()
    cutout.addEllipse(QPointF(cx + r * 0.55, cy - r * 0.25), r * 0.75, r * 0.75)
    crescent = path - cutout
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#C4C9CF")))
    p.drawPath(crescent)
    p.end()
    return QIcon(pixmap)


# Geographic bounds of the CONUS radar map image.
# Adjust these if your map image covers a different extent.
MAP_NORTH = 50.0
MAP_SOUTH = 24.0
MAP_WEST = -126.0
MAP_EAST = -66.0


class ZoomableMap(QWidget):
    """Widget that displays the radar map with zoom, pan, and click-to-select."""
    radar_selected = pyqtSignal(str)

    ZOOM_MIN = 1.0
    ZOOM_MAX = 8.0
    ZOOM_STEP = 1.25

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap_orig = None
        self._zoom = 1.0
        self._pan_offset = QPointF(0, 0)
        self._drag_start = None
        self._pan_at_drag_start = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        btn_style = (
            "QPushButton { background-color: rgba(50,50,50,180); color: white;"
            " border: none; border-radius: 4px; font-weight: bold; }"
            " QPushButton:hover { background-color: rgba(80,80,80,200); }"
        )
        zoom_font = QFont()
        zoom_font.setPointSize(14)
        zoom_font.setBold(True)

        self._zoom_in_btn = QPushButton("+", self)
        self._zoom_in_btn.setFont(zoom_font)
        self._zoom_in_btn.setFixedSize(36, 36)
        self._zoom_in_btn.setStyleSheet(btn_style)
        self._zoom_in_btn.clicked.connect(lambda: self._zoom_by(self.ZOOM_STEP))

        self._zoom_out_btn = QPushButton("-", self)
        self._zoom_out_btn.setFont(zoom_font)
        self._zoom_out_btn.setFixedSize(36, 36)
        self._zoom_out_btn.setStyleSheet(btn_style)
        self._zoom_out_btn.clicked.connect(lambda: self._zoom_by(1 / self.ZOOM_STEP))

    def set_source_pixmap(self, pixmap):
        self._pixmap_orig = pixmap
        self.update()

    # -- geometry helpers --

    def _base_rect(self):
        """The rect the image would occupy at zoom=1, centred in the widget."""
        if not self._pixmap_orig:
            return QRectF()
        pm = self._pixmap_orig
        scale = min(self.width() / pm.width(), self.height() / pm.height())
        w, h = pm.width() * scale, pm.height() * scale
        x = (self.width() - w) / 2
        y = (self.height() - h) / 2
        return QRectF(x, y, w, h)

    def _image_rect(self):
        """The rect the image occupies after zoom + pan."""
        base = self._base_rect()
        cx = base.center().x() + self._pan_offset.x()
        cy = base.center().y() + self._pan_offset.y()
        w = base.width() * self._zoom
        h = base.height() * self._zoom
        return QRectF(cx - w / 2, cy - h / 2, w, h)

    def _widget_to_frac(self, pos):
        """Convert a widget-space point to (frac_x, frac_y) in [0,1] of the image."""
        r = self._image_rect()
        fx = (pos.x() - r.x()) / r.width()
        fy = (pos.y() - r.y()) / r.height()
        return fx, fy

    # -- painting --

    def paintEvent(self, event):
        if not self._pixmap_orig:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        p.drawPixmap(self._image_rect().toRect(), self._pixmap_orig)
        p.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_buttons()
        self.update()

    def _position_buttons(self):
        margin = 10
        self._zoom_in_btn.move(self.width() - self._zoom_in_btn.width() - margin, margin)
        self._zoom_out_btn.move(
            self.width() - self._zoom_out_btn.width() - margin,
            margin + self._zoom_in_btn.height() + 6,
        )

    # -- zoom --

    def _zoom_by(self, factor, focus=None):
        new_zoom = max(self.ZOOM_MIN, min(self.ZOOM_MAX, self._zoom * factor))
        if new_zoom == self._zoom:
            return
        if focus is not None:
            base = self._base_rect()
            bc = base.center()
            old_cx = bc.x() + self._pan_offset.x()
            old_cy = bc.y() + self._pan_offset.y()
            ratio = new_zoom / self._zoom
            new_cx = focus.x() - (focus.x() - old_cx) * ratio
            new_cy = focus.y() - (focus.y() - old_cy) * ratio
            self._pan_offset = QPointF(new_cx - bc.x(), new_cy - bc.y())
        self._zoom = new_zoom
        if self._zoom == 1.0:
            self._pan_offset = QPointF(0, 0)
        self.update()

    def wheelEvent(self, event):
        pos = event.position()
        if event.angleDelta().y() > 0:
            self._zoom_by(self.ZOOM_STEP, focus=pos)
        else:
            self._zoom_by(1 / self.ZOOM_STEP, focus=pos)

    # -- pan (right-click or middle-click drag) --

    def mousePressEvent(self, event):
        if event.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self._drag_start = event.position()
            self._pan_at_drag_start = QPointF(self._pan_offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if event.button() == Qt.MouseButton.LeftButton and self._zoom > 1.0:
            self._drag_start = event.position()
            self._pan_at_drag_start = QPointF(self._pan_offset)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._handle_click(event.position())

    def mouseMoveEvent(self, event):
        if self._drag_start is not None and self._pan_at_drag_start is not None:
            delta = event.position() - self._drag_start
            self._pan_offset = self._pan_at_drag_start + delta
            self.update()

    def mouseReleaseEvent(self, event):
        if self._drag_start is not None:
            moved = (event.position() - self._drag_start)
            was_drag = math.hypot(moved.x(), moved.y()) > 5
            self._drag_start = None
            self._pan_at_drag_start = None
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            if not was_drag and event.button() == Qt.MouseButton.LeftButton:
                self._handle_click(event.position())

    def _handle_click(self, pos):
        if not self._pixmap_orig:
            return
        fx, fy = self._widget_to_frac(pos)
        if not (0 <= fx <= 1 and 0 <= fy <= 1):
            return
        lon = MAP_WEST + fx * (MAP_EAST - MAP_WEST)
        lat = MAP_NORTH - fy * (MAP_NORTH - MAP_SOUTH)
        best = _find_nearest_radar(lat, lon)
        if best:
            self.radar_selected.emit(best)


from zoneinfo import ZoneInfo

RADAR_TIMEZONES = {
    "KABR": "America/Chicago",
    "KABX": "America/Denver",
    "KAKQ": "America/New_York",
    "KAMA": "America/Chicago",
    "KAMX": "America/New_York",
    "KAPX": "America/Detroit",
    "KARX": "America/Chicago",
    "KATX": "America/Los_Angeles",
    "KBBX": "America/Los_Angeles",
    "KBGM": "America/New_York",
    "KBHX": "America/Los_Angeles",
    "KBIS": "America/Chicago",
    "KBLX": "America/Denver",
    "KBMX": "America/Chicago",
    "KBOX": "America/New_York",
    "KBRO": "America/Chicago",
    "KBUF": "America/New_York",
    "KBYX": "America/New_York",
    "KCAE": "America/New_York",
    "KCBW": "America/New_York",
    "KCBX": "America/Boise",
    "KCCX": "America/New_York",
    "KCLE": "America/New_York",
    "KCLX": "America/New_York",
    "KCRP": "America/Chicago",
    "KCXX": "America/New_York",
    "KCYS": "America/Denver",
    "KDAX": "America/Los_Angeles",
    "KDDC": "America/Chicago",
    "KDFX": "America/Chicago",
    "KDGX": "America/Chicago",
    "KDIX": "America/New_York",
    "KDLH": "America/Chicago",
    "KDMX": "America/Chicago",
    "KDOX": "America/New_York",
    "KDTX": "America/Detroit",
    "KDVN": "America/Chicago",
    "KDYX": "America/Chicago",
    "KEAX": "America/Chicago",
    "KEMX": "America/Phoenix",
    "KENX": "America/New_York",
    "KEOX": "America/Chicago",
    "KEPZ": "America/Denver",
    "KESX": "America/Los_Angeles",
    "KEVX": "America/Chicago",
    "KEWX": "America/Chicago",
    "KEYX": "America/Los_Angeles",
    "KFCX": "America/New_York",
    "KFDR": "America/Chicago",
    "KFDX": "America/Denver",
    "KFFC": "America/New_York",
    "KFSD": "America/Chicago",
    "KFSX": "America/Phoenix",
    "KFTG": "America/Denver",
    "KFWS": "America/Chicago",
    "KGGW": "America/Denver",
    "KGJX": "America/Denver",
    "KGLD": "America/Denver",
    "KGRB": "America/Chicago",
    "KGRK": "America/Chicago",
    "KGRR": "America/Detroit",
    "KGSP": "America/New_York",
    "KGWX": "America/Chicago",
    "KGYX": "America/New_York",
    "KHDX": "America/Denver",
    "KHGX": "America/Chicago",
    "KHNX": "America/Los_Angeles",
    "KHPX": "America/Chicago",
    "KHTX": "America/Chicago",
    "KICT": "America/Chicago",
    "KICX": "America/Denver",
    "KILN": "America/New_York",
    "KILX": "America/Chicago",
    "KIND": "America/Indiana/Indianapolis",
    "KINX": "America/Chicago",
    "KIWA": "America/Phoenix",
    "KIWX": "America/Indiana/Indianapolis",
    "KJAX": "America/New_York",
    "KJGX": "America/New_York",
    "KJKL": "America/New_York",
    "KLBB": "America/Chicago",
    "KLCH": "America/Chicago",
    "KLGX": "America/Los_Angeles",
    "KLIX": "America/Chicago",
    "KLNX": "America/Chicago",
    "KLOT": "America/Chicago",
    "KLRX": "America/Los_Angeles",
    "KLSX": "America/Chicago",
    "KLTX": "America/New_York",
    "KLWX": "America/New_York",
    "KLZK": "America/Chicago",
    "KMAF": "America/Chicago",
    "KMAX": "America/Los_Angeles",
    "KMBX": "America/Chicago",
    "KMHX": "America/New_York",
    "KMKX": "America/Chicago",
    "KMLB": "America/New_York",
    "KMOB": "America/Chicago",
    "KMPX": "America/Chicago",
    "KMQT": "America/Detroit",
    "KMRX": "America/New_York",
    "KMSX": "America/Denver",
    "KMTX": "America/Denver",
    "KMUX": "America/Los_Angeles",
    "KMVX": "America/Chicago",
    "KMXX": "America/Chicago",
    "KNKX": "America/Los_Angeles",
    "KNQA": "America/Chicago",
    "KOAX": "America/Chicago",
    "KOHX": "America/Chicago",
    "KOKX": "America/New_York",
    "KOTX": "America/Los_Angeles",
    "KPAH": "America/Chicago",
    "KPBZ": "America/New_York",
    "KPDT": "America/Los_Angeles",
    "KPOE": "America/Chicago",
    "KPUX": "America/Denver",
    "KRAX": "America/New_York",
    "KRGX": "America/Los_Angeles",
    "KRIW": "America/Denver",
    "KRLX": "America/New_York",
    "KRTX": "America/Los_Angeles",
    "KSFX": "America/Boise",
    "KSGF": "America/Chicago",
    "KSHV": "America/Chicago",
    "KSJT": "America/Chicago",
    "KSMX": "America/Los_Angeles",
    "KSOX": "America/Los_Angeles",
    "KSRX": "America/Chicago",
    "KTBW": "America/New_York",
    "KTLX": "America/Chicago",
    "KTWX": "America/Chicago",
    "KTYX": "America/New_York",
    "KUDX": "America/Denver",
    "KUEX": "America/Chicago",
    "KVAX": "America/New_York",
    "KVBX": "America/Los_Angeles",
    "KVNX": "America/Chicago",
    "KVTX": "America/Los_Angeles",
    "KVWX": "America/Chicago",
    "KYUX": "America/Phoenix",
    "LPLA": "Atlantic/Azores",
    "PABC": "America/Anchorage",
    "PACG": "America/Anchorage",
    "PAEC": "America/Nome",
    "PAHG": "America/Anchorage",
    "PAIH": "America/Anchorage",
    "PAKC": "America/Anchorage",
    "PAPD": "America/Anchorage",
    "PHKI": "Pacific/Honolulu",
    "PHKM": "Pacific/Honolulu",
    "PHMO": "Pacific/Honolulu",
    "PHWA": "Pacific/Honolulu",
    "TJUA": "America/Puerto_Rico",
}


def _get_utc_offset(radar_code, date_obj=None):
    """Return a string like 'GMT-5' using the radar's actual IANA timezone."""
    tz_name = RADAR_TIMEZONES.get(radar_code)
    if not tz_name:
        return ""
    try:
        tz = ZoneInfo(tz_name)
        if date_obj:
            dt = datetime(date_obj.year, date_obj.month, date_obj.day, 12, tzinfo=tz)
        else:
            dt = datetime.now(tz)
        offset_seconds = dt.utcoffset().total_seconds()
        offset_hours = int(offset_seconds // 3600)
        return f"GMT{offset_hours:+d}"
    except Exception:
        return ""


import json
import urllib.request
import urllib.parse


def _geocode_nominatim(address):
    """Geocode via OpenStreetMap Nominatim. Returns (lat, lon) or None."""
    try:
        params = urllib.parse.urlencode({
            "q": address, "format": "json", "limit": "1",
        })
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "RadarDownloader/1.0",
        })
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


def _geocode_census(address):
    """Geocode via US Census Bureau. Returns (lat, lon) or None."""
    try:
        params = urllib.parse.urlencode({
            "address": address,
            "benchmark": "Public_AR_Current",
            "format": "json",
        })
        url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "RadarDownloader/1.0",
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0]["coordinates"]
            return float(coords["y"]), float(coords["x"])
    except Exception:
        pass
    return None


def _geocode_address(address):
    """Try Nominatim first, fall back to US Census geocoder."""
    result = _geocode_nominatim(address)
    if result is None:
        result = _geocode_census(address)
    return result


def _find_nearest_radar(lat, lon):
    best, best_dist = None, float("inf")
    for code, (rlat, rlon) in RADAR_SITES.items():
        d = math.hypot(lat - rlat, lon - rlon)
        if d < best_dist:
            best, best_dist = code, d
    return best


s3_client = boto3.client(
    "s3",
    config=botocore.config.Config(signature_version=botocore.UNSIGNED),
)
BUCKET_NAME = "unidata-nexrad-level2"


def list_files_in_s3(prefix):
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
    except Exception as e:
        print("Error listing files:", e)
        return []
    return []


def validate_date_parts(year, month, day):
    try:
        return datetime(int(year), int(month), int(day)).date()
    except Exception:
        return None


def validate_hour_minute(hour_str, minute_str):
    try:
        h, m = int(hour_str), int(minute_str)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        return f"{h:02d}:{m:02d}"
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Background worker so the UI stays responsive during downloads
# ---------------------------------------------------------------------------
class DownloadWorker(QThread):
    progress = pyqtSignal(int, int)   # (current, total)
    finished = pyqtSignal(int)        # file count
    error = pyqtSignal(str)

    def __init__(self, start_dt, end_dt, radar):
        super().__init__()
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.radar = radar

    def run(self):
        download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(download_folder, exist_ok=True)

        prefix = f"{self.start_dt.strftime('%Y/%m/%d')}/{self.radar}/"
        file_list = list_files_in_s3(prefix)

        filtered_files = []
        for file_key in file_list:
            try:
                file_time_str = file_key.split("_")[1][:6]
                file_datetime = datetime.strptime(
                    self.start_dt.strftime("%Y%m%d") + file_time_str,
                    "%Y%m%d%H%M%S",
                )
                if self.start_dt <= file_datetime <= self.end_dt:
                    filtered_files.append(file_key)
            except Exception:
                continue

        total = len(filtered_files)
        if total == 0:
            self.finished.emit(0)
            return

        count = 0
        for idx, file_key in enumerate(filtered_files):
            try:
                file_path = os.path.join(
                    download_folder, os.path.basename(file_key)
                )
                s3_client.download_file(BUCKET_NAME, file_key, file_path)
                count += 1
            except Exception as e:
                self.error.emit(f"Error downloading {file_key}: {e}")
            self.progress.emit(idx + 1, total)

        self.finished.emit(count)


class GeocoderWorker(QThread):
    result = pyqtSignal(str)   # nearest radar code
    error = pyqtSignal(str)

    def __init__(self, address):
        super().__init__()
        self.address = address

    def run(self):
        coords = _geocode_address(self.address)
        if coords is None:
            self.error.emit("Could not geocode address.")
            return
        lat, lon = coords
        code = _find_nearest_radar(lat, lon)
        if code:
            self.result.emit(code)
        else:
            self.error.emit("No nearby radar found.")


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class RadarDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Downloader")
        self.resize(1600, 0)
        self._worker = None
        self._geocoder_worker = None

        base_font = QFont()
        base_font.setPointSize(14)
        base_font.setBold(True)
        self.setFont(base_font)

        self._dark_mode = True
        self.setStyleSheet(DARK_STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # ---- Left panel (controls) ----
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(16, 0, 16,
                                      left_panel.contentsMargins().bottom())
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Top button row: theme toggle + show map (show map only visible when map hidden)
        top_btn_row = QHBoxLayout()
        self._sun_icon = _make_sun_icon()
        self._moon_icon = _make_moon_icon()
        self.theme_btn = QPushButton()
        self.theme_btn.setIcon(self._moon_icon)
        self.theme_btn.setIconSize(self.theme_btn.sizeHint())
        self.theme_btn.setFixedSize(35, 35)
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.clicked.connect(self._on_theme_toggled)
        top_btn_row.addWidget(self.theme_btn)
        top_btn_row.addStretch()

        self.show_map_btn = QPushButton("Show Map")
        self.show_map_btn.setFixedHeight(35)
        self.show_map_btn.setObjectName("mapToggleBtn")
        self.show_map_btn.clicked.connect(self._on_toggle_map)
        self.show_map_btn.setVisible(False)
        top_btn_row.addWidget(self.show_map_btn)
        left_panel.addLayout(top_btn_row)

        bold_font = QFont()
        bold_font.setPointSize(17)
        bold_font.setBold(True)

        # Radar site
        lbl = QLabel("Radar Site")
        lbl.setObjectName("header")
        lbl.setFont(bold_font)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(lbl)

        self.radar_input = QLineEdit()
        self.radar_input.setPlaceholderText("e.g. KTLX")
        self.radar_input.setFixedWidth(140)
        self.radar_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.radar_input.textChanged.connect(self._update_tz_label)
        left_panel.addWidget(self.radar_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.tz_label = QLabel("")
        self.tz_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(self.tz_label)

        left_panel.addSpacing(2)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter address...")
        self.address_input.returnPressed.connect(self._on_find_radar)
        left_panel.addWidget(self.address_input)

        left_panel.addSpacing(4)

        self.find_radar_btn = QPushButton("Find Radar")
        self.find_radar_btn.clicked.connect(self._on_find_radar)
        left_panel.addWidget(self.find_radar_btn)

        left_panel.addSpacing(12)

        # Date
        lbl = QLabel("Select Date")
        lbl.setObjectName("header")
        lbl.setFont(bold_font)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(lbl)
        left_panel.addSpacing(6)

        today = datetime.utcnow().date()
        date_row = QHBoxLayout()
        date_row.addStretch()
        date_row.addWidget(QLabel("Year"))
        self.year_input = QLineEdit(str(today.year))
        self.year_input.setFixedWidth(55)
        self.year_input.textChanged.connect(self._update_tz_label)
        date_row.addWidget(self.year_input)
        date_row.addSpacing(10)
        date_row.addWidget(QLabel("Month"))
        self.month_input = QLineEdit(f"{today.month:02d}")
        self.month_input.setFixedWidth(35)
        self.month_input.textChanged.connect(self._update_tz_label)
        date_row.addWidget(self.month_input)
        date_row.addSpacing(10)
        date_row.addWidget(QLabel("Day"))
        self.day_input = QLineEdit(f"{today.day:02d}")
        self.day_input.setFixedWidth(35)
        self.day_input.textChanged.connect(self._update_tz_label)
        date_row.addWidget(self.day_input)
        date_row.addStretch()
        left_panel.addLayout(date_row)

        left_panel.addSpacing(8)

        day_btn_row = QHBoxLayout()
        prev_btn = QPushButton("Previous Day")
        prev_btn.clicked.connect(lambda: self._change_day(-1))
        next_btn = QPushButton("Next Day")
        next_btn.clicked.connect(lambda: self._change_day(1))
        day_btn_row.addWidget(prev_btn)
        day_btn_row.addWidget(next_btn)
        left_panel.addLayout(day_btn_row)

        left_panel.addSpacing(12)

        # Start time
        lbl = QLabel("Start Time")
        lbl.setObjectName("subheader")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(lbl)
        left_panel.addSpacing(4)

        start_row = QHBoxLayout()
        start_row.addStretch()
        start_row.addWidget(QLabel("Hour"))
        self.start_hh = QLineEdit("00")
        self.start_hh.setFixedWidth(35)
        start_row.addWidget(self.start_hh)
        start_row.addSpacing(20)
        start_row.addWidget(QLabel("Minute"))
        self.start_mm = QLineEdit("00")
        self.start_mm.setFixedWidth(35)
        start_row.addWidget(self.start_mm)
        start_row.addStretch()
        left_panel.addLayout(start_row)

        left_panel.addSpacing(8)

        # End time
        lbl = QLabel("End Time")
        lbl.setObjectName("subheader")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(lbl)
        left_panel.addSpacing(4)

        end_row = QHBoxLayout()
        end_row.addStretch()
        end_row.addWidget(QLabel("Hour"))
        self.end_hh = QLineEdit("23")
        self.end_hh.setFixedWidth(35)
        end_row.addWidget(self.end_hh)
        end_row.addSpacing(20)
        end_row.addWidget(QLabel("Minute"))
        self.end_mm = QLineEdit("59")
        self.end_mm.setFixedWidth(35)
        end_row.addWidget(self.end_mm)
        end_row.addStretch()
        left_panel.addLayout(end_row)

        left_panel.addSpacing(20)

        # Download button and progress bar share the same slot
        self.download_btn = QPushButton("Download")
        self.download_btn.setFixedHeight(36)
        self.download_btn.clicked.connect(self._on_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(36)
        self.progress_bar.setVisible(False)

        from PyQt6.QtWidgets import QStackedWidget
        self._download_stack = QStackedWidget()
        self._download_stack.setFixedHeight(36)
        self._download_stack.addWidget(self.download_btn)
        self._download_stack.addWidget(self.progress_bar)
        self._download_stack.setCurrentWidget(self.download_btn)
        left_panel.addWidget(self._download_stack)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        left_panel.addWidget(self.status_label)

        left_panel.addStretch()

        self._left_widget = QWidget()
        self._left_widget.setLayout(left_panel)
        self._left_widget.setMinimumWidth(340)
        self._left_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        main_layout.addWidget(self._left_widget)

        # ---- Right panel (map toggle + zoomable map) ----
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(2)

        self.map_toggle_btn = QPushButton("Hide Map")
        self.map_toggle_btn.setFixedHeight(35)
        self.map_toggle_btn.setObjectName("mapToggleBtn")
        self.map_toggle_btn.clicked.connect(self._on_toggle_map)
        right_panel.addWidget(self.map_toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        self.map_widget = ZoomableMap()
        self.map_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.map_widget.setMinimumSize(200, 200)
        self.map_widget.radar_selected.connect(self._on_radar_selected)
        map_path = _resource_path("WSR-88DMap.png")
        if os.path.exists(map_path):
            self.map_widget.set_source_pixmap(QPixmap(map_path))
        right_panel.addWidget(self.map_widget)

        self._right_widget = QWidget()
        self._right_widget.setLayout(right_panel)
        main_layout.addWidget(self._right_widget, stretch=1)

        # Tab order: cycle through text boxes only
        text_boxes = [
            self.radar_input, self.address_input,
            self.year_input, self.month_input, self.day_input,
            self.start_hh, self.start_mm,
            self.end_hh, self.end_mm,
        ]
        for i in range(len(text_boxes) - 1):
            self.setTabOrder(text_boxes[i], text_boxes[i + 1])
        self.setTabOrder(text_boxes[-1], text_boxes[0])

        for widget in self.findChildren(QWidget):
            if widget not in text_boxes:
                widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        for tb in text_boxes:
            tb.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.radar_input.setFocus()

        min_h = self._left_widget.sizeHint().height()
        self.resize(1600, min_h)

    # ---- Helpers ----

    def _change_day(self, delta):
        current = validate_date_parts(
            self.year_input.text(), self.month_input.text(), self.day_input.text()
        )
        if current is None:
            current = datetime.utcnow().date()
        new_date = current + timedelta(days=delta)
        self.year_input.setText(new_date.strftime("%Y"))
        self.month_input.setText(new_date.strftime("%m"))
        self.day_input.setText(new_date.strftime("%d"))
        self.start_hh.setText("00")
        self.start_mm.setText("00")

    def _on_download(self):
        radar = self.radar_input.text().upper().strip()
        if not radar:
            QMessageBox.warning(self, "Input Error", "Please enter a radar site code.")
            return

        date_val = validate_date_parts(
            self.year_input.text(), self.month_input.text(), self.day_input.text()
        )
        if not date_val:
            QMessageBox.warning(self, "Input Error", "Invalid date entered.")
            return

        start_time_val = validate_hour_minute(self.start_hh.text(), self.start_mm.text())
        end_time_val = validate_hour_minute(self.end_hh.text(), self.end_mm.text())
        if not start_time_val or not end_time_val:
            QMessageBox.warning(self, "Input Error", "Invalid start or end time.")
            return

        start_dt = datetime.strptime(f"{date_val} {start_time_val}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date_val} {end_time_val}", "%Y-%m-%d %H:%M")
        if start_dt >= end_dt:
            QMessageBox.warning(self, "Input Error", "Start time must be before end time.")
            return

        self.progress_bar.setValue(0)
        self._download_stack.setCurrentWidget(self.progress_bar)
        self.status_label.setText("Downloading...")

        self._worker = DownloadWorker(start_dt, end_dt, radar)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Downloading {current}/{total}")

    def _on_finished(self, count):
        self._download_stack.setCurrentWidget(self.download_btn)
        if count == 0:
            self.status_label.setText(
                f"No files found for radar site {self.radar_input.text().upper().strip()}."
            )
        else:
            self.status_label.setText(f"Download Complete! {count} files downloaded.")

    def _update_tz_label(self):
        radar = self.radar_input.text().upper().strip()
        if not radar or radar not in RADAR_TIMEZONES:
            self.tz_label.setText("")
            return
        date_obj = validate_date_parts(
            self.year_input.text(), self.month_input.text(), self.day_input.text()
        )
        offset_str = _get_utc_offset(radar, date_obj)
        if offset_str:
            self.tz_label.setText(f"Local time: {offset_str}")
        else:
            self.tz_label.setText("")

    def _on_find_radar(self):
        address = self.address_input.text().strip()
        if not address:
            return
        self.find_radar_btn.setEnabled(False)
        self.status_label.setText("Looking up address...")
        self._geocoder_worker = GeocoderWorker(address)
        self._geocoder_worker.result.connect(self._on_geocode_result)
        self._geocoder_worker.error.connect(self._on_geocode_error)
        self._geocoder_worker.start()

    def _on_geocode_result(self, code):
        self.radar_input.setText(code)
        self.find_radar_btn.setEnabled(True)
        self.status_label.setText(f"Nearest radar: {code}")

    def _on_geocode_error(self, message):
        self.find_radar_btn.setEnabled(True)
        self.status_label.setText(message)

    def _on_radar_selected(self, code):
        self.radar_input.setText(code)

    def _on_toggle_map(self):
        visible = self._right_widget.isVisible()
        self._right_widget.setVisible(not visible)
        self.show_map_btn.setVisible(visible)
        if visible:
            self.resize(self._left_widget.sizeHint().width(), self.height())
        else:
            self.resize(1600, self.height())

    def _on_theme_toggled(self):
        self._dark_mode = not self._dark_mode
        if self._dark_mode:
            self.setStyleSheet(DARK_STYLESHEET)
            self.theme_btn.setIcon(self._moon_icon)
        else:
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.theme_btn.setIcon(self._sun_icon)

    def _on_error(self, message):
        self._download_stack.setCurrentWidget(self.download_btn)
        self.status_label.setText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RadarDownloader()
    window.show()
    sys.exit(app.exec())
