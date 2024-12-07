import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from model_downloader import download_model

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Model İndirme Testi")
        self.setGeometry(100, 100, 400, 200)

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Test butonu
        test_button = QPushButton("Model İndir")
        test_button.clicked.connect(self.test_download)
        layout.addButton(test_button)

    def test_download(self):
        # Test için models klasörünü oluştur
        if not os.path.exists("models"):
            os.makedirs("models")

        # Test URL ve yolu
        test_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/master/hed/deploy.prototxt"
        test_save_path = "models/deploy.prototxt"
        
        # Test indirmesi başlat
        self.downloader = download_model(test_url, test_save_path, self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())