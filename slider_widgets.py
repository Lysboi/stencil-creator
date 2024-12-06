from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QDoubleSpinBox
from PyQt6.QtCore import Qt, pyqtSignal
import logging

class LabeledSlider(QWidget):
    """Etiketli slider widget"""
    
    # Değer değiştiğinde sinyal gönder
    valueChanged = pyqtSignal(float)
    
    def __init__(self, name, min_val, max_val, default_val, step=1, decimals=1):
        super().__init__()
        self.name = name
        self.decimals = decimals
        self.step = step
        self.setup_ui(min_val, max_val, default_val)
        
    def setup_ui(self, min_val, max_val, default_val):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Label
        self.label = QLabel(self.name)
        self.label.setFixedWidth(100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * (10 ** self.decimals)), 
                           int(max_val * (10 ** self.decimals)))
        self.slider.setValue(int(default_val * (10 ** self.decimals)))
        
        # SpinBox
        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setValue(default_val)
        self.spin.setSingleStep(self.step)
        self.spin.setDecimals(self.decimals)
        self.spin.setFixedWidth(70)
        self.spin.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Olayları bağla
        self.slider.valueChanged.connect(self._slider_changed)
        self.spin.valueChanged.connect(self._spin_changed)
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider, stretch=1)
        layout.addWidget(self.spin)
        self.setLayout(layout)
        
        # İlk değeri kaydet
        self._last_value = default_val
        logging.debug(f"Slider oluşturuldu: {self.name} - Değer: {default_val}")
        
    def _slider_changed(self, value):
        """Slider değeri değiştiğinde"""
        try:
            new_value = value / (10 ** self.decimals)
            if new_value != self._last_value:
                self.spin.setValue(new_value)
                self._last_value = new_value
                self.valueChanged.emit(new_value)
                logging.debug(f"Slider değişti: {self.name} = {new_value}")
        except Exception as e:
            logging.error(f"Slider değişim hatası: {str(e)}")
        
    def _spin_changed(self, value):
        """SpinBox değeri değiştiğinde"""
        try:
            if value != self._last_value:
                self.slider.setValue(int(value * (10 ** self.decimals)))
                self._last_value = value
                self.valueChanged.emit(value)
                logging.debug(f"SpinBox değişti: {self.name} = {value}")
        except Exception as e:
            logging.error(f"SpinBox değişim hatası: {str(e)}")
        
    def value(self) -> float:
        """Mevcut değeri döndür"""
        return self.spin.value()
        
    def setValue(self, value: float):
        """Değeri ayarla"""
        try:
            self.spin.setValue(value)
            logging.debug(f"Değer ayarlandı: {self.name} = {value}")
        except Exception as e:
            logging.error(f"Değer ayarlama hatası: {str(e)}")
