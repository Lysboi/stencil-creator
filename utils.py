import logging
from PyQt6.QtWidgets import QTextEdit
import cv2
import numpy as np

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

def process_stencil(image, threshold1, threshold2, blur_size, line_thickness):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_value = blur_size if blur_size % 2 == 1 else blur_size + 1
    blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
    edges = cv2.Canny(blurred, threshold1, threshold2)
    
    # Çizgi kalınlığı ayarı
    kernel = np.ones((line_thickness, line_thickness), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    return cv2.bitwise_not(edges)