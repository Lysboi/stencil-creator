from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor
import logging
from utils import QTextEditLogger

class ImageCropWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.crop_rect = None
        self.dragging = False
        self.start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.crop_rect = QRectF(self.start_pos, self.start_pos)
            self.dragging = True

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.crop_rect.setBottomRight(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.crop_rect:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawRect(self.crop_rect)

class ConsoleWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        self.setLayout(layout)
        
        self.log_handler = QTextEditLogger(self.console)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)