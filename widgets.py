from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QTextEdit, QComboBox
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QImage, QPixmap
import logging
import cv2
from utils import QTextEditLogger

class ImageCropWidget(QLabel):
    """Ana görüntü gösterme alanı"""
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                border: 2px solid #2d2d2d;
                border-radius: 4px;
            }
        """)

    def display_image(self, image):
        try:
            if len(image.shape) == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
                
            h, w = rgb_image.shape[:2]
            label_w = self.width()
            label_h = self.height()
            
            scale = min(label_w/w, label_h/h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            
            bytes_per_line = 3 * w if len(image.shape) == 3 else w
            
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line,
                            QImage.Format.Format_RGB888 if len(image.shape) == 3 
                            else QImage.Format.Format_Grayscale8)
            
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(new_w, new_h, 
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(scaled_pixmap)
            logging.info(f"Görüntü başarıyla gösterildi: {w}x{h}")
            
        except Exception as e:
            logging.error(f"Görüntü gösterme hatası: {str(e)}")

class ConsoleWidget(QWidget):
    """Konsol penceresi"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        self.setLayout(layout)
        
        self.log_handler = QTextEditLogger(self.console)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

class StencilTypeSelector(QComboBox):
    """Stencil tipi seçim kutusu"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems([
            'Temel', 
            'Adaptif', 
            'Karakalem',
            'Derin Stencil',  # Yeni eklenen
            'Sanatsal Stencil'  # Yeni eklenen
        ])
        self.setMaximumWidth(200)
        self.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                border-left: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QComboBox::down-arrow {
                border: solid #ffffff;
                border-width: 0 2px 2px 0;
                padding: 3px;
                transform: rotate(45deg);
                margin-top: -5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #3d3d3d;
                border: none;
            }
            QComboBox:hover {
                background-color: #3d3d3d;
            }
        """)