import cv2
import numpy as np
import logging

class AdvancedSketchProcessor:
    @staticmethod
    def preprocess_image(image: np.ndarray, settings: dict) -> np.ndarray:
        """Görüntü ön işleme"""
        try:
            # Ayarları al
            detail_preservation = settings.get('detail_preservation', 70) / 100.0
            contrast_boost = settings.get('contrast_boost', 1.5)
            smoothness = settings.get('smoothness', 30) / 100.0

            # Görüntüyü LAB uzayına dönüştür
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Kontrast iyileştirme
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(l)
            
            # Gürültü azaltma (detay koruma seviyesine göre)
            denoised = cv2.fastNlMeansDenoising(
                enhanced,
                h=10 * (1 - detail_preservation),
                templateWindowSize=7,
                searchWindowSize=21
            )

            # Keskinleştirme
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)

            # Kontrast artırma
            adjusted = cv2.convertScaleAbs(sharpened, alpha=contrast_boost, beta=0)

            # Yumuşatma (smoothness seviyesine göre)
            if smoothness > 0:
                blur_size = int(3 + smoothness * 6) | 1  # Tek sayı olması için
                adjusted = cv2.GaussianBlur(adjusted, (blur_size, blur_size), 0)

            return adjusted

        except Exception as e:
            logging.error(f"Görüntü ön işleme hatası: {str(e)}")
            return None

    @staticmethod
    def create_stencil_mask(preprocessed: np.ndarray, settings: dict) -> np.ndarray:
        """Stencil maskesi oluştur"""
        try:
            # Ayarları al
            detail_level = settings.get('detail_level', 50) / 100.0
            edge_sensitivity = settings.get('edge_sensitivity', 50) / 100.0
            min_line_width = max(1, settings.get('min_line_width', 1))
            max_line_width = max(min_line_width, settings.get('max_line_width', 3))

            # Çoklu kenar tespiti
            edges1 = cv2.Canny(
                preprocessed,
                threshold1=100 * (1 - edge_sensitivity),
                threshold2=200 * edge_sensitivity
            )

            edges2 = cv2.adaptiveThreshold(
                preprocessed,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                11,
                2
            )

            # Kenarları birleştir
            combined_edges = cv2.addWeighted(
                edges1, detail_level,
                edges2, 1 - detail_level,
                0
            )

            # Çizgi kalınlığını ayarla
            kernel_size = int(min_line_width + (max_line_width - min_line_width) * detail_level)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
            dilated = cv2.dilate(combined_edges, kernel, iterations=1)

            return dilated

        except Exception as e:
            logging.error(f"Stencil maskesi oluşturma hatası: {str(e)}")
            return None

    @staticmethod
    def portrait_to_sketch(image: np.ndarray, settings: dict) -> np.ndarray:
        """Gelişmiş portre-çizim dönüşümü"""
        try:
            # Ön işleme
            preprocessed = AdvancedSketchProcessor.preprocess_image(image, settings)
            if preprocessed is None:
                return None

            # Stencil maskesi oluştur
            stencil = AdvancedSketchProcessor.create_stencil_mask(preprocessed, settings)
            if stencil is None:
                return None

            # Son işlemler
            if settings.get('invert_output', True):
                stencil = cv2.bitwise_not(stencil)

            # Keskin detayları koru
            detail_preservation = settings.get('detail_preservation', 70) / 100.0
            if detail_preservation > 0.5:
                edges = cv2.Canny(preprocessed, 100, 200)
                stencil = cv2.addWeighted(stencil, 0.7, edges, 0.3, 0)

            return stencil

        except Exception as e:
            logging.error(f"Portre-çizim dönüşümü hatası: {str(e)}")
            return None

    @staticmethod
    def artistic_sketch(image: np.ndarray, settings: dict) -> np.ndarray:
        """Sanatsal çizim dönüşümü"""
        try:
            # Ön işleme ayarlarını güncelle
            artistic_settings = settings.copy()
            artistic_settings.update({
                'detail_preservation': 85,
                'contrast_boost': 2.0,
                'smoothness': 20,
                'edge_sensitivity': 70,
                'min_line_width': 1.5,
                'max_line_width': 4
            })

            # Ön işleme
            preprocessed = AdvancedSketchProcessor.preprocess_image(image, artistic_settings)
            if preprocessed is None:
                return None

            # Ana işlem
            # XDoG (eXtended Difference of Gaussians) benzeri efekt
            sigma = 0.3
            k = 4.5
            p = 19  # Keskinlik

            gaussianPic = cv2.GaussianBlur(preprocessed, (0, 0), sigma)
            gaussianPic2 = cv2.GaussianBlur(preprocessed, (0, 0), sigma * k)
            
            dog = gaussianPic - gaussianPic2
            dog = np.where(dog < 0, 0, 255)
            dog = dog.astype(np.uint8)

            # Detayları geliştir
            detail_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            enhanced = cv2.filter2D(dog, -1, detail_kernel)

            # Son işlemler
            if settings.get('invert_output', True):
                enhanced = cv2.bitwise_not(enhanced)

            return enhanced

        except Exception as e:
            logging.error(f"Sanatsal çizim dönüşümü hatası: {str(e)}")
            return None