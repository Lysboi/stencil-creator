from PyQt6.QtCore import QThread, pyqtSignal
import urllib.request
import os
import logging
import traceback

# Loglama ayarlarını yapılandır
logging.basicConfig(
    filename='model_download.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ModelDownloaderThread(QThread):
    """Model indirme işlemini arka planda yapan thread"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            logging.info(f"İndirme başladı - URL: {self.url}")
            logging.info(f"Hedef dosya: {self.save_path}")

            if not os.path.exists(os.path.dirname(self.save_path)):
                os.makedirs(os.path.dirname(self.save_path))
                logging.info(f"Klasör oluşturuldu: {os.path.dirname(self.save_path)}")

            # URL'yi açmaya çalışmadan önce bağlantıyı test et
            request = urllib.request.Request(
                self.url,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                }
            )
            
            logging.info("İndirme başlıyor...")
            with urllib.request.urlopen(request, timeout=60) as response:  # Timeout süresini artırdık
                # Dosyayı doğrudan kaydet
                with open(self.save_path + '.tmp', 'wb') as out_file:  # Geçici dosya kullan
                    total_size = int(response.headers.get('content-length', 0))
                    logging.info(f"Toplam dosya boyutu: {total_size} bytes")
                    
                    block_size = 8192
                    count = 0
                    downloaded = 0
                    
                    while True:
                        data = response.read(block_size)
                        if not data:
                            break
                        out_file.write(data)
                        downloaded += len(data)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress.emit(percent)
                
                # İndirme başarılı olduysa geçici dosyayı taşı
                if os.path.exists(self.save_path + '.tmp'):
                    os.replace(self.save_path + '.tmp', self.save_path)
                    file_size = os.path.getsize(self.save_path)
                    logging.info(f"Dosya başarıyla kaydedildi. Boyut: {file_size} bytes")
                else:
                    logging.error("Dosya kaydedilemedi!")
                    raise Exception("Dosya indirilemedi")

            self.finished.emit(True, "")
            
        except Exception as e:
            error_msg = f"Model indirme hatası: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            if os.path.exists(self.save_path + '.tmp'):
                os.remove(self.save_path + '.tmp')
            self.finished.emit(False, str(e))

def download_model(url, save_path, parent=None):
    """Model indirme işlemini başlat"""
    from PyQt6.QtWidgets import QProgressDialog, QMessageBox
    from PyQt6.QtCore import Qt
    
    progress = QProgressDialog("Model indiriliyor...", "İptal", 0, 100, parent)
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    
    downloader = ModelDownloaderThread(url, save_path)
    
    def update_progress(percent):
        progress.setValue(percent)
        
    def download_finished(success, error):
        progress.close()
        if success:
            QMessageBox.information(parent, "Başarılı", "Model başarıyla indirildi.")
        else:
            QMessageBox.critical(parent, "Hata", f"Model indirilirken hata oluştu: {error}")
    
    downloader.progress.connect(update_progress)
    downloader.finished.connect(download_finished)
    downloader.start()
    
    return downloader