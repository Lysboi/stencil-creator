from PyQt6.QtWidgets import (QDialog, QGraphicsScene, QGraphicsView, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
                             QGraphicsRectItem, QGraphicsItem)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QPen, QColor, QImage, QBrush, QCursor, QPainter
import numpy as np

class CropGraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.crop_rect = None
        self.is_cropping = False
        self.start_pos = None
        self.guides_visible = True
        self.aspect_ratio_locked = False
        self.aspect_ratio = 1.0

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.scenePos()
            if not self.crop_rect:
                self.crop_rect = QGraphicsRectItem()
                self.crop_rect.setPen(QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DashLine))
                self.addItem(self.crop_rect)
            self.is_cropping = True
            self.update_rect(event.scenePos())

    def mouseMoveEvent(self, event):
        if self.is_cropping:
            self.update_rect(event.scenePos())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_cropping = False

    def update_rect(self, current_pos):
        if not self.start_pos:
            return
            
        # Kırpma alanını hesapla
        x = min(self.start_pos.x(), current_pos.x())
        y = min(self.start_pos.y(), current_pos.y())
        w = abs(current_pos.x() - self.start_pos.x())
        h = abs(current_pos.y() - self.start_pos.y())
        
        # En-boy oranı kilitliyse ayarla
        if self.aspect_ratio_locked and w > 0:
            h = w / self.aspect_ratio
            if current_pos.y() < self.start_pos.y():
                y = self.start_pos.y() - h
                
        # Sahne sınırlarını kontrol et
        rect = self.sceneRect()
        x = max(0, min(x, rect.right()))
        y = max(0, min(y, rect.bottom()))
        w = min(w, rect.right() - x)
        h = min(h, rect.bottom() - y)
        
        self.crop_rect.setRect(x, y, w, h)
        self.draw_guides()

    def draw_guides(self):
        if not self.guides_visible or not self.crop_rect:
            return
            
        # Önceki kılavuzları temizle
        for item in self.items():
            if isinstance(item, QGraphicsRectItem) and item != self.crop_rect:
                self.removeItem(item)
                
        # Kılavuz çizgileri çiz
        rect = self.crop_rect.rect()
        pen = QPen(QColor(255, 255, 255, 128), 1, Qt.PenStyle.DashLine)
        
        # Üçte bir çizgileri
        for i in range(1, 3):
            # Dikey çizgiler
            x = rect.x() + (rect.width() * i / 3)
            line = QGraphicsRectItem(x, rect.y(), 1, rect.height())
            line.setPen(pen)
            self.addItem(line)
            
            # Yatay çizgiler
            y = rect.y() + (rect.height() * i / 3)
            line = QGraphicsRectItem(rect.x(), y, rect.width(), 1)
            line.setPen(pen)
            self.addItem(line)

class CropGraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background: #1a1a1a;")

    def resizeEvent(self, event):
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

class CropWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Görüntüyü Kırp")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Grafik sahnesi
        self.scene = CropGraphicsScene()
        self.view = CropGraphicsView(self.scene)
        layout.addWidget(self.view)

        # Kontrol paneli
        controls = QHBoxLayout()

        # Kılavuz çizgileri seçeneği
        self.guide_check = QCheckBox("Kılavuz Çizgileri")
        self.guide_check.setChecked(True)
        self.guide_check.toggled.connect(self.toggle_guides)
        controls.addWidget(self.guide_check)

        # En-boy oranı kilidi
        self.ratio_check = QCheckBox("En-Boy Oranını Kilitle")
        self.ratio_check.toggled.connect(self.toggle_aspect_ratio)
        controls.addWidget(self.ratio_check)

        controls.addStretch()

        # İşlem butonları
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        controls.addWidget(self.cancel_btn)

        self.accept_btn = QPushButton("Onayla")
        self.accept_btn.clicked.connect(self.accept)
        controls.addWidget(self.accept_btn)

        layout.addLayout(controls)

        # Stiller
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
            }
        """)

    def set_image(self, image):
        try:
            if isinstance(image, QImage):
                pixmap = QPixmap.fromImage(image)
            elif isinstance(image, np.ndarray):
                height, width = image.shape[:2]
                bytes_per_line = 3 * width
                qimage = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
            else:
                pixmap = QPixmap(image)
                
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.scene.setSceneRect(pixmap.rect())
            self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        except Exception as e:
            print(f"set_image error: {str(e)}")  # Debug

    def toggle_guides(self, checked):
        self.scene.guides_visible = checked
        if self.scene.crop_rect:
            self.scene.draw_guides()

    def toggle_aspect_ratio(self, checked):
        self.scene.aspect_ratio_locked = checked
        if checked and self.scene.crop_rect:
            rect = self.scene.crop_rect.rect()
            self.scene.aspect_ratio = rect.width() / rect.height()

    def get_crop_rect(self):
        if self.scene.crop_rect:
            return self.scene.crop_rect.rect()
        return None