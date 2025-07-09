from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QApplication, 
                             QDesktopWidget, QSystemTrayIcon, QMenu, QAction, 
                             QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QMutex
from PyQt5.QtGui import QPainter, QColor, QBrush, QKeySequence
from PyQt5.QtWidgets import QShortcut
import os

# Retro bileşenleri import et
from .retro_components import (
    KahyaFace, RetroClock, RetroCalendar, 
    RetroChatbox, SoundWave, RetroNotes, RetroInventory
)

# Widget yönetici import et
from .widget_manager import WidgetManager
from .monitor_manager import MonitorManager
from .control_menu import ControlMenu

class KahyaWallpaper(QWidget):
    command_received = pyqtSignal(str)  # Komut alındığında
    
    def __init__(self, db_path, usage_tracker=None):
        super().__init__()
        self.db_path = db_path
        self.usage_tracker = usage_tracker
        
        # Pencere ayarları - widget tarzında
        self.setWindowTitle("Kahya AI Desktop Assistant")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Focus policy - kısayol tuşları için
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Widget yönetici
        self.widget_manager = WidgetManager("widget_config.json")
        self.widget_manager.parent = self  # Parent referansını ayarla
        
        # Monitör yönetici
        self.monitor_manager = MonitorManager()
        self.monitor_manager.monitor_changed.connect(self.on_monitor_changed)
        
        # Widget yöneticiye monitör yönetici referansını ayarla
        self.widget_manager.set_monitor_manager(self.monitor_manager)
        
        # Kaydedilmiş monitörü yükle
        saved_monitor = self.widget_manager.current_monitor
        if saved_monitor < self.monitor_manager.get_monitor_count():
            self.monitor_manager.switch_to_monitor(saved_monitor)
        
        # Tam ekran yap
        self.setup_fullscreen()
        
        # UI bileşenleri
        self.setup_ui()
        
        # Kontrol menüsü
        self.control_menu = ControlMenu(self.widget_manager, self.monitor_manager, self)
        self.control_menu.widget_toggled.connect(self.on_widget_toggled)
        self.control_menu.positions_reset.connect(self.widget_manager.reset_positions)
        self.control_menu.monitor_changed.connect(self.monitor_manager.switch_to_monitor)
        
        # Kontrol menüsünü sağ üst köşeye yerleştir
        screen_geometry = self.screen().geometry()
        menu_x = screen_geometry.width() - 300 - 50  # 300 genişlik + 50 margin
        menu_y = 50
        self.control_menu.move(menu_x, menu_y)
        self.control_menu.show()
        
        # Sistem tray
        self.setup_system_tray()
        
        # Global kısayol tuşları
        self.setup_global_shortcuts()
        
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
        screen_geometry = self.monitor_manager.get_current_screen_geometry()
        self.setGeometry(screen_geometry)
        
    def setup_ui(self):
        """UI'yi kur - sürüklenebilir widget'lar olarak"""
        # Widget'ları oluştur
        self.create_widgets()
        

        
    def create_widgets(self):
        """Sürüklenebilir widget'ları oluştur"""
        # Saat widget'ı
        self.clock = RetroClock()
        self.clock_widget = self.widget_manager.create_widget("saat", "SAAT", self.clock)
        
        # Takvim widget'ı
        self.calendar = RetroCalendar()
        self.calendar_widget = self.widget_manager.create_widget("takvim", "TAKVİM", self.calendar)
        
        # Kahya yüzü widget'ı
        self.kahya_face = KahyaFace()
        self.kahya_widget = self.widget_manager.create_widget("kahya_yuzu", "KAHYA", self.kahya_face)
        
        # Chatbox widget'ı
        self.retro_chatbox = RetroChatbox()
        self.chatbox_widget = self.widget_manager.create_widget("sohbet", "SOHBET", self.retro_chatbox)
        
        # Chatbox'tan Kahya yüzüne konuşma durumu sinyalini bağla
        self.retro_chatbox.kahya_talking.connect(self.kahya_face.set_talking)
        
        # Ses dalgası widget'ı
        self.sound_wave = SoundWave()
        self.sound_widget = self.widget_manager.create_widget("ses_dalgasi", "SES", self.sound_wave)
        
        # Notlar widget'ı
        self.notes = RetroNotes()
        self.notes_widget = self.widget_manager.create_widget("notlar", "NOTLAR", self.notes)
        
        # Envanter widget'ı
        self.inventory = RetroInventory()
        self.inventory_widget = self.widget_manager.create_widget("envanter", "ENVANTER", self.inventory)
        
        # Tüm widget'ları göster
        self.widget_manager.show_all_widgets()
        
    def on_monitor_changed(self, monitor_index):
        """Monitör değiştiğinde"""
        # Ana pencereyi yeni monitöre taşı
        screen_geometry = self.monitor_manager.get_screen_geometry(monitor_index)
        self.setGeometry(screen_geometry)
        
        # Widget pozisyonlarını yeni monitöre göre ayarla
        self.adjust_widget_positions_for_monitor(monitor_index)
        
        # Konfigürasyona kaydet
        self.widget_manager.set_current_monitor(monitor_index)
        
    def adjust_widget_positions_for_monitor(self, monitor_index):
        """Widget pozisyonlarını monitöre göre ayarla"""
        screen_geometry = self.monitor_manager.get_screen_geometry(monitor_index)
        
        # Widget'ları yeni monitörün sınırları içinde tut
        for widget_name, widget in self.widget_manager.widgets.items():
            widget_geometry = widget.geometry()
            
            # Widget'ı yeni monitörün sınırları içinde tut
            new_x = max(0, min(widget_geometry.x(), screen_geometry.width() - widget_geometry.width()))
            new_y = max(0, min(widget_geometry.y(), screen_geometry.height() - widget_geometry.height()))
            
            widget.move(new_x, new_y)
            
            # Konfigürasyonu güncelle
            if widget_name in self.widget_manager.config:
                self.widget_manager.config[widget_name]["x"] = new_x
                self.widget_manager.config[widget_name]["y"] = new_y
                
        self.widget_manager.save_config()
        
    def on_widget_toggled(self, widget_name, visible):
        """Widget gizlendiğinde/gösterildiğinde"""
        if widget_name in self.widget_manager.widgets:
            widget = self.widget_manager.widgets[widget_name]
            widget.set_visibility(visible)
        
    def toggle_all_widgets(self):
        """Tüm widget'ları gizle/göster"""
        all_visible = all(widget.is_visible for widget in self.widget_manager.widgets.values())
        
        if all_visible:
            # Tümünü gizle
            for widget in self.widget_manager.widgets.values():
                widget.set_visibility(False)
        else:
            # Tümünü göster
            for widget in self.widget_manager.widgets.values():
                widget.set_visibility(True)
                
    def show_hidden_widgets(self):
        """Gizli widget'ları göster"""
        for widget in self.widget_manager.widgets.values():
            if not widget.is_visible:
                widget.set_visibility(True)
                
    def setup_global_shortcuts(self):
        """Global kısayol tuşlarını kur"""
        # Ctrl+Shift+C: Kontrol menüsünü göster
        self.control_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.control_shortcut.activated.connect(self.show_control_menu)
        
        # Ctrl+Shift+W: Gizli widget'ları göster
        self.widget_shortcut = QShortcut(QKeySequence("Ctrl+Shift+W"), self)
        self.widget_shortcut.activated.connect(self.show_hidden_widgets)
        
        # Ctrl+Shift+A: Tüm widget'ları gizle/göster
        self.toggle_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), self)
        self.toggle_all_shortcut.activated.connect(self.toggle_all_widgets)
        
        # Ctrl+Shift+H: Ana uygulamayı gizle/göster
        self.hide_shortcut = QShortcut(QKeySequence("Ctrl+Shift+H"), self)
        self.hide_shortcut.activated.connect(self.toggle_visibility)
        

        
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
        
        # Kontrol menüsü
        control_menu_action = QAction("Kontrol Menüsü", self)
        control_menu_action.triggered.connect(self.toggle_control_menu)
        tray_menu.addAction(control_menu_action)
        
        # Kontrol menüsünü göster (gizliyse)
        show_control_action = QAction("Kontrol Menüsünü Göster (Ctrl+Shift+C)", self)
        show_control_action.triggered.connect(self.show_control_menu)
        tray_menu.addAction(show_control_action)
        
        # Gizli widget'ları göster
        show_hidden_action = QAction("Gizli Widget'ları Göster (Ctrl+Shift+W)", self)
        show_hidden_action.triggered.connect(self.show_hidden_widgets)
        tray_menu.addAction(show_hidden_action)
        
        # Tüm widget'ları gizle/göster
        toggle_all_action = QAction("Tüm Widget'ları Gizle/Göster (Ctrl+Shift+A)", self)
        toggle_all_action.triggered.connect(self.toggle_all_widgets)
        tray_menu.addAction(toggle_all_action)
        
        tray_menu.addSeparator()
        
        # Widget yönetimi
        widget_menu = tray_menu.addMenu("Widget Yönetimi")
        
        # Tümünü gizle/göster
        self.toggle_all_action = QAction("Tümünü Gizle", self)
        self.toggle_all_action.triggered.connect(self.toggle_all_widgets)
        widget_menu.addAction(self.toggle_all_action)
        
        # Gizli widget'ları göster
        show_hidden_action = QAction("Gizli Widget'ları Göster", self)
        show_hidden_action.triggered.connect(self.show_hidden_widgets)
        widget_menu.addAction(show_hidden_action)
        
        # Pozisyonları sıfırla
        reset_action = QAction("Pozisyonları Sıfırla", self)
        reset_action.triggered.connect(self.widget_manager.reset_positions)
        widget_menu.addAction(reset_action)
        
        tray_menu.addSeparator()
        
        # Monitör seçimi (birden fazla monitör varsa)
        if self.monitor_manager.get_monitor_count() > 1:
            monitor_menu = tray_menu.addMenu("Monitör Seç")
            for i, screen in enumerate(self.monitor_manager.screens):
                action = QAction(f"{screen['name']} ({screen['geometry'].width()}x{screen['geometry'].height()})", self)
                action.setCheckable(True)
                action.setChecked(i == self.monitor_manager.get_current_monitor_index())
                action.triggered.connect(lambda checked, idx=i: self.monitor_manager.switch_to_monitor(idx))
                monitor_menu.addAction(action)
        
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
            
    def toggle_control_menu(self):
        """Kontrol menüsünü gizle/göster"""
        if hasattr(self, 'control_menu'):
            if self.control_menu.isVisible():
                self.control_menu.hide()
            else:
                self.control_menu.show()
                self.control_menu.raise_()
                
    def show_control_menu(self):
        """Kontrol menüsünü göster (gizliyse)"""
        if hasattr(self, 'control_menu'):
            self.control_menu.show()
            self.control_menu.raise_()
            # Kontrol menüsünü sağ üst köşeye yerleştir
            screen_geometry = self.screen().geometry()
            menu_x = screen_geometry.width() - 300 - 50  # 300 genişlik + 50 margin
            menu_y = 50
            self.control_menu.move(menu_x, menu_y)
            # Ana pencereye focus ver (kısayol tuşları için)
            self.setFocus()
            
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
            import random
            expressions = ["neutral", "happy", "surprised"]
            if random.random() < 0.01:  # %1 şans
                self.kahya_face.set_expression(random.choice(expressions))
                
    def show_notification(self, title, message):
        """Bildirim göster"""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
        
    def paintEvent(self, event):
        """Özel çizim - widget tarzında"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Tamamen şeffaf arka plan
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
    def keyPressEvent(self, event):
        """Tuş basma olayı"""
        if event.key() == Qt.Key_Escape:
            self.toggle_visibility()
        elif event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_M:
            self.toggle_microphone()
        elif event.key() == Qt.Key_Space:
            # Space tuşunu engelle
            event.accept()
            return
        super().keyPressEvent(event)
            
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
        elif event.button() == Qt.LeftButton:
            # Sol tık - masaüstüne odaklan
            self.setFocus()
            # Widget'ların arkasındaki masaüstüne tıklama geçir
            event.ignore()
            
    def show_context_menu(self, pos):
        """Bağlam menüsünü göster"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu(self)
        
        # Gizle/Göster
        toggle_action = menu.addAction("Gizle" if self.isVisible() else "Göster")
        toggle_action.triggered.connect(self.toggle_visibility)
        
        menu.addSeparator()
        
        # Kontrol menüsü
        control_menu_action = menu.addAction("Kontrol Menüsü")
        control_menu_action.triggered.connect(self.toggle_control_menu)
        
        menu.addSeparator()
        
        # Widget yönetimi
        widget_menu = menu.addMenu("Widget Yönetimi")
        
        # Tümünü gizle/göster
        toggle_all_action = menu.addAction("Tümünü Gizle" if all(widget.is_visible for widget in self.widget_manager.widgets.values()) else "Tümünü Göster")
        toggle_all_action.triggered.connect(self.toggle_all_widgets)
        widget_menu.addAction(toggle_all_action)
        
        # Pozisyonları sıfırla
        reset_action = menu.addAction("Pozisyonları Sıfırla")
        reset_action.triggered.connect(self.widget_manager.reset_positions)
        widget_menu.addAction(reset_action)
        
        menu.addSeparator()
        
        # Monitör seçimi (birden fazla monitör varsa)
        if self.monitor_manager.get_monitor_count() > 1:
            monitor_menu = menu.addMenu("Monitör Seç")
            for i, screen in enumerate(self.monitor_manager.screens):
                action = QAction(f"{screen['name']} ({screen['geometry'].width()}x{screen['geometry'].height()})", self)
                action.setCheckable(True)
                action.setChecked(i == self.monitor_manager.get_current_monitor_index())
                action.triggered.connect(lambda checked, idx=i: self.monitor_manager.switch_to_monitor(idx))
                monitor_menu.addAction(action)
        
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
        
        # Widget yöneticiyi temizle
        if hasattr(self, 'widget_manager'):
            self.widget_manager.cleanup()
        
        # Bileşenleri temizle
        if hasattr(self, 'calendar'):
            self.calendar.cleanup()
        if hasattr(self, 'clock'):
            self.clock.cleanup()
        if hasattr(self, 'retro_chatbox'):
            self.retro_chatbox.cleanup()
        if hasattr(self, 'sound_wave'):
            self.sound_wave.cleanup()
        if hasattr(self, 'kahya_face'):
            self.kahya_face.cleanup()
        
        # Kullanım takibini durdur
        if self.usage_tracker:
            self.usage_tracker.cleanup()
            
        # Sistem tray'i kaldır
        if self.tray_icon:
            self.tray_icon.hide() 