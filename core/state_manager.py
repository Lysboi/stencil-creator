import cv2
import numpy as np
import logging
import traceback
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import urllib.request

@dataclass
class StencilState:
    """Stencil durumunu tutan sınıf"""
    original_image: Optional[np.ndarray] = None
    processed_image: Optional[np.ndarray] = None
    stencil_type: str = "Temel"
    settings: Dict[str, Dict[str, Any]] = None
    last_modified: datetime = field(default_factory=datetime.now)
    model_downloaded: bool = False

    def __post_init__(self):
        if self.settings is None:
            self.settings = {
                "Temel": {
                    "threshold1": 50.0,
                    "threshold2": 150.0,
                    "blur": 5.0,
                    "line_thickness": 2.0
                },
                "Adaptif": {
                    "block_size": 11.0,
                    "c_value": 2.0,
                    "blur": 5.0,
                    "line_thickness": 2.0
                },
                "Karakalem": {
                    "darkness": 50.0,
                    "contrast": 50.0,
                    "line_thickness": 2.0
                },
                "Derin Stencil": {
                    "threshold": 50.0,
                    "line_thickness": 2.0,
                    "denoise": True
                },
                "Sanatsal Stencil": {
                    "detail_level": 50.0,
                    "contrast": 50.0,
                    "line_thickness": 2.0
                }
            }
            logging.info("Varsayılan ayarlar yüklendi")
            print("Varsayılan ayarlar:", self.settings)  # Debug

