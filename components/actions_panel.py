from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal

class ActionsPanel(QWidget):
    """İşlem butonları paneli"""
    
    # Sinyaller
    load_requested = pyqtSignal()
    crop_requested = pyqtSignal()
    convert_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    save_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Butonlar
        buttons = [
            ("resim_yukle_button", "Resim Yükle", self.load_requested),
            ("kirp_button", "Kırp", self.crop_requested),
            ("stencil_button", "Stencil'e Dönüştür", self.convert_requested),
            ("geri_al_button", "Geri Al", self.undo_requested),
            ("yinele_button", "Yinele", self.redo_requested),
            ("kaydet_button", "Kaydet", self.save_requested)
        ]
        
        for btn_id, text, signal in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(signal.emit)
            layout.addWidget(btn)
            # Butonu sınıfın attribute'u olarak sakla
            setattr(self, btn_id, btn)
            
        layout.addStretch()
        
    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Geri al/yinele butonlarının durumunu güncelle"""
        self.geri_al_button.setEnabled(can_undo)
        self.yinele_button.setEnabled(can_redo)
        
    def update_image_dependent_buttons(self, has_image: bool):
        """Görüntü bağımlı butonların durumunu güncelle"""
        self.kirp_button.setEnabled(has_image)
        self.stencil_button.setEnabled(has_image)
        self.kaydet_button.setEnabled(has_image)