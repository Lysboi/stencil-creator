import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt6.QtCore import Qt
import logging
import traceback
import cv2
import numpy as np

from styles import DarkTheme
from widgets import ImageCropWidget
from core.state_manager import StateManager
from core.image_processor import ImageProcessor
from core.stencil_processors import StencilProcessor
from components.tools_panel import StencilTools
from components.actions_panel import ActionsPanel
from components.menu_bar import MenuBar
from crop_window import CropWindow

def exception_hook(exctype, value, tb):
    logging.error(''.join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

class DockPanel(QDockWidget):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | 
                        QDockWidget.DockWidgetFeature.DockWidgetFloatable |
                        QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        
class StencilCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.state = StateManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Stencil Oluşturucu")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(DarkTheme.MAIN_STYLE)
        
        # Merkez widget
        self.image_display = ImageCropWidget()
        self.setCentralWidget(self.image_display)
        
        # Menü bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.setup_menu_connections()
        
        # Paneller
        self.setup_panels()
        
        # Panel görünürlük durumlarını menüye ekle
        self.setup_view_toggles()
        
        logging.info("Program başlatıldı")
        
    def setup_panels(self):
        # Araçlar paneli
        self.tools_panel = StencilTools()
        tools_dock = DockPanel("Stencil Ayarları")
        tools_dock.setWidget(self.tools_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tools_dock)
        self.tools_panel.settings_changed.connect(self.on_settings_changed)
        
        # İşlemler paneli
        self.actions_panel = ActionsPanel()
        actions_dock = DockPanel("İşlemler")
        actions_dock.setWidget(self.actions_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, actions_dock)
        self.setup_action_connections()
        
        # Panelleri sakla
        self.dock_panels = {
            "Stencil Ayarları": tools_dock,
            "İşlemler": actions_dock
        }
        
    def setup_menu_connections(self):
        self.menu_bar.load_requested.connect(self.load_image)
        self.menu_bar.save_requested.connect(self.save_image)
        self.menu_bar.undo_requested.connect(self.undo)
        self.menu_bar.redo_requested.connect(self.redo)
        
    def setup_action_connections(self):
        self.actions_panel.load_requested.connect(self.load_image)
        self.actions_panel.crop_requested.connect(self.crop_image)
        self.actions_panel.convert_requested.connect(self.convert_to_stencil)
        self.actions_panel.undo_requested.connect(self.undo)
        self.actions_panel.redo_requested.connect(self.redo)
        self.actions_panel.save_requested.connect(self.save_image)
        
    def setup_view_toggles(self):
        for name, panel in self.dock_panels.items():
            self.menu_bar.add_view_toggle(name, panel.toggleViewAction().trigger)
            
    def on_settings_changed(self, stencil_type, settings):
        self.state.set_stencil_type(stencil_type)
        for key, value in settings.items():
            self.state.update_setting(key, value)
        self.update_stencil()
        
    def load_image(self):
        image = self.show_file_dialog("open")
        if image is not None:
            self.state.set_original_image(image)
            self.update_display(image)
            self.actions_panel.update_image_dependent_buttons(True)
            
    def save_image(self):
        if self.state.state.processed_image is not None:
            self.show_file_dialog("save", self.state.state.processed_image)
            
    def crop_image(self):
        print("Kırpma başladı")  # Debug
        try:
            if not hasattr(self, 'state') or self.state.state.original_image is None:
                print("Orijinal görüntü yok")  # Debug
                return

            print("CropWindow oluşturuluyor")  # Debug
            dialog = CropWindow(self)
            h, w = self.state.state.original_image.shape[:2]
            print(f"Görüntü boyutu: {w}x{h}")  # Debug

            # RGB'ye dönüştür
            rgb_image = cv2.cvtColor(self.state.state.original_image, cv2.COLOR_BGR2RGB)
            print("Görüntü RGB'ye dönüştürüldü")  # Debug
            
            dialog.set_image(rgb_image)
            print("Görüntü pencereye yüklendi")  # Debug
            
            if dialog.exec() == dialog.DialogCode.Accepted:
                print("Kırpma onaylandı")  # Debug
                rect = dialog.get_crop_rect()
                if rect:
                    x, y = int(rect.x()), int(rect.y())
                    w, h = int(rect.width()), int(rect.height())
                    cropped = self.state.state.original_image[y:y+h, x:x+w]
                    self.state.set_original_image(cropped)
                    self.update_display(cropped)
                    print(f"Kırpma tamamlandı: {w}x{h}")  # Debug

        except Exception as e:
            print(f"Kırpma hatası: {str(e)}")  # Debug
            logging.error(f"Kırpma hatası: {str(e)}")
            traceback.print_exc()
            
    def convert_to_stencil(self):
        print("\n--- STENCIL DÖNÜŞTÜRME BAŞLADI ---")  # Debug
        if self.state.state.original_image is None:
            print("HATA: Orijinal görüntü yok")  # Debug
            return
            
        stencil_type = self.state.state.stencil_type
        settings = self.state.get_current_settings()
        
        print(f"İşlem tipi: {stencil_type}")  # Debug
        print(f"Ayarlar: {settings}")  # Debug
        print(f"Orijinal görüntü boyutu: {self.state.state.original_image.shape}")  # Debug
        
        result = None
        
        if stencil_type == "Temel":
            print("Temel stencil işlemi başlatılıyor...")  # Debug
            result = StencilProcessor.basic_stencil(
                self.state.state.original_image,
                settings
            )
            print(f"Temel stencil sonucu: {'Başarılı' if result is not None else 'Başarısız'}")  # Debug
            if result is None:
                print("HATA: Temel stencil işlemi başarısız oldu")  # Debug
            else:
                print(f"Sonuç görüntü boyutu: {result.shape}")  # Debug

        elif stencil_type == "Adaptif":
            print("Adaptif stencil işlemi başlatılıyor...")  # Debug
            result = StencilProcessor.adaptive_stencil(
                self.state.state.original_image,
                settings
            )
            print(f"Adaptif stencil sonucu: {'Başarılı' if result is not None else 'Başarısız'}")  # Debug
            if result is None:
                print("HATA: Adaptif stencil işlemi başarısız oldu")  # Debug
            else:
                print(f"Sonuç görüntü boyutu: {result.shape}")  # Debug

        else:  # Karakalem
            result = StencilProcessor.sketch_stencil(
                self.state.state.original_image,
                settings
            )
            
        print(f"İşlem sonucu: {'Başarılı' if result is not None else 'Başarısız'}")  # Debug
            
        if result is not None:
            self.state.set_processed_image(result)
            self.update_display(result)
            print("Görüntü güncellendi")  # Debug
            
        print("--- STENCIL DÖNÜŞTÜRME TAMAMLANDI ---\n")  # Debug

    def update_stencil(self):
        if self.state.state.original_image is not None:
            self.convert_to_stencil()
            
    def undo(self):
        result = self.state.undo()
        if result is not None:
            self.update_display(result)
        self.update_undo_redo_state()
            
    def redo(self):
        result = self.state.redo()
        if result is not None:
            self.update_display(result)
        self.update_undo_redo_state()
            
    def update_display(self, image):
        self.image_display.display_image(image)
        
    def update_undo_redo_state(self):
        can_undo = self.state.can_undo()
        can_redo = self.state.can_redo()
        self.actions_panel.update_undo_redo_state(can_undo, can_redo)
        self.menu_bar.update_undo_redo_state(can_undo, can_redo)
        
    def show_file_dialog(self, dialog_type, image=None):
        from PyQt6.QtWidgets import QFileDialog
        import cv2
        import numpy as np
        
        try:
            if dialog_type == "open":
                file_name, _ = QFileDialog.getOpenFileName(
                    self, "Resim Seç", "", "Images (*.png *.jpg *.jpeg)"
                )
                if file_name:
                    with open(file_name, 'rb') as f:
                        file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        
            elif dialog_type == "save" and image is not None:
                file_name, _ = QFileDialog.getSaveFileName(
                    self, "Stencil'i Kaydet", "", "Images (*.png)"
                )
                if file_name:
                    _, buf = cv2.imencode('.png', image)
                    buf.tofile(file_name)
                    
        except Exception as e:
            logging.error(f"Dosya işlemi hatası: {str(e)}")
            
        return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StencilCreator()
    window.show()
    sys.exit(app.exec())