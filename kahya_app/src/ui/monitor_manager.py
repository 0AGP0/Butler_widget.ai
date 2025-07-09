from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMenu, QAction
from PyQt5.QtCore import QObject, pyqtSignal, QRect
from PyQt5.QtGui import QScreen

class MonitorManager(QObject):
    """Çoklu monitör yönetici sınıfı"""
    
    monitor_changed = pyqtSignal(int)  # monitör indeksi
    
    def __init__(self):
        super().__init__()
        self.current_monitor = 0
        self.screens = []
        self.update_screens()
        
    def update_screens(self):
        """Ekranları güncelle"""
        self.screens = []
        desktop = QDesktopWidget()
        
        for i in range(desktop.screenCount()):
            geometry = desktop.screenGeometry(i)
            self.screens.append({
                'index': i,
                'geometry': geometry,
                'available_geometry': desktop.availableGeometry(i),
                'name': f"Monitör {i+1}"
            })
            
    def get_current_screen_geometry(self):
        """Mevcut monitörün geometrisini al"""
        if self.screens and self.current_monitor < len(self.screens):
            return self.screens[self.current_monitor]['geometry']
        return QRect(0, 0, 1920, 1080)  # Varsayılan
        
    def get_screen_geometry(self, monitor_index):
        """Belirli monitörün geometrisini al"""
        if 0 <= monitor_index < len(self.screens):
            return self.screens[monitor_index]['geometry']
        return QRect(0, 0, 1920, 1080)
        
    def switch_to_monitor(self, monitor_index):
        """Monitör değiştir"""
        if 0 <= monitor_index < len(self.screens):
            self.current_monitor = monitor_index
            self.monitor_changed.emit(monitor_index)
            
    def get_monitor_menu(self, parent=None):
        """Monitör seçim menüsü oluştur"""
        menu = QMenu("Monitör Seç", parent)
        
        for i, screen in enumerate(self.screens):
            action = QAction(f"{screen['name']} ({screen['geometry'].width()}x{screen['geometry'].height()})", parent)
            action.setCheckable(True)
            action.setChecked(i == self.current_monitor)
            action.triggered.connect(lambda checked, idx=i: self.switch_to_monitor(idx))
            menu.addAction(action)
            
        return menu
        
    def get_monitor_count(self):
        """Monitör sayısını al"""
        return len(self.screens)
        
    def get_current_monitor_index(self):
        """Mevcut monitör indeksini al"""
        return self.current_monitor 