# ----------------------- PART 1: IMPORTS AND INITIAL SETUP START -----------------------
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
import logging
import traceback
import cv2
import numpy as np
from model_downloader import download_model  # YENİ: ModelDownloader import

from styles import DarkTheme
from widgets import ImageCropWidget
from core.state_manager import StateManager
from core.image_processor import ImageProcessor
from core.stencil_processors import StencilProcessor
from core.deep_processor import DeepProcessor
from components.tools_panel import StencilTools
from components.actions_panel import ActionsPanel
from components.menu_bar import MenuBar
from crop_window import CropWindow

def exception_hook(exctype, value, tb):
    logging.error(''.join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook
# ----------------------- PART 2: DOCK PANEL AND STENCIL CREATOR START -----------------------
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
       self.model_downloaders = []
       self.init_ui()
       self.check_models()
       
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
        # Yeni sinyal bağlantısı
        self.tools_panel.apply_model_settings.connect(self.on_model_settings_applied)
        
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
       self.menu_bar.download_models_requested.connect(self.download_models)
       
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
# ----------------------- PART 2: DOCK PANEL AND STENCIL CREATOR END -----------------------
# ----------------------- PART 3: MODEL AND IMAGE HANDLING METHODS START -----------------------
   def check_models(self):
      """Model dosyalarının varlığını kontrol et"""
      import sys
      
      # Ana dizini belirle (exe veya script konumuna göre)
      if getattr(sys, 'frozen', False):
          base_dir = os.path.dirname(sys.executable)
      else:
          base_dir = os.path.dirname(os.path.abspath(__file__))
      
      # Models klasörü yolu
      models_dir = os.path.join(base_dir, "models")
      
      model_paths = [
          os.path.join(models_dir, "hed_model.caffemodel"),
          os.path.join(models_dir, "deploy.prototxt")
      ]
      
      missing_models = False
      for path in model_paths:
          if not os.path.exists(path):
              missing_models = True
              break
              
      if missing_models:
          reply = QMessageBox.question(
              self,
              "Model Dosyaları Eksik",
              "Derin öğrenme modelleri bulunamadı. Şimdi indirmek ister misiniz?",
              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
          )
          if reply == QMessageBox.StandardButton.Yes:
              self.download_models()

   def download_models(self):
      """Derin öğrenme modellerini indir"""
      # Exe mi yoksa script olarak mı çalışıyor kontrol et
      import sys
      
      # Ana dizini belirle (exe veya script konumuna göre)
      if getattr(sys, 'frozen', False):
          base_dir = os.path.dirname(sys.executable)
      else:
          base_dir = os.path.dirname(os.path.abspath(__file__))
      
      # Models klasörünü ana dizinin altında oluştur
      models_dir = os.path.join(base_dir, "models")
      
      # Model bilgileri
      models = [
          {
              "name": "HED Model",
              "url": "https://raw.githubusercontent.com/ashukid/hed-edge-detector/refs/heads/master/hed_pretrained_bsds.caffemodel",
              "path": os.path.join(models_dir, "hed_model.caffemodel")
          },
          {
              "name": "Proto Dosyası",
              "url": "https://raw.githubusercontent.com/ashukid/hed-edge-detector/refs/heads/master/deploy.prototxt",
              "path": os.path.join(models_dir, "deploy.prototxt")
          }
      ]

      # Models dizini yoksa oluştur
      if not os.path.exists(models_dir):
          os.makedirs(models_dir)
          logging.info(f"Models dizini oluşturuldu: {models_dir}")

      # Modelleri indir
      for model in models:
          if not os.path.exists(model["path"]):
              downloader = download_model(model["url"], model["path"], self)
              self.model_downloaders.append(downloader)
              logging.info(f"İndirme başlatıldı: {model['path']}")

   def is_model_based_type(self, stencil_type):
      """Stencil tipinin model tabanlı olup olmadığını kontrol et"""
      return stencil_type in ["Derin Stencil", "Sanatsal Stencil"]
   
   def on_settings_changed(self, stencil_type, settings):
      """Normal stencil ayarları değiştiğinde"""
      if stencil_type not in ["Derin Stencil", "Sanatsal Stencil"]:
          self.state.set_stencil_type(stencil_type)
          for key, value in settings.items():
              self.state.update_setting(key, value)
          self.update_stencil()

   def on_model_settings_applied(self, stencil_type, settings):
       """Model tabanlı stencil ayarları onaylandığında"""
       # Model dosyalarını kontrol et - exe için düzeltilmiş yol
       import sys
       if getattr(sys, 'frozen', False):
           base_dir = os.path.dirname(sys.executable)
       else:
           base_dir = os.path.dirname(os.path.abspath(__file__))
           
       model_path = os.path.join(base_dir, "models", "hed_model.caffemodel")
       
       if not os.path.exists(model_path):
           reply = QMessageBox.question(
               self,
               "Model Eksik",
               "Bu stencil tipi için gerekli model dosyaları eksik. Şimdi indirmek ister misiniz?",
               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
           )
           if reply == QMessageBox.StandardButton.Yes:
               self.download_models()
           return
               
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
# ----------------------- PART 3: MODEL AND IMAGE HANDLING METHODS END -----------------------
# ----------------------- PART 4: IMAGE PROCESSING METHODS START -----------------------
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
       
       try:
           if stencil_type == "Temel":
               result = StencilProcessor.basic_stencil(
                   self.state.state.original_image,
                   settings
               )
           elif stencil_type == "Adaptif":
               result = StencilProcessor.adaptive_stencil(
                   self.state.state.original_image,
                   settings
               )
           elif stencil_type == "Karakalem":
               result = StencilProcessor.sketch_stencil(
                   self.state.state.original_image,
                   settings
               )
           elif stencil_type == "Derin Stencil":
               result = StencilProcessor.deep_stencil(
                   self.state.state.original_image,
                   settings
               )
           elif stencil_type == "Sanatsal Stencil":
               result = StencilProcessor.artistic_stencil(
                   self.state.state.original_image,
                   settings
               )
           
           if result is not None:
               print("İşlem başarılı, görüntü güncelleniyor...")  # Debug
               self.state.set_processed_image(result)
               self.update_display(result)
               print("Görüntü güncellendi")  # Debug
           else:
               print("HATA: İşlem başarısız oldu")  # Debug

       except Exception as e:
           print(f"Stencil dönüştürme hatası: {str(e)}")  # Debug
           logging.error(f"Stencil dönüştürme hatası: {str(e)}")
           traceback.print_exc()
           
       print("--- STENCIL DÖNÜŞTÜRME TAMAMLANDI ---\n")  # Debug
# ----------------------- PART 4: IMAGE PROCESSING METHODS END -----------------------
# ----------------------- PART 5: UTILITY METHODS AND MAIN START -----------------------
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
# ----------------------- PART 5: UTILITY METHODS AND MAIN END -----------------------