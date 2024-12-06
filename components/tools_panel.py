from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSignal
from widgets import StencilTypeSelector
from slider_widgets import LabeledSlider
import logging

class StencilTools(QWidget):
    """Stencil araçları paneli"""
    
    # Sinyaller
    settings_changed = pyqtSignal(str, dict)  # (stencil_type, settings)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Stencil Tipi Seçici
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Stencil Tipi"))
        self.stencil_type = StencilTypeSelector()
        self.stencil_type.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.stencil_type)
        layout.addLayout(type_layout)
        
        # Ayarlar için StackedWidget
        self.settings_stack = QStackedWidget()
        
        # Temel Stencil Ayarları
        self.basic_settings = self.create_basic_settings()
        self.settings_stack.addWidget(self.basic_settings)
        
        # Adaptif Stencil Ayarları
        self.adaptive_settings = self.create_adaptive_settings()
        self.settings_stack.addWidget(self.adaptive_settings)
        
        # Karakalem Ayarları
        self.sketch_settings = self.create_sketch_settings()
        self.settings_stack.addWidget(self.sketch_settings)
        
        layout.addWidget(self.settings_stack)
        layout.addStretch()
        
        # İlk ayarları gönder
        self.emit_current_settings()
        logging.info("Tools panel başlatıldı")
        
    def create_basic_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.threshold1 = LabeledSlider("Alt Eşik", 0, 255, 50)
        self.threshold2 = LabeledSlider("Üst Eşik", 0, 255, 150)
        self.basic_blur = LabeledSlider("Bulanıklık", 1, 21, 5)
        self.basic_thickness = LabeledSlider("Çizgi Kalınlığı", 0.5, 10, 2, 0.1, 1)
        
        for slider in [self.threshold1, self.threshold2, self.basic_blur, self.basic_thickness]:
            slider.slider.valueChanged.connect(lambda: self.on_basic_settings_changed())
            layout.addWidget(slider)
            
        return widget
        
    def create_adaptive_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.block_size = LabeledSlider("Block Size", 3, 99, 11, 2)
        self.c_value = LabeledSlider("C Değeri", -50, 100, 2, 1)
        self.adaptive_blur = LabeledSlider("Bulanıklık", 1, 21, 5)
        self.adaptive_thickness = LabeledSlider("Çizgi Kalınlığı", 0.5, 10, 2, 0.1, 1)
        
        for slider in [self.block_size, self.c_value, self.adaptive_blur, self.adaptive_thickness]:
            slider.slider.valueChanged.connect(lambda: self.on_adaptive_settings_changed())
            layout.addWidget(slider)
            
        return widget
        
    def create_sketch_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.darkness = LabeledSlider("Koyuluk", 0, 100, 50)
        self.contrast = LabeledSlider("Kontrast", 0, 100, 50)
        self.sketch_thickness = LabeledSlider("Çizgi Kalınlığı", 0.5, 10, 2, 0.1, 1)
        
        for slider in [self.darkness, self.contrast, self.sketch_thickness]:
            slider.slider.valueChanged.connect(lambda: self.on_sketch_settings_changed())
            layout.addWidget(slider)
            
        return widget
        
    def on_type_changed(self, index):
        self.settings_stack.setCurrentIndex(index)
        self.emit_current_settings()
        logging.debug(f"Stencil tipi değiştirildi: {self.stencil_type.currentText()}")
        
    def on_basic_settings_changed(self):
        if self.stencil_type.currentText() == "Temel":
            self.emit_current_settings()
            logging.debug("Temel ayarlar güncellendi")
            
    def on_adaptive_settings_changed(self):
        if self.stencil_type.currentText() == "Adaptif":
            self.emit_current_settings()
            logging.debug("Adaptif ayarlar güncellendi")
            
    def on_sketch_settings_changed(self):
        if self.stencil_type.currentText() == "Karakalem":
            self.emit_current_settings()
            logging.debug("Karakalem ayarlar güncellendi")
            
    def emit_current_settings(self):
        stencil_type = self.stencil_type.currentText()
        settings = {}
        
        if stencil_type == "Temel":
            settings = {
                "threshold1": self.threshold1.value(),
                "threshold2": self.threshold2.value(),
                "blur": self.basic_blur.value(),
                "line_thickness": self.basic_thickness.value()
            }
        elif stencil_type == "Adaptif":
            settings = {
                "block_size": self.block_size.value(),
                "c_value": self.c_value.value(),
                "blur": self.adaptive_blur.value(),
                "line_thickness": self.adaptive_thickness.value()
            }
        else:  # Karakalem
            settings = {
                "darkness": self.darkness.value(),
                "contrast": self.contrast.value(),
                "line_thickness": self.sketch_thickness.value()
            }
            
        self.settings_changed.emit(stencil_type, settings)
        logging.debug(f"Ayarlar gönderildi - Tip: {stencil_type}, Ayarlar: {settings}")