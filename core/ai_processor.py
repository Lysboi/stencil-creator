import replicate
import cv2
import numpy as np
import logging
import os
import tempfile
from typing import Optional
import requests
from PIL import Image
import io

class AIProcessor:
    """AI tabanlı görüntü işleme sınıfı"""
    
    def __init__(self):
        # API anahtarını environ'dan al
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            logging.warning("REPLICATE_API_TOKEN bulunamadı!")
        
    def process_with_controlnet(
        self,
        image: np.ndarray,
        prompt: str = "detailed stencil art, black and white, high contrast",
        negative_prompt: str = "color, blurry, noisy, unrealistic, low quality",
    ) -> Optional[np.ndarray]:
        """ControlNet ile stencil oluştur"""
        try:
            # Görüntüyü geçici dosyaya kaydet
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                cv2.imwrite(tmp_file.name, image)
                
                # ControlNet modelini çalıştır
                output = replicate.run(
                    "jagilley/controlnet-canny:aff48af9c68d162388d230a2ab003f68d2638d88307bdaf1c2f1ac95079c9613",
                    input={
                        "image": open(tmp_file.name, "rb"),
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": 20,
                        "guidance_scale": 9
                    }
                )
                
                # Geçici dosyayı sil
                os.unlink(tmp_file.name)
                
                if output and isinstance(output, list) and len(output) > 0:
                    # URL'den görüntüyü al
                    response = requests.get(output[0])
                    if response.status_code == 200:
                        # Bytes'ı numpy array'e çevir
                        image_bytes = io.BytesIO(response.content)
                        pil_image = Image.open(image_bytes)
                        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    
                logging.error("AI işleme başarısız oldu")
                return None
                
        except Exception as e:
            logging.error(f"AI işleme hatası: {str(e)}")
            return None
            
    @staticmethod
    def prepare_image_for_controlnet(image: np.ndarray, settings: dict) -> np.ndarray:
        """Görüntüyü ControlNet için hazırla"""
        try:
            # Canny kenar tespiti uygula
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(
                blur,
                threshold1=float(settings.get("threshold1", 100)),
                threshold2=float(settings.get("threshold2", 200))
            )
            return edges
            
        except Exception as e:
            logging.error(f"Görüntü hazırlama hatası: {str(e)}")
            return None