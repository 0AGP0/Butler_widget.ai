import json
import os
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QObject, pyqtSignal
from .draggable_widget import DraggableWidget

class WidgetManager(QObject):
    """Widget yönetici sınıfı"""
    
    config_changed = pyqtSignal()
    
    def __init__(self, config_file="widget_config.json"):
        super().__init__()
        # Tam dosya yolu oluştur
        import os
        if not os.path.isabs(config_file):
            # Mevcut çalışma dizinini al
            current_dir = os.getcwd()
            self.config_file = os.path.join(current_dir, config_file)
        else:
            self.config_file = config_file
            
        self.widgets = {}
        self.config = self.load_config()
        self.current_monitor = self.config.get("current_monitor", 0)
        self.monitor_manager = None  # Monitör yönetici referansı
        
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Konfigürasyon yükleme hatası: {e}")
        
        # Varsayılan konfigürasyon
        return {
            "saat": {"x": 50, "y": 50, "visible": True},
            "takvim": {"x": 50, "y": 200, "visible": True},
            "kahya_yuzu": {"x": 300, "y": 150, "visible": True},
            "sohbet": {"x": 937, "y": 179, "visible": True},
            "ses_dalgasi": {"x": 800, "y": 50, "visible": False},
            "notlar": {"x": 550, "y": 400, "visible": True},
            "current_monitor": 0
        }
        
    def save_config(self):
        """Konfigürasyonu kaydet"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.config_changed.emit()
        except Exception as e:
            print(f"Konfigürasyon kaydetme hatası: {e}")
            
    def create_widget(self, widget_name, title, content_widget):
        """Widget oluştur"""
        if widget_name in self.widgets:
            return self.widgets[widget_name]
            
        # Sürüklenebilir widget oluştur
        draggable_widget = DraggableWidget(widget_name, title)
        draggable_widget.set_content_widget(content_widget)
        
        # Widget yönetici referansını ayarla
        draggable_widget.set_widget_manager(self)
        
        # Monitör yönetici referansını ayarla
        if self.monitor_manager:
            draggable_widget.set_monitor_manager(self.monitor_manager)
        
        # Konfigürasyondan pozisyon ve görünürlük ayarla
        if widget_name in self.config:
            config = self.config[widget_name]
            draggable_widget.move(config.get("x", 50), config.get("y", 50))
            visible = config.get("visible", True)
            draggable_widget.set_visibility(visible)
        
        # Sinyalleri bağla
        draggable_widget.widget_moved.connect(self.on_widget_moved)
        draggable_widget.widget_toggled.connect(self.on_widget_toggled)
        
        self.widgets[widget_name] = draggable_widget
        return draggable_widget
        
    def on_widget_moved(self, widget_name, x, y):
        """Widget taşındığında"""
        if widget_name in self.config:
            self.config[widget_name]["x"] = x
            self.config[widget_name]["y"] = y
            self.save_config()
            
    def on_widget_toggled(self, widget_name, visible):
        """Widget gizlendiğinde/gösterildiğinde"""
        if widget_name in self.config:
            self.config[widget_name]["visible"] = visible
            self.save_config()
            
    def set_current_monitor(self, monitor_index):
        """Mevcut monitörü ayarla"""
        self.current_monitor = monitor_index
        self.config["current_monitor"] = monitor_index
        self.save_config()
        
    def set_monitor_manager(self, monitor_manager):
        """Monitör yönetici referansını ayarla"""
        self.monitor_manager = monitor_manager
        # Mevcut widget'lara da monitör yönetici referansını ayarla
        for widget in self.widgets.values():
            widget.set_monitor_manager(monitor_manager)
            
    def show_all_widgets(self):
        """Tüm widget'ları göster"""
        for widget in self.widgets.values():
            widget.set_visibility(True)
                
    def hide_all_widgets(self):
        """Tüm widget'ları gizle"""
        for widget in self.widgets.values():
            widget.set_visibility(False)
            
    def reset_positions(self):
        """Widget pozisyonlarını sıfırla"""
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        
        # Varsayılan pozisyonlar
        default_positions = {
            "saat": (50, 50),
            "takvim": (50, 200),
            "kahya_yuzu": (300, 150),
            "sohbet": (screen_geometry.width() - 250, 179),
            "ses_dalgasi": (screen_geometry.width() - 200, 50),
            "notlar": (550, 400)
        }
        
        for widget_name, (x, y) in default_positions.items():
            if widget_name in self.widgets:
                self.widgets[widget_name].move(x, y)
                if widget_name in self.config:
                    self.config[widget_name]["x"] = x
                    self.config[widget_name]["y"] = y
                    
        self.save_config()
        
    def cleanup(self):
        """Temizlik"""
        for widget in self.widgets.values():
            widget.close()
        self.widgets.clear()
        
    def show_control_panel(self):
        """Kontrol panelini göster"""
        # Ana wallpaper'a sinyal gönder
        if hasattr(self, 'parent') and self.parent:
            self.parent.show_control_menu() 