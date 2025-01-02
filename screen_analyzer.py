import numpy as np
from PIL import Image
import win32gui
import win32ui
import win32con
import win32api
from sklearn.cluster import KMeans
import colorsys

class ScreenColorAnalyzer:
    def __init__(self):
        self.last_colors = None
        
    def get_screen_image(self):
        hwnd = win32gui.GetDesktopWindow()
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        
        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()
        
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
        
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)
        
        return im

    def get_color_brightness(self, color):
        """Получить яркость цвета (0-1)"""
        # Преобразуем RGB в HSL
        rgb_normalized = [x/255.0 for x in color]
        h, l, s = colorsys.rgb_to_hls(*rgb_normalized)
        return l

    def get_color_dominance(self, image, color):
        """Получить доминантность цвета на изображении (0-1)"""
        img_array = np.array(image)
        total_pixels = img_array.shape[0] * img_array.shape[1]
        
        # Создаем маску для подсчета пикселей близких к цвету
        color_diff = np.abs(img_array - np.array(color)).sum(axis=2)
        similar_pixels = np.sum(color_diff < 150)  # Порог схожести
        
        return similar_pixels / total_pixels

    def sort_colors_by_dominance(self, image, colors):
        """Сортировка цветов по их доминантности"""
        dominance_scores = [(color, self.get_color_dominance(image, color)) for color in colors]
        return [color for color, _ in sorted(dominance_scores, key=lambda x: x[1], reverse=True)]

    def get_dominant_colors(self, num_colors=3):
        try:
            # Получаем скриншот
            screen = self.get_screen_image()
            
            # Уменьшаем изображение для ускорения обработки
            screen.thumbnail((300, 300))
            
            # Преобразуем изображение в массив
            img_array = np.array(screen)
            pixels = img_array.reshape(-1, 3)
            
            # Применяем K-means clustering
            kmeans = KMeans(n_clusters=num_colors, random_state=0)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            
            # Преобразуем в список RGB цветов
            colors = [tuple(color) for color in colors]
            
            # Сортируем цвета по яркости
            colors_with_brightness = [(color, self.get_color_brightness(color)) for color in colors]
            
            # Сортируем: самый темный будет первым (для фона)
            sorted_colors = sorted(colors_with_brightness, key=lambda x: x[1])
            colors = [color for color, _ in sorted_colors]
            
            # Проверяем доминантность
            colors = self.sort_colors_by_dominance(screen, colors)
            
            # Преобразуем в HEX
            hex_colors = ['#%02x%02x%02x' % color for color in colors]
            
            self.last_colors = hex_colors
            return hex_colors
            
        except Exception as e:
            print(f"Ошибка при анализе цветов: {str(e)}")
            if self.last_colors:
                return self.last_colors
            return ['#36393F', '#2F3136', '#202225']  # Discord default colors 