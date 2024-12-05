import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QAction
import cv2
import numpy as np
import io
import logging

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
        
        # Logger setup
        self.log_handler = QTextEditLogger(self.console)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class StencilCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Stencil Oluşturucu")
        self.setMinimumSize(1000, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QSlider {
                background-color: #2d2d2d;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)
        
        # Menü bar
        self.create_menu_bar()
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Sol panel - Araçlar
        tools_panel = QWidget()
        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Stencil ayarları
        self.threshold1 = QSlider(Qt.Orientation.Horizontal)
        self.threshold1.setRange(0, 255)
        self.threshold1.setValue(50)
        self.threshold1.valueChanged.connect(self.update_stencil)
        
        self.threshold2 = QSlider(Qt.Orientation.Horizontal)
        self.threshold2.setRange(0, 255)
        self.threshold2.setValue(150)
        self.threshold2.valueChanged.connect(self.update_stencil)
        
        self.blur = QSlider(Qt.Orientation.Horizontal)
        self.blur.setRange(1, 21)
        self.blur.setValue(5)
        self.blur.valueChanged.connect(lambda x: self.update_stencil() if x % 2 == 1 else None)
        
        tools_layout.addWidget(QLabel("Kenar Algılama - Alt"))
        tools_layout.addWidget(self.threshold1)
        tools_layout.addWidget(QLabel("Kenar Algılama - Üst"))
        tools_layout.addWidget(self.threshold2)
        tools_layout.addWidget(QLabel("Bulanıklık"))
        tools_layout.addWidget(self.blur)
        
        layout.addWidget(tools_panel)
        
        # Orta panel - Görüntü
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        
        self.image_label = ImageCropWidget()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 500)
        self.image_label.setStyleSheet("border: 1px solid #3d3d3d;")
        center_layout.addWidget(self.image_label)
        
        button_layout = QHBoxLayout()
        
        self.load_button = QPushButton("Resim Yükle")
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)
        
        self.crop_button = QPushButton("Kırp")
        self.crop_button.clicked.connect(self.crop_image)
        button_layout.addWidget(self.crop_button)
        
        self.convert_button = QPushButton("Stencil'e Dönüştür")
        self.convert_button.clicked.connect(self.convert_to_stencil)
        button_layout.addWidget(self.convert_button)
        
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_button)
        
        center_layout.addLayout(button_layout)
        layout.addWidget(center_panel)
        
        # Console
        self.console_widget = ConsoleWidget()
        self.console_widget.hide()
        layout.addWidget(self.console_widget)
        
        self.original_image = None
        self.processed_image = None
        
        logging.info("Program başlatıldı")

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menüsü
        file_menu = menubar.addMenu('Dosya')
        
        open_action = QAction('Aç', self)
        open_action.triggered.connect(self.load_image)
        file_menu.addAction(open_action)
        
        save_action = QAction('Kaydet', self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        
        # View menüsü
        view_menu = menubar.addMenu('Görünüm')
        
        console_action = QAction('Konsol', self, checkable=True)
        console_action.triggered.connect(self.toggle_console)
        view_menu.addAction(console_action)

    def toggle_console(self, state):
        self.console_widget.setVisible(state)

    def load_image(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Images (*.png *.jpg *.jpeg)")
            if file_name:
                with open(file_name, 'rb') as f:
                    file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                    self.original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if self.original_image is not None:
                    self.display_image(self.original_image)
                    logging.info(f"Resim yüklendi: {file_name}")
                else:
                    logging.error("Resim yüklenemedi!")
        except Exception as e:
            logging.error(f"Resim yükleme hatası: {str(e)}")

    def crop_image(self):
        if self.original_image is None or self.image_label.crop_rect is None:
            return
            
        rect = self.image_label.crop_rect
        pixmap = self.image_label.pixmap()
        
        # Koordinatları orijinal görüntü boyutuna ölçekle
        scale_x = self.original_image.shape[1] / pixmap.width()
        scale_y = self.original_image.shape[0] / pixmap.height()
        
        x = int(rect.x() * scale_x)
        y = int(rect.y() * scale_y)
        w = int(rect.width() * scale_x)
        h = int(rect.height() * scale_y)
        
        self.original_image = self.original_image[y:y+h, x:x+w]
        self.display_image(self.original_image)
        self.image_label.crop_rect = None
        logging.info("Resim kırpıldı")

    def convert_to_stencil(self):
        if self.original_image is None:
            return
            
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        blur_value = self.blur.value() if self.blur.value() % 2 == 1 else self.blur.value() + 1
        blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
        edges = cv2.Canny(blurred, self.threshold1.value(), self.threshold2.value())
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        self.processed_image = cv2.bitwise_not(edges)
        self.display_image(self.processed_image)
        logging.info("Stencil oluşturuldu")

    def update_stencil(self):
        if self.original_image is not None and hasattr(self, 'processed_image'):
            self.convert_to_stencil()

    def save_image(self):
        if self.processed_image is None:
            return

        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Stencil'i Kaydet", "", "Images (*.png)")
            if file_name:
                _, buf = cv2.imencode('.png', self.processed_image)
                buf.tofile(file_name)
                logging.info(f"Stencil kaydedildi: {file_name}")
        except Exception as e:
            logging.error(f"Kaydetme hatası: {str(e)}")

    def display_image(self, image):
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            h, w = image.shape[:2]
            
            # En-boy oranını koru
            label_w = self.image_label.width()
            label_h = self.image_label.height()
            
            scale = min(label_w/w, label_h/h)
            new_w = int(w * scale)
            new_h = int(h * scale)
                
            format = QImage.Format.Format_Grayscale8 if len(image.shape) == 2 else QImage.Format.Format_RGB888
            qt_image = QImage(image.data, w, h, image.strides[0], format)
            
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            logging.error(f"Görüntü gösterme hatası: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StencilCreator()
    window.show()
    sys.exit(app.exec())