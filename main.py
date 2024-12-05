import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import cv2
import numpy as np
import os

class StencilCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stencil Oluşturucu")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(780, 500)
        self.image_label.setStyleSheet("border: 1px solid black;")
        layout.addWidget(self.image_label)
        
        button_layout = QVBoxLayout()
        
        self.load_button = QPushButton("Resim Yükle")
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)
        
        self.convert_button = QPushButton("Stencil'e Dönüştür")
        self.convert_button.clicked.connect(self.convert_to_stencil)
        button_layout.addWidget(self.convert_button)
        
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.original_image = None
        self.processed_image = None

    def load_image(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Images (*.png *.jpg *.jpeg)")
            if file_name:
                # NumPy ile resmi oku
                with open(file_name, 'rb') as f:
                    file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                    self.original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if self.original_image is not None:
                    self.display_image(self.original_image)
                else:
                    QMessageBox.warning(self, "Hata", "Resim yüklenemedi!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Resim yükleme hatası: {str(e)}")

    def convert_to_stencil(self):
        if self.original_image is None:
            return
            
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        self.processed_image = cv2.bitwise_not(edges)
        self.display_image(self.processed_image)

    def save_image(self):
        if self.processed_image is None:
            return

        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Stencil'i Kaydet", "", "Images (*.png)")
            if file_name:
                # NumPy ile kaydet
                _, buf = cv2.imencode('.png', self.processed_image)
                buf.tofile(file_name)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {str(e)}")

    def display_image(self, image):
        try:
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            h, w = image.shape[:2]
            max_w = self.image_label.width()
            max_h = self.image_label.height()
            
            aspect_ratio = w/h
            if w > h:
                new_w = min(max_w, w)
                new_h = int(new_w/aspect_ratio)
            else:
                new_h = min(max_h, h)
                new_w = int(new_h*aspect_ratio)
                
            format = QImage.Format.Format_Grayscale8 if len(image.shape) == 2 else QImage.Format.Format_RGB888
            qt_image = QImage(image.data, w, h, image.strides[0], format)
            
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(new_w, new_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Görüntü gösterme hatası: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StencilCreator()
    window.show()
    sys.exit(app.exec())