class StateManager:
    """Program durumunu yöneten sınıf"""
    MODEL_PATH = "models/hed_model.caffemodel"
    PROTO_PATH = "models/deploy.prototxt"
    MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/hed_pretrained_bsds.caffemodel"
    PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/master/hed/deploy.prototxt"

    def __init__(self):
        self.state = StencilState()
        self.history: List[np.ndarray] = []
        self.history_position: int = -1
        self.max_history: int = 10
        self.ensure_model_exists()
        logging.info("StateManager başlatıldı")

    def ensure_model_exists(self):
        """Model dosyalarının varlığını kontrol et ve indir"""
        try:
            if not os.path.exists('models'):
                os.makedirs('models')
                logging.info("Models klasörü oluşturuldu")

            if not os.path.exists(self.MODEL_PATH):
                logging.info("HED model indiriliyor...")
                urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_PATH)
                logging.info("HED model indirildi")

            if not os.path.exists(self.PROTO_PATH):
                logging.info("Proto dosyası indiriliyor...")
                urllib.request.urlretrieve(self.PROTO_URL, self.PROTO_PATH)
                logging.info("Proto dosyası indirildi")

            self.state.model_downloaded = True
        except Exception as e:
            logging.error(f"Model indirme hatası: {str(e)}")
            self.state.model_downloaded = False

    def set_original_image(self, image: np.ndarray) -> None:
        """Orijinal görüntüyü ayarla"""
        try:
            if image is None:
                logging.error("Boş görüntü yüklenmeye çalışıldı")
                return

            self.state.original_image = image.copy()
            self.state.last_modified = datetime.now()
            h, w = image.shape[:2]
            logging.info(f"Orijinal görüntü ayarlandı - Boyut: {w}x{h}")
            print(f"Orijinal görüntü ayarlandı: {w}x{h}")  # Debug
            
        except Exception as e:
            logging.error(f"Orijinal görüntü ayarlama hatası: {str(e)}")
            print(f"Orijinal görüntü hatası: {str(e)}")  # Debug
            logging.debug(traceback.format_exc())

    def set_processed_image(self, image: np.ndarray) -> None:
        """İşlenmiş görüntüyü ayarla ve geçmişe ekle"""
        try:
            if image is None:
                logging.error("Boş işlenmiş görüntü ayarlanmaya çalışıldı")
                return

            self.state.processed_image = image.copy()
            self.state.last_modified = datetime.now()
            self.add_to_history(image)
            h, w = image.shape[:2]
            logging.info(f"İşlenmiş görüntü ayarlandı - Boyut: {w}x{h}")
            print(f"İşlenmiş görüntü ayarlandı: {w}x{h}")  # Debug
            
        except Exception as e:
            logging.error(f"İşlenmiş görüntü ayarlama hatası: {str(e)}")
            print(f"İşlenmiş görüntü hatası: {str(e)}")  # Debug
            logging.debug(traceback.format_exc())

    def set_stencil_type(self, stencil_type: str) -> None:
        """Stencil tipini değiştir"""
        try:
            if stencil_type not in self.state.settings:
                logging.error(f"Geçersiz stencil tipi: {stencil_type}")
                print(f"Geçersiz stencil tipi: {stencil_type}")  # Debug
                return
                
            if stencil_type in ["Derin Stencil", "Sanatsal Stencil"] and not self.state.model_downloaded:
                logging.warning("Model henüz indirilmedi!")
                self.ensure_model_exists()

            self.state.stencil_type = stencil_type
            self.state.last_modified = datetime.now()
            logging.info(f"Stencil tipi değiştirildi: {stencil_type}")
            print(f"Stencil tipi değiştirildi: {stencil_type}")  # Debug
            print(f"Mevcut ayarlar: {self.state.settings[stencil_type]}")  # Debug
            
        except Exception as e:
            logging.error(f"Stencil tipi değiştirme hatası: {str(e)}")
            print(f"Stencil tipi değiştirme hatası: {str(e)}")  # Debug
            logging.debug(traceback.format_exc())

    def update_setting(self, setting_name: str, value: Any) -> None:
        """Belirli bir ayarı güncelle"""
        try:
            if self.state.stencil_type not in self.state.settings:
                logging.error(f"Geçersiz stencil tipi: {self.state.stencil_type}")
                print(f"Geçersiz stencil tipi: {self.state.stencil_type}")  # Debug
                return
                
            settings = self.state.settings[self.state.stencil_type]
            if setting_name not in settings:
                logging.error(f"Geçersiz ayar adı: {setting_name}")
                print(f"Geçersiz ayar adı: {setting_name}")  # Debug
                return
                
            old_value = settings[setting_name]
            
            # Boolean değerler için özel kontrol
            if isinstance(old_value, bool):
                settings[setting_name] = bool(value)
            else:
                settings[setting_name] = float(value)  # Diğer değerler float
                
            self.state.last_modified = datetime.now()
            
            logging.info(f"Ayar güncellendi: {setting_name} = {value} (eski: {old_value})")
            print(f"Ayar güncellendi: {setting_name} = {value} (eski: {old_value})")  # Debug
            print(f"Güncel ayarlar: {settings}")  # Debug
            
        except Exception as e:
            logging.error(f"Ayar güncelleme hatası: {str(e)}")
            print(f"Ayar güncelleme hatası: {str(e)}")  # Debug
            logging.debug(traceback.format_exc())

    def get_current_settings(self) -> Dict[str, Any]:
        """Mevcut stencil tipinin ayarlarını döndür"""
        try:
            if self.state.stencil_type not in self.state.settings:
                logging.error(f"Geçersiz stencil tipi: {self.state.stencil_type}")
                print(f"Geçersiz stencil tipi: {self.state.stencil_type}")  # Debug
                return {}
                
            settings = self.state.settings[self.state.stencil_type].copy()
            print(f"Mevcut ayarlar alınıyor: {settings}")  # Debug
            return settings
            
        except Exception as e:
            logging.error(f"Ayarları alma hatası: {str(e)}")
            print(f"Ayarları alma hatası: {str(e)}")  # Debug
            logging.debug(traceback.format_exc())
            return {}

    def add_to_history(self, image: np.ndarray) -> None:
        """Görüntüyü geçmişe ekle"""
        try:
            if image is None:
                logging.error("Boş görüntü geçmişe eklenmeye çalışıldı")
                return

            if self.history_position < len(self.history) - 1:
                removed_count = len(self.history) - (self.history_position + 1)
                self.history = self.history[:self.history_position + 1]
                logging.debug(f"{removed_count} geçmiş öğesi temizlendi")
            
            self.history.append(image.copy())
            self.history_position += 1
            
            if len(self.history) > self.max_history:
                self.history.pop(0)
                self.history_position -= 1
            
            logging.info(f"Geçmişe eklendi - Pozisyon: {self.history_position + 1}/{len(self.history)}")
            
        except Exception as e:
            logging.error(f"Geçmişe ekleme hatası: {str(e)}")
            logging.debug(traceback.format_exc())

    def undo(self) -> Optional[np.ndarray]:
        """Bir önceki duruma dön"""
        try:
            if not self.can_undo():
                logging.debug("Geri alınabilecek işlem yok")
                return None

            self.history_position -= 1
            self.state.processed_image = self.history[self.history_position].copy()
            logging.info(f"İşlem geri alındı - Yeni pozisyon: {self.history_position + 1}/{len(self.history)}")
            return self.state.processed_image
            
        except Exception as e:
            logging.error(f"Geri alma hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    def redo(self) -> Optional[np.ndarray]:
        """İleri al"""
        try:
            if not self.can_redo():
                logging.debug("İleri alınabilecek işlem yok")
                return None

            self.history_position += 1
            self.state.processed_image = self.history[self.history_position].copy()
            logging.info(f"İşlem yinelendi - Yeni pozisyon: {self.history_position + 1}/{len(self.history)}")
            return self.state.processed_image
            
        except Exception as e:
            logging.error(f"İleri alma hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    def can_undo(self) -> bool:
        """Geri alma yapılabilir mi?"""
        return self.history_position > 0

    def can_redo(self) -> bool:
        """İleri alma yapılabilir mi?"""
        return self.history_position < len(self.history) - 1