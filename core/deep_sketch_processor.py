import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
import cv2
import yaml
import logging
import os

class APDrawingModel(nn.Module):
    def __init__(self):
        super(APDrawingModel, self).__init__()
        # Model mimarisi burada tanımlanacak
        self.layers = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=7, stride=1, padding=3),
            nn.ReLU(True),
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(256, 512, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(True),
            nn.Conv2d(64, 1, kernel_size=7, stride=1, padding=3),
            nn.Tanh()
        )

    def forward(self, x):
        return self.layers(x)

class DeepSketchProcessor:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def load_model(self, model_path):
        try:
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")

            self.model = APDrawingModel().to(self.device)
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            logging.info("Model başarıyla yüklendi")
            return True
        except Exception as e:
            logging.error(f"Model yükleme hatası: {str(e)}")
            return False

    def preprocess_image(self, image):
        # Görüntüyü model için hazırla
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        # Görüntüyü 512x512'ye yeniden boyutlandır
        image = cv2.resize(image, (512, 512))
        
        # Normalizasyon ve tensor dönüşümü
        tensor = self.transform(image)
        tensor = tensor.unsqueeze(0).to(self.device)
        
        return tensor

    def postprocess_output(self, output):
        # Model çıktısını görüntüye dönüştür
        output = output.cpu().detach().numpy()
        output = np.transpose(output[0], (1, 2, 0))
        output = ((output + 1) * 127.5).astype(np.uint8)
        
        # Tek kanala dönüştür
        if output.shape[-1] > 1:
            output = cv2.cvtColor(output, cv2.COLOR_RGB2GRAY)
        
        return output

    def process_image(self, image, settings=None):
        """Görüntüyü işle ve sketch'e dönüştür"""
        try:
            if self.model is None:
                raise ValueError("Model yüklenmemiş!")

            with torch.no_grad():
                # Görüntüyü hazırla
                input_tensor = self.preprocess_image(image)
                
                # Model çıktısını al
                output = self.model(input_tensor)
                
                # Çıktıyı işle
                result = self.postprocess_output(output)
                
                # Orijinal boyuta döndür
                if image.shape[:2] != result.shape[:2]:
                    result = cv2.resize(result, (image.shape[1], image.shape[0]))
                
                return result

        except Exception as e:
            logging.error(f"Görüntü işleme hatası: {str(e)}")
            return None
