import cv2
import numpy as np
import os

class QRExtractor:
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.webp']
    
    def extract_from_image(self, image_path):
        if not os.path.exists(image_path):
            return None
        
        try:
            # Baca gambar
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # QR Detector bawaan OpenCV
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if data and data.strip():
                return data.strip()
            
            # Fallback: grayscale + threshold
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            data2, bbox2, _ = detector.detectAndDecode(thresh)
            
            if data2 and data2.strip():
                return data2.strip()
            
        except Exception as e:
            pass
        
        return None