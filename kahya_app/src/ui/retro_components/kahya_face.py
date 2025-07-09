import random
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

class KahyaFace(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        # Renkler
        self.bg_color = QColor(8, 20, 10)
        self.grid_color = QColor(40, 80, 40, 60)
        self.detail_color = QColor(80, 255, 120)
        self.outline_color = QColor(80, 255, 120)
        self.eye_color = QColor(80, 255, 120)
        self.brow_color = QColor(80, 255, 120)
        self.face_color = QColor(40, 120, 60)
        # Animasyon
        self.blink_state = 0
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.blink)
        self.blink_timer.start(4000)
        self.eye_x = 0.0
        self.eye_y = 0.0
        self.eye_target_x = 0.0
        self.eye_target_y = 0.0
        self.eye_move_timer = QTimer(self)
        self.eye_move_timer.timeout.connect(self.move_eyes)
        self.eye_move_timer.start(3000)
        self.expression = "neutral"
        # Partikül efekti (tamamen baştan)
        self.particles = []
        self.particle_count = 24
        for _ in range(self.particle_count):
            self.particles.append(self.spawn_particle())
        self.particle_timer = QTimer(self)
        self.particle_timer.timeout.connect(self.update_particles)
        self.particle_timer.start(50)
        # Ağız animasyonu için
        self.mouth_anim = 0.0
        self.mouth_timer = QTimer(self)
        self.mouth_timer.timeout.connect(self.update_mouth)
        self.mouth_timer.start(60)
        # Mouse takibi
        self.setMouseTracking(True)
        
        # Konuşma durumu
        self.talking = False
    def spawn_particle(self):
        w, h = self.width(), self.height()
        return {
            'x': random.uniform(2, w-6),
            'y': random.uniform(2, h-6),
            'vx': random.uniform(-1.2, 1.2),
            'vy': random.uniform(-1.2, 1.2),
            'life': random.randint(60, 180)
        }
    def update_particles(self):
        w, h = self.width(), self.height()
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            # Kenara çarpınca yön değiştir
            if p['x'] <= 2 or p['x'] >= w-6:
                p['vx'] *= -1
                p['x'] = max(2, min(w-6, p['x']))
            if p['y'] <= 2 or p['y'] >= h-6:
                p['vy'] *= -1
                p['y'] = max(2, min(h-6, p['y']))
            # Yaşam süresi bitince yeniden doğsun
            if p['life'] <= 0:
                np = self.spawn_particle()
                p['x'], p['y'], p['vx'], p['vy'], p['life'] = np['x'], np['y'], np['vx'], np['vy'], np['life']
        self.update()
    def set_expression(self, expression):
        self.expression = expression
        self.update()
    def blink(self):
        self.blink_state = 1
        QTimer.singleShot(120, lambda: setattr(self, 'blink_state', 0))
        self.update()
    def move_eyes(self):
        pass
    def update_mouth(self):
        self.mouth_anim = (self.mouth_anim + 0.08) % (2 * math.pi)
        self.update()
    def mouseMoveEvent(self, event):
        w, h = self.width(), self.height()
        
        # Göz alanlarını tanımla
        eye_w, eye_h = 50, 35
        eye_y = h//2 - 45
        left_eye_x = w//2 - 75
        right_eye_x = w//2 + 25
        
        # Mouse pozisyonunu göz alanlarına göre hesapla
        mouse_x = event.x()
        mouse_y = event.y()
        
        # Sol göz için hedef
        left_eye_center_x = left_eye_x + eye_w//2
        left_eye_center_y = eye_y + eye_h//2
        left_mx = (mouse_x - left_eye_center_x) / (eye_w//2)
        left_my = (mouse_y - left_eye_center_y) / (eye_h//2)
        
        # Sağ göz için hedef
        right_eye_center_x = right_eye_x + eye_w//2
        right_eye_center_y = eye_y + eye_h//2
        right_mx = (mouse_x - right_eye_center_x) / (eye_w//2)
        right_my = (mouse_y - right_eye_center_y) / (eye_h//2)
        
        # Ortalama hedef (her iki göz için)
        self.eye_target_x = max(-1, min(1, (left_mx + right_mx) / 2))
        self.eye_target_y = max(-0.7, min(0.7, (left_my + right_my) / 2))
        
        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()
        # Arka plan (tamamen gridli)
        painter.fillRect(0, 0, w, h, self.bg_color)
        grid_size = 8
        painter.setPen(QPen(self.grid_color, 1))
        for x in range(0, w, grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, grid_size):
            painter.drawLine(0, y, w, y)
        # Dış çerçeve (pixel-art)
        painter.setPen(QPen(self.outline_color, 4))
        painter.setBrush(Qt.NoBrush)
        margin = 16
        painter.drawRect(margin, margin, w-2*margin, h-2*margin)
        # Köşe detayları
        painter.setPen(QPen(self.outline_color, 4))
        for dx in [0, w-2*margin]:
            for dy in [0, h-2*margin]:
                painter.drawPoint(margin+dx, margin+dy)
        # Yan çıkıntılar
        painter.setPen(QPen(self.outline_color, 4))
        painter.drawLine(margin-10, h//2-48, margin, h//2-48)
        painter.drawLine(margin-10, h//2+48, margin, h//2+48)
        painter.drawLine(w-margin+10, h//2-48, w-margin, h//2-48)
        painter.drawLine(w-margin+10, h//2+48, w-margin, h//2+48)
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+32, margin-10, w-margin-32, margin-10)
        painter.drawLine(margin+32, h-margin+10, w-margin-32, h-margin+10)
        
        # Partiküller (tüm monitör componentinde)
        for p in self.particles:
            alpha = int(120 + 120 * (p['life'] / 180))
            color = QColor(self.detail_color.red(), self.detail_color.green(), self.detail_color.blue(), alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(p['x']), int(p['y']), 3, 3)
            
        # Göz ve ağız koordinatları - daha büyük yüz
        eye_w, eye_h = 50, 35  # Daha büyük oval gözler
        eye_y = h//2 - 45
        left_eye_x = w//2 - 75
        right_eye_x = w//2 + 25
        mouth_w, mouth_h = 80, 15  # Ağızı küçülttüm
        mouth_x = w//2 - mouth_w//2
        mouth_y = h//2 + 50
        
        # Kaş koordinatları - gözlerin tam üzerinde
        brow_w, brow_h = 45, 10
        left_brow_x = left_eye_x - 2
        right_brow_x = right_eye_x - 2
        brow_y = eye_y - 12  # Gözlerin tam üzerinde
        
        # Kaşları çiz (duyguya göre tasarımlı)
        painter.setPen(QPen(self.brow_color, 4))
        painter.setBrush(QBrush(self.brow_color))
        
        if self.expression == "happy":
            # Mutlu kaşlar - hafif kavisli yukarı
            # Sol kaş
            painter.drawLine(left_brow_x, brow_y-2, left_brow_x+15, brow_y-4)
            painter.drawLine(left_brow_x+15, brow_y-4, left_brow_x+30, brow_y-3)
            painter.drawLine(left_brow_x+30, brow_y-3, left_brow_x+brow_w, brow_y-2)
            # Sağ kaş
            painter.drawLine(right_brow_x, brow_y-2, right_brow_x+15, brow_y-4)
            painter.drawLine(right_brow_x+15, brow_y-4, right_brow_x+30, brow_y-3)
            painter.drawLine(right_brow_x+30, brow_y-3, right_brow_x+brow_w, brow_y-2)
        elif self.expression == "sad":
            # Üzgün kaşlar - içe doğru kavisli
            # Sol kaş
            painter.drawLine(left_brow_x, brow_y+2, left_brow_x+15, brow_y+1)
            painter.drawLine(left_brow_x+15, brow_y+1, left_brow_x+30, brow_y+3)
            painter.drawLine(left_brow_x+30, brow_y+3, left_brow_x+brow_w, brow_y+2)
            # Sağ kaş
            painter.drawLine(right_brow_x, brow_y+2, right_brow_x+15, brow_y+1)
            painter.drawLine(right_brow_x+15, brow_y+1, right_brow_x+30, brow_y+3)
            painter.drawLine(right_brow_x+30, brow_y+3, right_brow_x+brow_w, brow_y+2)
        elif self.expression == "surprised":
            # Şaşkın kaşlar - yukarı kavisli
            # Sol kaş
            painter.drawLine(left_brow_x, brow_y-3, left_brow_x+15, brow_y-6)
            painter.drawLine(left_brow_x+15, brow_y-6, left_brow_x+30, brow_y-7)
            painter.drawLine(left_brow_x+30, brow_y-7, left_brow_x+brow_w, brow_y-5)
            # Sağ kaş
            painter.drawLine(right_brow_x, brow_y-3, right_brow_x+15, brow_y-6)
            painter.drawLine(right_brow_x+15, brow_y-6, right_brow_x+30, brow_y-7)
            painter.drawLine(right_brow_x+30, brow_y-7, right_brow_x+brow_w, brow_y-5)
        else:
            # Normal kaşlar - hafif kavisli
            # Sol kaş
            painter.drawLine(left_brow_x, brow_y, left_brow_x+15, brow_y-1)
            painter.drawLine(left_brow_x+15, brow_y-1, left_brow_x+30, brow_y-1)
            painter.drawLine(left_brow_x+30, brow_y-1, left_brow_x+brow_w, brow_y)
            # Sağ kaş
            painter.drawLine(right_brow_x, brow_y, right_brow_x+15, brow_y-1)
            painter.drawLine(right_brow_x+15, brow_y-1, right_brow_x+30, brow_y-1)
            painter.drawLine(right_brow_x+30, brow_y-1, right_brow_x+brow_w, brow_y)
        
        # Gözler (oval ve göz bebeği yok)
        self.eye_x += (self.eye_target_x - self.eye_x) * 0.25
        self.eye_y += (self.eye_target_y - self.eye_y) * 0.25
        
        # Sol göz - oval
        self.draw_oval_eye(painter, left_eye_x, eye_y, eye_w, eye_h, self.eye_x, self.eye_y)
        
        # Sağ göz - oval
        self.draw_oval_eye(painter, right_eye_x, eye_y, eye_w, eye_h, self.eye_x, self.eye_y)
        
        # Blink efekti (göz kapatma animasyonu)
        if self.blink_state:
            painter.setBrush(QBrush(self.bg_color))  # Arka plan rengi ile gözü kapat
            painter.setPen(Qt.NoPen)
            # Sol gözü tamamen kapat
            painter.drawRect(left_eye_x, eye_y, eye_w, eye_h)
            # Sağ gözü tamamen kapat
            painter.drawRect(right_eye_x, eye_y, eye_w, eye_h)
            
        # Ağız (hafif tebessüm)
        painter.setPen(QPen(self.eye_color, 0))
        painter.setBrush(QBrush(self.eye_color))
        
        if hasattr(self, 'talking') and self.talking:
            # Konuşurken basit hareket
            anim = int((math.sin(self.mouth_anim) * 0.5 + 0.5) * 4)
            painter.drawRect(mouth_x, mouth_y+anim, mouth_w, 6)
        else:
            # Normal durumda hafif tebessüm
            anim = int((math.sin(self.mouth_anim) * 0.5 + 0.5) * 2)
            # Hafif tebessüm efekti - köşeler yukarı
            for i in range(mouth_w // 4):
                x = mouth_x + i * 4
                # Tebessüm için y pozisyonunu hesapla
                smile_factor = abs(i - (mouth_w // 8)) / (mouth_w // 8)  # Merkezden uzaklık
                y_offset = int(smile_factor * 2)  # Hafif yukarı
                y = mouth_y + 2 + anim - y_offset
                painter.drawRect(x, y, 3, 3)
    def cleanup(self):
        self.blink_timer.stop()
        self.eye_move_timer.stop()
        self.particle_timer.stop()
        self.mouth_timer.stop() 
    def draw_oval_eye(self, painter, x, y, w, h, eye_x, eye_y):
        """Göz çiz (göz kapağı efekti ile)"""
        painter.setBrush(Qt.NoBrush)  # İçi boş
        painter.setPen(QPen(self.eye_color, 3))  # Kalın çerçeve
        
        # Göz çerçevesi (oval çember)
        painter.drawEllipse(x, y, w, h)
        
        # Üst göz kapağı efekti - gözün üst kısmını kısmen kapatır
        painter.setBrush(QBrush(self.bg_color))  # Arka plan rengi ile doldur
        painter.setPen(Qt.NoPen)
        # Gözün üst 1/3'ünü kapatacak şekilde
        eyelid_height = h // 3
        painter.drawRect(x, y, w, eyelid_height)
        
        # Göz bebeği (merkezde)
        pupil_size = 8
        pupil_x = x + w//2 - pupil_size//2 + int(eye_x * 8)
        pupil_y = y + h//2 - pupil_size//2 + int(eye_y * 8)
        painter.setBrush(QBrush(self.eye_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(pupil_x, pupil_y, pupil_size, pupil_size)
    
    def set_talking(self, talking):
        """Konuşma durumunu ayarla"""
        self.talking = talking
        self.update() 