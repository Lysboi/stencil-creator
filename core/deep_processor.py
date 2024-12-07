import cv2
import numpy as np
import logging
import os
import urllib.request

class DeepProcessor:
    """Derin öğrenme tabanlı görüntü işleme"""
    
    MODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/hed_pretrained_bsds.caffemodel"
    PROTO_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/master/hed/deploy.prototxt"
    
    def __init__(self):
        self.model_path = "models/hed_model.caffemodel"
        self.proto_path = "models/deploy.prototxt"
        self._ensure_model_exists()
        
        try:
            self.net = cv2.dnn.readNetFromCaffe(self.proto_path, self.model_path)
            logging.info("HED model başarıyla yüklendi")
        except Exception as e:
            logging.error(f"Model yükleme hatası: {str(e)}")
            self.net = None

    def _ensure_model_exists(self):
        """Model dosyalarının varlığını kontrol et ve indir"""
        if not os.path.exists('models'):
            os.makedirs('models')
            
        if not os.path.exists(self.model_path):
            logging.info("HED model indiriliyor...")
            urllib.request.urlretrieve(self.MODEL_URL, self.model_path)
            
        if not os.path.exists(self.proto_path):
            logging.info("Proto dosyası indiriliyor...")
            urllib.request.urlretrieve(self.PROTO_URL, self.proto_path)

    def process_hed(self, image: np.ndarray, settings: dict) -> np.ndarray:
        """HED modeli ile kenar tespiti"""
        try:
            if self.net is None:
                raise Exception("Model yüklenemedi!")

            # Görüntüyü hazırla
            height, width = image.shape[:2]
            inp = cv2.dnn.blobFromImage(
                image, 
                scalefactor=1.0, 
                size=(width, height),
                mean=(104.00698793, 116.66876762, 122.67891434),
                swapRB=False, 
                crop=False
            )
            
            # Modeli çalıştır
            self.net.setInput(inp)
            edges = self.net.forward()
            edges = edges[0, 0]
            edges = cv2.resize(edges, (width, height))
            
            # Eşikleme ve temizleme
            threshold = float(settings.get("threshold", 50)) / 100.0
            edges = cv2.threshold(edges, threshold, 1, cv2.THRESH_BINARY)[1]
            
            # Görüntüyü 0-255 aralığına normalize et
            edges = (edges * 255).astype(np.uint8)
            
            # Çizgi kalınlığı
            thickness = max(1, int(settings.get("line_thickness", 2)))
            kernel = np.ones((thickness, thickness), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Gürültü azaltma
            if settings.get("denoise", True):
                edges = cv2.medianBlur(edges, 3)
            
            # Sonucu tersine çevir (beyaz arka plan, siyah çizgiler)
            return cv2.bitwise_not(edges)
            
        except Exception as e:
            logging.error(f"HED işleme hatası: {str(e)}")
            return None

    def deep_artistic_stencil(self, image: np.ndarray, settings: dict) -> np.ndarray:
        """Gelişmiş sanatsal stencil efekti"""
        try:
            # İlk olarak HED ile kenarları bul
            edges = self.process_hed(image, settings)
            if edges is None:
                return None
                
            # Kontrast ve detay ayarlamaları
            detail_level = float(settings.get("detail_level", 50)) / 100.0
            contrast = float(settings.get("contrast", 50)) / 50.0
            
            # Kontrast ayarla
            adjusted = cv2.convertScaleAbs(edges, alpha=contrast, beta=0)
            
            # Detay seviyesi için adaptif eşikleme
            if detail_level > 0.5:  # Daha fazla detay
                window_size = int(21 * (2.0 - detail_level))  # 21'den küçük
                if window_size % 2 == 0:
                    window_size += 1
                final = cv2.adaptiveThreshold(
                    adjusted,
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    window_size,
                    10
                )
            else:  # Daha az detay
                threshold = int(255 * detail_level)
                final = cv2.threshold(adjusted, threshold, 255, cv2.THRESH_BINARY)[1]
            
            return final
            
        except Exception as e:
            logging.error(f"Artistic stencil hatası: {str(e)}")
            return None