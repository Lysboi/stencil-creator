from typing import Optional, List
import numpy as np
import logging

class HistoryManager:
    """İşlem geçmişini yöneten sınıf"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[np.ndarray] = []
        self.position: int = -1
        self.max_history: int = max_history

    def add(self, image: np.ndarray) -> None:
        """Yeni durumu geçmişe ekle"""
        try:
            # Eğer geçmişte ileri gittikten sonra yeni bir işlem yapıldıysa
            # eski ileri geçmişi sil
            if self.position < len(self.history) - 1:
                self.history = self.history[:self.position + 1]

            # Yeni durumu ekle
            self.history.append(image.copy())
            self.position += 1

            # Geçmiş limitini kontrol et
            if len(self.history) > self.max_history:
                self.history.pop(0)
                self.position -= 1

            logging.info(f"Geçmişe yeni durum eklendi. Pozisyon: {self.position}")
        except Exception as e:
            logging.error(f"Geçmişe ekleme hatası: {str(e)}")

    def undo(self) -> Optional[np.ndarray]:
        """Bir önceki duruma dön"""
        try:
            if self.can_undo():
                self.position -= 1
                logging.info(f"Geri alındı. Yeni pozisyon: {self.position}")
                return self.history[self.position].copy()
            return None
        except Exception as e:
            logging.error(f"Geri alma hatası: {str(e)}")
            return None

    def redo(self) -> Optional[np.ndarray]:
        """Sonraki duruma geç"""
        try:
            if self.can_redo():
                self.position += 1
                logging.info(f"İleri alındı. Yeni pozisyon: {self.position}")
                return self.history[self.position].copy()
            return None
        except Exception as e:
            logging.error(f"İleri alma hatası: {str(e)}")
            return None

    def can_undo(self) -> bool:
        """Geri alma yapılabilir mi?"""
        return self.position > 0

    def can_redo(self) -> bool:
        """İleri alma yapılabilir mi?"""
        return self.position < len(self.history) - 1

    def get_current(self) -> Optional[np.ndarray]:
        """Mevcut durumu döndür"""
        try:
            if self.position >= 0 and self.position < len(self.history):
                return self.history[self.position].copy()
            return None
        except Exception as e:
            logging.error(f"Mevcut durumu alma hatası: {str(e)}")
            return None

    def clear(self) -> None:
        """Geçmişi temizle"""
        try:
            self.history.clear()
            self.position = -1
            logging.info("Geçmiş temizlendi")
        except Exception as e:
            logging.error(f"Geçmiş temizleme hatası: {str(e)}")

    def get_history_info(self) -> str:
        """Geçmiş durumu hakkında bilgi döndür"""
        return f"Pozisyon: {self.position + 1}/{len(self.history)}"