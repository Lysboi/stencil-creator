from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget, QCheckBox, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from widgets import StencilTypeSelector
from slider_widgets import LabeledSlider
import logging

class StencilTools(QWidget):
    """Stencil araçları paneli"""
    
    # Sinyaller
    settings_changed = pyqtSignal(str, dict)  # (stencil_type, settings)
    apply_model_settings = pyqtSignal(str, dict)  # Model tabanlı işlemler için

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
        
        # Derin Stencil Ayarları
        self.deep_settings = self.create_deep_settings()
        self.settings_stack.addWidget(self.deep_settings)
        
        # Sanatsal Stencil Ayarları
        self.artistic_settings = self.create_artistic_settings()
        self.settings_stack.addWidget(self.artistic_settings)
        
        layout.addWidget(self.settings_stack)
        
        # Onayla butonu
        self.apply_button = QPushButton("Onayla")
        self.apply_button.clicked.connect(self.on_apply_clicked)
        self.apply_button.hide()
        layout.addWidget(self.apply_button)
        
        layout.addStretch()
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
            self.connect_slider(slider, self.on_basic_settings_changed)
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
            self.connect_slider(slider, self.on_adaptive_settings_changed)
            layout.addWidget(slider)
            
        return widget

    def create_sketch_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.darkness = LabeledSlider("Koyuluk", 0, 100, 50)
        self.contrast = LabeledSlider("Kontrast", 0, 100, 50)
        self.sketch_thickness = LabeledSlider("Çizgi Kalınlığı", 0.5, 10, 2, 0.1, 1)
        
        for slider in [self.darkness, self.contrast, self.sketch_thickness]:
            self.connect_slider(slider, self.on_sketch_settings_changed)
            layout.addWidget(slider)
            
        return widget

    def create_deep_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Detay kontrolü
        self.detail_level = LabeledSlider("Detay Seviyesi", 0, 100, 50)
        self.edge_sensitivity = LabeledSlider("Kenar Hassasiyeti", 0, 100, 50)
        self.detail_preservation = LabeledSlider("Detay Koruma", 0, 100, 70)
        
        # Çizgi kontrolü
        self.min_line_width = LabeledSlider("Min Çizgi Kalınlığı", 0.5, 5, 1, 0.1, 1)
        self.max_line_width = LabeledSlider("Max Çizgi Kalınlığı", 1, 10, 3, 0.1, 1)
        
        # Görüntü ayarları
        self.contrast_boost = LabeledSlider("Kontrast", 0.5, 3.0, 1.5, 0.1, 1)
        self.smoothness = LabeledSlider("Yumuşaklık", 0, 100, 30)
        
        sliders = [
            self.detail_level, self.edge_sensitivity, self.detail_preservation,
            self.min_line_width, self.max_line_width, self.contrast_boost,
            self.smoothness
        ]
        
        for slider in sliders:
            self.connect_slider(slider, self.on_deep_settings_changed)
            layout.addWidget(slider)
        
        return widget

    def create_artistic_settings(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Detay kontrolü
        self.artistic_detail = LabeledSlider("Detay Seviyesi", 0, 100, 50)
        self.artistic_edge = LabeledSlider("Kenar Hassasiyeti", 0, 100, 70)
        self.artistic_preservation = LabeledSlider("Detay Koruma", 0, 100, 85)
        
        # Çizgi kontrolü
        self.artistic_min_width = LabeledSlider("Min Çizgi Kalınlığı", 0.5, 5, 1.5, 0.1, 1)
        self.artistic_max_width = LabeledSlider("Max Çizgi Kalınlığı", 1, 10, 4, 0.1, 1)
        
        # Görüntü ayarları
        self.artistic_contrast = LabeledSlider("Kontrast", 0.5, 3.0, 2.0, 0.1, 1)
        self.artistic_smoothness = LabeledSlider("Yumuşaklık", 0, 100, 20)
        
        sliders = [
            self.artistic_detail, self.artistic_edge, self.artistic_preservation,
            self.artistic_min_width, self.artistic_max_width, self.artistic_contrast,
            self.artistic_smoothness
        ]
        
        for slider in sliders:
            self.connect_slider(slider, self.on_artistic_settings_changed)
            layout.addWidget(slider)
        
        return widget

    def connect_slider(self, slider, callback):
        """Slider'a callback bağla"""
        slider.valueChanged.connect(callback)

    def is_model_based(self, stencil_type):
        """Stencil tipinin model tabanlı olup olmadığını kontrol et"""
        return stencil_type in ["Derin Stencil", "Sanatsal Stencil"]
        
    def on_type_changed(self, index):
        stencil_type = self.stencil_type.currentText()
        self.settings_stack.setCurrentIndex(index)
        
        # Model tabanlı işlemler için buton görünürlüğünü ayarla
        self.apply_button.setVisible(self.is_model_based(stencil_type))
        
        # Model tabanlı olmayan işlemler için hemen güncelle
        if not self.is_model_based(stencil_type):
            self.emit_current_settings()
    
    def on_basic_settings_changed(self):
        if self.stencil_type.currentText() == "Temel":
            self.emit_current_settings()
            
    def on_adaptive_settings_changed(self):
        if self.stencil_type.currentText() == "Adaptif":
            self.emit_current_settings()
            
    def on_sketch_settings_changed(self):
        if self.stencil_type.currentText() == "Karakalem":
            self.emit_current_settings()

    def on_deep_settings_changed(self):
        # Sadece ayarları güncelle, görüntüyü güncelleme
        pass

    def on_artistic_settings_changed(self):
        # Sadece ayarları güncelle, görüntüyü güncelleme
        pass
            
    def get_current_settings(self):
        """Mevcut ayarları al"""
        stencil_type = self.stencil_type.currentText()
        
        if stencil_type == "Temel":
            return {
                "threshold1": self.threshold1.value(),
                "threshold2": self.threshold2.value(),
                "blur": self.basic_blur.value(),
                "line_thickness": self.basic_thickness.value()
            }
        elif stencil_type == "Adaptif":
            return {
                "block_size": self.block_size.value(),
                "c_value": self.c_value.value(),
                "blur": self.adaptive_blur.value(),
                "line_thickness": self.adaptive_thickness.value()
            }
        elif stencil_type == "Karakalem":
            return {
                "darkness": self.darkness.value(),
                "contrast": self.contrast.value(),
                "line_thickness": self.sketch_thickness.value()
            }
        elif stencil_type == "Derin Stencil":
            return {
                "detail_level": self.detail_level.value(),
                "edge_sensitivity": self.edge_sensitivity.value(),
                "detail_preservation": self.detail_preservation.value(),
                "min_line_width": self.min_line_width.value(),
                "max_line_width": self.max_line_width.value(),
                "contrast_boost": self.contrast_boost.value(),
                "smoothness": self.smoothness.value()
            }
        elif stencil_type == "Sanatsal Stencil":
            return {
                "detail_level": self.artistic_detail.value(),
                "edge_sensitivity": self.artistic_edge.value(),
                "detail_preservation": self.artistic_preservation.value(),
                "min_line_width": self.artistic_min_width.value(),
                "max_line_width": self.artistic_max_width.value(),
                "contrast_boost": self.artistic_contrast.value(),
                "smoothness": self.artistic_smoothness.value()
            }
        return {}
            
    def emit_current_settings(self):
        stencil_type = self.stencil_type.currentText()
        settings = self.get_current_settings()
        
        # Model tabanlı olmayan işlemler için direkt sinyal gönder
        if not self.is_model_based(stencil_type):
            self.settings_changed.emit(stencil_type, settings)
            logging.debug(f"Ayarlar gönderildi - Tip: {stencil_type}, Ayarlar: {settings}")

    def on_apply_clicked(self):
        """Onayla butonuna tıklandığında"""
        if self.is_model_based(self.stencil_type.currentText()):
            stencil_type = self.stencil_type.currentText()
            settings = self.get_current_settings()
            self.apply_model_settings.emit(stencil_type, settings)