import cv2
import numpy as np
import logging

class CropProcessor:
    @staticmethod
    def process_crop(image, rect, pixmap):
        if not all([image is not None, rect is not None, pixmap is not None]):
            logging.warning("Kırpma için gerekli parametreler eksik")
            return None
            
        try:
            scale_x = image.shape[1] / pixmap.width()
            scale_y = image.shape[0] / pixmap.height()
            
            x = max(0, int(rect.x() * scale_x))
            y = max(0, int(rect.y() * scale_y))
            w = min(int(rect.width() * scale_x), image.shape[1] - x)
            h = min(int(rect.height() * scale_y), image.shape[0] - y)
            
            if w > 0 and h > 0:
                cropped = image[y:y+h, x:x+w]
                logging.info(f"Görüntü başarıyla kırpıldı: {w}x{h}")
                return cropped
                
        except Exception as e:
            logging.error(f"Kırpma işlemi hatası: {str(e)}")
            return None
        
        return None