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
        
        # Renkler
        self.bg_color = QColor(0, 0, 0)  # Siyah arka plan
        self.text_color = QColor(0, 255, 0)  # Yeşil metin
        self.border_color = QColor(0, 200, 0)  # Yeşil kenarlık
        self.glow_color = QColor(0, 255, 0, 50)  # Yeşil glow efekti
        
        # Font
        self.time_font = QFont("Courier", 24, QFont.Bold)
        self.date_font = QFont("Courier", 12, QFont.Bold)
        
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
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Widget boyutları
        width = self.width()
        height = self.height()
        
        # Arka plan
        painter.fillRect(self.rect(), self.bg_color)
        
        # Kenarlık
        painter.setPen(QPen(self.border_color, 2))
        painter.drawRect(0, 0, width-1, height-1)
        
        # İç kenarlık
        painter.setPen(QPen(QColor(0, 150, 0), 1))
        painter.drawRect(2, 2, width-5, height-5)
        
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
        time_x = (width - time_rect.width()) // 2
        time_y = height // 2 - 10
        painter.drawText(time_x, time_y, time_str)
        
        # Ana metin
        painter.setPen(QPen(self.text_color, 2))
        painter.drawText(time_x, time_y, time_str)
        
        # Tarih metni
        painter.setFont(self.date_font)
        date_rect = painter.fontMetrics().boundingRect(date_str)
        date_x = (width - date_rect.width()) // 2
        date_y = height // 2 + 20
        painter.drawText(date_x, date_y, date_str)
        
        # Gün metni
        day_rect = painter.fontMetrics().boundingRect(day_str)
        day_x = (width - day_rect.width()) // 2
        day_y = height // 2 + 40
        painter.drawText(day_x, day_y, day_str)
        
        # Köşe dekorasyonları
        self.draw_corners(painter, width, height)
        
        # Scan line efekti
        self.draw_scan_lines(painter, width, height)
        
    def draw_corners(self, painter, width, height):
        """Köşe dekorasyonlarını çiz"""
        corner_size = 15
        corner_color = QColor(0, 200, 0)
        
        painter.setPen(QPen(corner_color, 2))
        
        # Sol üst köşe
        painter.drawLine(5, 5, corner_size, 5)
        painter.drawLine(5, 5, 5, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(width - corner_size, 5, width - 5, 5)
        painter.drawLine(width - 5, 5, width - 5, corner_size)
        
        # Sol alt köşe
        painter.drawLine(5, height - corner_size, 5, height - 5)
        painter.drawLine(5, height - 5, corner_size, height - 5)
        
        # Sağ alt köşe
        painter.drawLine(width - corner_size, height - 5, width - 5, height - 5)
        painter.drawLine(width - 5, height - corner_size, width - 5, height - 5)
        
    def draw_scan_lines(self, painter, width, height):
        """Scan line efektini çiz"""
        scan_color = QColor(0, 255, 0, 20)
        painter.setPen(QPen(scan_color, 1))
        
        for y in range(0, height, 3):
            painter.drawLine(0, y, width, y)
            
    def resizeEvent(self, event):
        """Widget yeniden boyutlandırıldığında"""
        super().resizeEvent(event)
        self.update()
        
    def cleanup(self):
        """Temizlik"""
        self.timer.stop()
        self.glow_timer.stop() 