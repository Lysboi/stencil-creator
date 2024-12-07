import cv2
import numpy as np
import logging
import traceback
from core.deep_processor import DeepProcessor
from core.advanced_sketch_processor import AdvancedSketchProcessor

class StencilProcessor:
    """Stencil işleme sınıfı"""
    
    _deep_processor = None
    _advanced_processor = AdvancedSketchProcessor()
    
    @classmethod
    def get_deep_processor(cls):
        if cls._deep_processor is None:
            cls._deep_processor = DeepProcessor()
        return cls._deep_processor
    
    @staticmethod
    def deep_stencil(image: np.ndarray, settings: dict) -> np.ndarray:
        """Derin öğrenme tabanlı stencil işlemi"""
        try:
            print("Derin stencil başladı:", settings)  # Debug
            return StencilProcessor._advanced_processor.portrait_to_sketch(image, settings)
        except Exception as e:
            print(f"Derin stencil hatası: {str(e)}")  # Debug
            logging.error(f"Derin stencil hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def artistic_stencil(image: np.ndarray, settings: dict) -> np.ndarray:
        """Sanatsal stencil işlemi"""
        try:
            print("Sanatsal stencil başladı:", settings)  # Debug
            return StencilProcessor._advanced_processor.artistic_sketch(image, settings)
        except Exception as e:
            print(f"Sanatsal stencil hatası: {str(e)}")  # Debug
            logging.error(f"Sanatsal stencil hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def basic_stencil(image: np.ndarray, settings: dict) -> np.ndarray:
        """Temel stencil işlemi"""
        try:
            print("Basic stencil başladı:", settings)  # Debug
            
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("Gri tonlama tamamlandı")  # Debug
            
            # Bulanıklaştır
            blur = int(settings.get("blur", 5))
            blur_value = blur if blur % 2 == 1 else blur + 1
            blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
            print(f"Bulanıklaştırma tamamlandı: {blur_value}")  # Debug
            
            # Kenar tespiti
            threshold1 = float(settings.get("threshold1", 50))
            threshold2 = float(settings.get("threshold2", 150))
            edges = cv2.Canny(blurred, threshold1, threshold2)
            print(f"Kenar tespiti tamamlandı: {threshold1}, {threshold2}")  # Debug
            
            # Çizgileri kalınlaştır
            thickness = float(settings.get("line_thickness", 2))
            kernel_size = max(1, int(thickness))
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            dilated = cv2.dilate(edges, kernel, iterations=1)
            print(f"Çizgiler kalınlaştırıldı: {thickness}")  # Debug
            
            result = cv2.bitwise_not(dilated)
            print("Basic stencil tamamlandı")  # Debug
            
            return result
            
        except Exception as e:
            print(f"Basic stencil hatası: {str(e)}")  # Debug
            logging.error(f"Basic stencil hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def adaptive_stencil(image: np.ndarray, settings: dict) -> np.ndarray:
        """Adaptif stencil işlemi"""
        try:
            print("Adaptif stencil başladı:", settings)  # Debug
            
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("Gri tonlama tamamlandı")  # Debug
            
            # Bulanıklaştır
            blur = int(settings.get("blur", 5))
            blur_value = blur if blur % 2 == 1 else blur + 1
            blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
            print(f"Bulanıklaştırma tamamlandı: {blur_value}")  # Debug
            
            # Adaptif eşikleme
            block_size = int(float(settings.get("block_size", 11)))
            c_value = float(settings.get("c_value", 2))
            
            if block_size % 2 == 0:
                block_size += 1
            
            thresh = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                block_size,
                c_value
            )
            print(f"Adaptif eşikleme tamamlandı: block={block_size}, c={c_value}")  # Debug
            
            # Çizgileri kalınlaştır
            thickness = float(settings.get("line_thickness", 2))
            kernel_size = max(1, int(thickness))
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            print(f"Çizgiler kalınlaştırıldı: {thickness}")  # Debug
            
            print("Adaptif stencil tamamlandı")  # Debug
            return dilated
            
        except Exception as e:
            print(f"Adaptif stencil hatası: {str(e)}")  # Debug
            logging.error(f"Adaptif stencil hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None

    @staticmethod
    def sketch_stencil(image: np.ndarray, settings: dict) -> np.ndarray:
        """Karakalem stencil işlemi"""
        try:
            print("Karakalem stencil başladı:", settings)  # Debug
            
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("Gri tonlama tamamlandı")  # Debug
            
            # Kontrast ve koyuluk ayarla
            contrast = float(settings.get("contrast", 50)) / 50.0  # 0-2 arası
            darkness = float(settings.get("darkness", 50)) - 50    # -50 ile +50 arası
            
            adjusted = cv2.convertScaleAbs(gray, alpha=contrast, beta=darkness)
            print(f"Kontrast ve koyuluk ayarlandı: contrast={contrast}, darkness={darkness}")  # Debug
            
            # Karakalem efekti
            inverted = cv2.bitwise_not(adjusted)
            blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
            sketch = cv2.divide(adjusted, cv2.bitwise_not(blurred), scale=256.0)
            print("Karakalem efekti uygulandı")  # Debug
            
            # Çizgileri kalınlaştır
            thickness = float(settings.get("line_thickness", 2))
            kernel_size = max(1, int(thickness))
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            dilated = cv2.dilate(sketch, kernel, iterations=1)
            print(f"Çizgiler kalınlaştırıldı: {thickness}")  # Debug
            
            result = cv2.bitwise_not(dilated)
            print("Karakalem stencil tamamlandı")  # Debug
            return result
            
        except Exception as e:
            print(f"Karakalem stencil hatası: {str(e)}")  # Debug
            logging.error(f"Karakalem stencil hatası: {str(e)}")
            logging.debug(traceback.format_exc())
            return None