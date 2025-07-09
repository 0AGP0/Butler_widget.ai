from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from datetime import datetime
import math

class RetroClock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 100)
        
        # Zamanlayıcı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Her saniye güncelle
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.grid_color = QColor(40, 80, 40, 60)  # Grid çizgileri
        self.text_color = QColor(80, 255, 120)  # Parlak yeşil metin
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.detail_color = QColor(80, 255, 120)  # Detay rengi
        self.glow_color = QColor(80, 255, 120, 50)  # Yeşil glow efekti
        
        # Font - pixel art için
        self.time_font = QFont("Courier", 18, QFont.Bold)
        self.date_font = QFont("Courier", 10, QFont.Bold)
        
        # Animasyon
        self.glow_alpha = 0
        self.glow_direction = 1
        
        # Glow animasyon zamanlayıcısı
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.update_glow)
        self.glow_timer.start(50)  # 50ms
        
    def update_time(self):
        """Zamanı güncelle"""
        self.update()
        
    def update_glow(self):
        """Glow efektini güncelle"""
        self.glow_alpha += self.glow_direction * 5
        if self.glow_alpha >= 100:
            self.glow_alpha = 100
            self.glow_direction = -1
        elif self.glow_alpha <= 0:
            self.glow_alpha = 0
            self.glow_direction = 1
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # Pixel art için
        
        # Widget boyutları
        w, h = self.width(), self.height()
        
        # Arka plan (gridli pixel art)
        painter.fillRect(0, 0, w, h, self.bg_color)
        
        # Grid çizgileri
        grid_size = 8
        painter.setPen(QPen(self.grid_color, 1))
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)
        
        # Dış çerçeve (pixel-art)
        painter.setPen(QPen(self.border_color, 4))
        painter.setBrush(Qt.NoBrush)
        margin = 12
        painter.drawRect(margin, margin, w-2*margin, h-2*margin)
        
        # Köşe detayları
        painter.setPen(QPen(self.border_color, 4))
        for dx in [0, w-2*margin]:
            for dy in [0, h-2*margin]:
                painter.drawPoint(margin+dx, margin+dy)
        
        # Yan çıkıntılar
        painter.setPen(QPen(self.border_color, 4))
        painter.drawLine(margin-8, h//2-20, margin, h//2-20)
        painter.drawLine(margin-8, h//2+20, margin, h//2+20)
        painter.drawLine(w-margin+8, h//2-20, w-margin, h//2-20)
        painter.drawLine(w-margin+8, h//2+20, w-margin, h//2+20)
        
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+24, margin-8, w-margin-24, margin-8)
        painter.drawLine(margin+24, h-margin+8, w-margin-24, h-margin+8)
        
        # Şu anki zaman
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%d.%m.%Y")
        day_str = now.strftime("%A")
        
        # Glow efekti
        glow_color = QColor(self.glow_color)
        glow_color.setAlpha(self.glow_alpha)
        painter.setPen(QPen(glow_color, 3))
        
        # Saat metni (glow)
        painter.setFont(self.time_font)
        time_rect = painter.fontMetrics().boundingRect(time_str)
        time_x = (w - time_rect.width()) // 2
        time_y = h // 2 - 8
        painter.drawText(time_x, time_y, time_str)
        
        # Ana metin
        painter.setPen(QPen(self.text_color, 2))
        painter.drawText(time_x, time_y, time_str)
        
        # Tarih metni
        painter.setFont(self.date_font)
        date_rect = painter.fontMetrics().boundingRect(date_str)
        date_x = (w - date_rect.width()) // 2
        date_y = h // 2 + 15
        painter.drawText(date_x, date_y, date_str)
        
        # Gün metni
        day_rect = painter.fontMetrics().boundingRect(day_str)
        day_x = (w - day_rect.width()) // 2
        day_y = h // 2 + 30
        painter.drawText(day_x, day_y, day_str)
        
        # Köşe dekorasyonları
        self.draw_corners(painter, w, h)
        
        # Scan line efekti
        self.draw_scan_lines(painter, w, h)
        
    def draw_corners(self, painter, width, height):
        """Köşe dekorasyonlarını çiz"""
        corner_size = 12
        corner_color = self.detail_color
        
        painter.setPen(QPen(corner_color, 3))
        
        # Sol üst köşe
        painter.drawLine(4, 4, corner_size, 4)
        painter.drawLine(4, 4, 4, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(width - corner_size, 4, width - 4, 4)
        painter.drawLine(width - 4, 4, width - 4, corner_size)
        
        # Sol alt köşe
        painter.drawLine(4, height - corner_size, 4, height - 4)
        painter.drawLine(4, height - 4, corner_size, height - 4)
        
        # Sağ alt köşe
        painter.drawLine(width - corner_size, height - 4, width - 4, height - 4)
        painter.drawLine(width - 4, height - corner_size, width - 4, height - 4)
        
    def draw_scan_lines(self, painter, width, height):
        """Scan line efektini çiz"""
        scan_color = QColor(80, 255, 120, 15)
        painter.setPen(QPen(scan_color, 1))
        
        for y in range(0, height, 4):
            painter.drawLine(0, y, width, y)
            
    def resizeEvent(self, event):
        """Widget yeniden boyutlandırıldığında"""
        super().resizeEvent(event)
        self.update()
        
    def cleanup(self):
        """Temizlik"""
        self.timer.stop()
        self.glow_timer.stop() 