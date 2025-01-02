import numpy as np
from PIL import ImageGrab
from sklearn.cluster import KMeans

class ScreenColorAnalyzer:
    def __init__(self):
        self.dominant_colors = []
    
    def get_dominant_colors(self, num_colors=3):
        # Получаем скриншот экрана
        screenshot = ImageGrab.grab()
        # Конвертируем в numpy массив
        np_screenshot = np.array(screenshot)
        
        # Reshape для KMeans
        pixels = np_screenshot.reshape(-1, 3)
        
        # Находим доминирующие цвета
        kmeans = KMeans(n_clusters=num_colors)
        kmeans.fit(pixels)
        
        # Получаем RGB значения
        colors = kmeans.cluster_centers_
        
        # Конвертируем в hex
        self.dominant_colors = ['#%02x%02x%02x' % tuple(map(int, color)) 
                              for color in colors]
        
        return self.dominant_colors 