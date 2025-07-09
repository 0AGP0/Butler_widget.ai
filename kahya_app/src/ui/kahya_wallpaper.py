from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QApplication, QDesktopWidget, QSystemTrayIcon,
                             QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QMutex
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QIcon
from PyQt5.QtWinExtras import QtWin
import sys
import os

# Retro bileşenleri import et
from .retro_components import (
    KahyaFace, RetroClock, RetroCalendar, 
    RetroChatbox, SoundWave, RetroNotes
)

class KahyaWallpaper(QWidget):
    command_received = pyqtSignal(str)  # Komut alındığında
    
    def __init__(self, db_path, usage_tracker=None):
        super().__init__()
        self.db_path = db_path
        self.usage_tracker = usage_tracker
        
        # Pencere ayarları
        self.setWindowTitle("Kahya AI Desktop Assistant")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Tam ekran yap
        self.setup_fullscreen()
        
        # UI bileşenleri
        self.setup_ui()
        
        # Sistem tray
        self.setup_system_tray()
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Her saniye güncelle
        
        # Thread güvenliği
        self.mutex = QMutex()
        
        # Kullanım takibini başlat
        if self.usage_tracker:
            self.usage_tracker.start_tracking()
            
    def setup_fullscreen(self):
        """Tam ekran ayarla"""
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        self.setGeometry(screen_geometry)
        
    def setup_ui(self):
        """UI'yi kur - istediğiniz layout'a göre"""
        # Ana layout
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Layout düzeni:
        # Sol üst: Saat
        self.clock = RetroClock()
        main_layout.addWidget(self.clock, 0, 0)
        
        # Orta üst: Envanter (gelecekte)
        self.inventory_placeholder = self.create_placeholder("ENVANTER")
        main_layout.addWidget(self.inventory_placeholder, 0, 1)
        
        # Sağ üst: Ses dalgası
        self.sound_wave = SoundWave()
        main_layout.addWidget(self.sound_wave, 0, 2)
        
        # Sol orta: Takvim
        self.calendar = RetroCalendar()
        main_layout.addWidget(self.calendar, 1, 0)
        
        # Orta: Kahya yüzü
        self.kahya_face = KahyaFace()
        main_layout.addWidget(self.kahya_face, 1, 1)
        
        # Sağ orta: Boş alan (gelecekte kullanım istatistikleri)
        self.stats_placeholder = self.create_placeholder("İSTATİSTİKLER")
        main_layout.addWidget(self.stats_placeholder, 1, 2)
        
        # Sol alt: Notlar
        self.notes = RetroNotes()
        main_layout.addWidget(self.notes, 2, 0)
        
        # Orta alt: Chatbox
        self.retro_chatbox = RetroChatbox()
        main_layout.addWidget(self.retro_chatbox, 2, 1)
        
        # Chatbox'tan Kahya yüzüne konuşma durumu sinyalini bağla
        self.retro_chatbox.kahya_talking.connect(self.kahya_face.set_talking)
        
        # Sağ alt: Kapı (gelecekte)
        self.door_placeholder = self.create_placeholder("KAPI")
        main_layout.addWidget(self.door_placeholder, 2, 2)
        
        # Layout ağırlıklarını ayarla
        main_layout.setRowStretch(0, 1)  # Üst satır
        main_layout.setRowStretch(1, 2)  # Orta satır daha büyük (Kahya yüzü için)
        main_layout.setRowStretch(2, 1)  # Alt satır
        
        main_layout.setColumnStretch(0, 1)  # Sol sütun
        main_layout.setColumnStretch(1, 2)  # Orta sütun daha büyük (Kahya yüzü için)
        main_layout.setColumnStretch(2, 1)  # Sağ sütun
        
    def create_placeholder(self, text):
        """Yer tutucu widget oluştur"""
        placeholder = QWidget()
        placeholder.setMinimumSize(180, 120)
        placeholder.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border: 2px solid #00ff00;
            }
        """)
        
        # Layout
        layout = QVBoxLayout(placeholder)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Başlık
        title = QLabel(text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #00ff00;
                background-color: #001100;
                padding: 3px;
            }
        """)
        layout.addWidget(title)
        
        # İçerik alanı
        content = QLabel("Yakında...")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
                font-size: 10px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(content)
        
        return placeholder
        
    def setup_system_tray(self):
        """Sistem tray'i kur"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Kahya AI Desktop Assistant")
        
        # Tray menüsü
        tray_menu = QMenu()
        
        # Gizle/Göster aksiyonu
        self.toggle_action = QAction("Gizle", self)
        self.toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(self.toggle_action)
        
        tray_menu.addSeparator()
        
        # Mikrofon aksiyonu
        self.mic_action = QAction("Mikrofonu Aç/Kapat", self)
        self.mic_action.triggered.connect(self.toggle_microphone)
        tray_menu.addAction(self.mic_action)
        
        tray_menu.addSeparator()
        
        # Çıkış aksiyonu
        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def toggle_visibility(self):
        """Görünürlüğü değiştir"""
        if self.isVisible():
            self.hide()
            self.toggle_action.setText("Göster")
        else:
            self.show()
            self.toggle_action.setText("Gizle")
            
    def toggle_microphone(self):
        """Mikrofonu aç/kapat"""
        if self.sound_wave.is_listening:
            self.sound_wave.stop_listening()
            self.mic_action.setText("Mikrofonu Aç")
        else:
            self.sound_wave.start_listening()
            self.mic_action.setText("Mikrofonu Kapat")
            
    def close_application(self):
        """Uygulamayı kapat"""
        reply = QMessageBox.question(
            self, 'Çıkış', 
            'Kahya AI Desktop Assistant\'ı kapatmak istediğinizden emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cleanup()
            QApplication.quit()
            
    def update_display(self):
        """Ekranı güncelle"""
        # Kahya'nın ifadesini güncelle (kullanım istatistiklerine göre)
        if self.usage_tracker:
            # Basit ifade değişimi (gelecekte daha karmaşık olabilir)
            import random
            expressions = ["neutral", "happy", "surprised"]
            if random.random() < 0.01:  # %1 şans
                self.kahya_face.set_expression(random.choice(expressions))
                
    def show_notification(self, title, message):
        """Bildirim göster"""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
        
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Yarı şeffaf arka plan
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        
        # Ana çerçeve
        painter.setPen(QPen(QColor(0, 200, 0), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.rect().adjusted(10, 10, -10, -10))
        
        # İç çerçeve
        painter.setPen(QPen(QColor(0, 100, 0), 1))
        painter.drawRect(self.rect().adjusted(15, 15, -15, -15))
        
        # Köşe dekorasyonları
        self.draw_corners(painter)
        
    def draw_corners(self, painter):
        """Köşe dekorasyonlarını çiz"""
        width = self.width()
        height = self.height()
        corner_size = 30
        
        painter.setPen(QPen(QColor(0, 200, 0), 3))
        
        # Sol üst köşe
        painter.drawLine(20, 20, corner_size, 20)
        painter.drawLine(20, 20, 20, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(width - corner_size, 20, width - 20, 20)
        painter.drawLine(width - 20, 20, width - 20, corner_size)
        
        # Sol alt köşe
        painter.drawLine(20, height - corner_size, 20, height - 20)
        painter.drawLine(20, height - 20, corner_size, height - 20)
        
        # Sağ alt köşe
        painter.drawLine(width - corner_size, height - 20, width - 20, height - 20)
        painter.drawLine(width - 20, height - corner_size, width - 20, height - 20)
        
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        if event.key() == Qt.Key_Escape:
            self.toggle_visibility()
        elif event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_M:
            self.toggle_microphone()
            
    def toggle_fullscreen(self):
        """Tam ekran modunu değiştir"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def mousePressEvent(self, event):
        """Fare tıklama olayı"""
        if event.button() == Qt.RightButton:
            # Sağ tık menüsü
            self.show_context_menu(event.pos())
            
    def show_context_menu(self, pos):
        """Bağlam menüsünü göster"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # Gizle/Göster
        toggle_action = menu.addAction("Gizle" if self.isVisible() else "Göster")
        toggle_action.triggered.connect(self.toggle_visibility)
        
        menu.addSeparator()
        
        # Mikrofon
        mic_action = menu.addAction("Mikrofonu Aç" if not self.sound_wave.is_listening else "Mikrofonu Kapat")
        mic_action.triggered.connect(self.toggle_microphone)
        
        menu.addSeparator()
        
        # Çıkış
        exit_action = menu.addAction("Çıkış")
        exit_action.triggered.connect(self.close_application)
        
        menu.exec_(self.mapToGlobal(pos))
        
    def resizeEvent(self, event):
        """Widget yeniden boyutlandırıldığında"""
        super().resizeEvent(event)
        self.update()
        
    def cleanup(self):
        """Temizlik"""
        # Zamanlayıcıları durdur
        self.update_timer.stop()
        
        # Bileşenleri temizle
        self.calendar.cleanup()
        self.clock.cleanup()
        self.retro_chatbox.cleanup()
        self.sound_wave.cleanup()
        self.kahya_face.cleanup()
        
        # Kullanım takibini durdur
        if self.usage_tracker:
            self.usage_tracker.cleanup()
            
        # Sistem tray'i kaldır
        if self.tray_icon:
            self.tray_icon.hide() 