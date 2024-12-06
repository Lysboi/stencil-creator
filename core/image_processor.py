import cv2
import numpy as np
import logging
from typing import Optional, Tuple, Dict, Any
import traceback

class ImageProcessor:
    """Görüntü işleme sınıfı"""
    
    @staticmethod
    def check_image(image: np.ndarray) -> bool:
        """Görüntünün geçerli olup olmadığını kontrol et"""
        try:
            if image is None:
                logging.error("Görüntü boş")
                return False
                
            if not isinstance(image, np.ndarray):
                logging.error(f"Geçersiz görüntü tipi: {type(image)}")
                return False
                
            if len(image.shape) not in [2, 3]:
                logging.error(f"Geçersiz görüntü boyutu: {image.shape}")
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"Görüntü kontrol hatası: {str(e)}")
            return False
    
    @staticmethod
    def preprocess_image(image: np.ndarray, blur_size: int) -> Optional[np.ndarray]:
        """Görüntüyü ön işleme"""
        try:
            if not ImageProcessor.check_image(image):
                return None
                
            # Gri tonlamaya çevir
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                logging.debug("Görüntü gri tonlamaya çevrildi")
            else:
                gray = image
                
            # Bulanıklaştır
            blur_value = blur_size if blur_size % 2 == 1 else blur_size + 1
            blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
            logging.debug(f"Gaussian blur uygulandı: {blur_value}x{blur_value}")
            
            return blurred
            
        except Exception as e:
            logging.error(f"Ön işleme hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def auto_brightness_contrast(image: np.ndarray) -> Tuple[float, float]:
        """Otomatik parlaklık ve kontrast değerlerini hesapla"""
        try:
            if not ImageProcessor.check_image(image):
                return 1.0, 0.0
                
            # Görüntü istatistiklerini hesapla
            min_val = np.percentile(image, 1)
            max_val = np.percentile(image, 99)
            
            # Kontrastı hesapla
            if max_val - min_val > 0:
                alpha = 255.0 / (max_val - min_val)
            else:
                alpha = 1.0
                
            # Parlaklığı hesapla
            beta = -min_val * alpha
            
            logging.debug(f"Otomatik değerler - Kontrast: {alpha:.2f}, Parlaklık: {beta:.2f}")
            return alpha, beta
            
        except Exception as e:
            logging.error(f"Otomatik ayar hesaplama hatası: {str(e)}")
            return 1.0, 0.0
            
    @staticmethod
    def resize_image(image: np.ndarray, 
                    width: Optional[int] = None, 
                    height: Optional[int] = None, 
                    keep_aspect: bool = True) -> Optional[np.ndarray]:
        """Görüntüyü yeniden boyutlandır"""
        try:
            if not ImageProcessor.check_image(image):
                return None
                
            orig_h, orig_w = image.shape[:2]
            logging.debug(f"Orijinal boyut: {orig_w}x{orig_h}")
            
            if width is None and height is None:
                logging.error("En az bir boyut belirtilmeli")
                return None
                
            if keep_aspect:
                if width is None:
                    width = int(height * orig_w / orig_h)
                elif height is None:
                    height = int(width * orig_h / orig_w)
                else:
                    # En-boy oranını koru
                    if width/height > orig_w/orig_h:
                        width = int(height * orig_w / orig_h)
                    else:
                        height = int(width * orig_h / orig_w)
                        
            else:
                if width is None:
                    width = orig_w
                if height is None:
                    height = orig_h
                    
            resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
            logging.info(f"Yeni boyut: {width}x{height}")
            return resized
            
        except Exception as e:
            logging.error(f"Yeniden boyutlandırma hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def adjust_image(image: np.ndarray, 
                    brightness: float = 0, 
                    contrast: float = 1.0, 
                    gamma: float = 1.0) -> Optional[np.ndarray]:
        """Görüntü parlaklık, kontrast ve gamma ayarları"""
        try:
            if not ImageProcessor.check_image(image):
                return None
                
            # Kontrast ve parlaklık
            adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
            
            # Gamma düzeltmesi
            if gamma != 1.0:
                inv_gamma = 1.0 / gamma
                table = np.array([((i / 255.0) ** inv_gamma) * 255
                                for i in np.arange(0, 256)]).astype("uint8")
                adjusted = cv2.LUT(adjusted, table)
                
            logging.debug(f"Görüntü ayarlandı - Parlaklık: {brightness}, Kontrast: {contrast}, Gamma: {gamma}")
            return adjusted
            
        except Exception as e:
            logging.error(f"Görüntü ayarlama hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def normalize_image(image: np.ndarray) -> Optional[np.ndarray]:
        """Görüntüyü normalize et"""
        try:
            if not ImageProcessor.check_image(image):
                return None
                
            normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
            logging.debug("Görüntü normalize edildi")
            return normalized
            
        except Exception as e:
            logging.error(f"Normalizasyon hatası: {str(e)}")
            return None