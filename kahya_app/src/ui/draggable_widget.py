from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QMouseEvent, QPainter, QPen, QColor, QFont

class DraggableWidget(QWidget):
    """Sürüklenebilir widget sınıfı"""
    
    widget_moved = pyqtSignal(str, int, int)  # widget_name, x, y
    widget_toggled = pyqtSignal(str, bool)    # widget_name, visible
    
    def __init__(self, widget_name, title, parent=None):
        super().__init__(parent)
        self.widget_name = widget_name
        self.title = title
        self.is_dragging = False
        self.drag_position = QPoint()
        self.is_visible = True
        self.widget_manager = None  # Widget yönetici referansı
        self.monitor_manager = None  # Monitör yönetici referansı
        
        # Widget ayarları
        self.setWindowFlags(Qt.FramelessWindowHint)  # En üstte tut kapalı başlasın
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Focus policy - tuş olaylarını yakalamak için
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Minimum boyut
        self.setMinimumSize(150, 100)
        
        # Başlık çubuğu
        self.setup_title_bar()
        
        # Stil
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border: 2px solid #00ff00;
                border-radius: 8px;
            }
        """)
        
    def setup_title_bar(self):
        """Başlık çubuğunu kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Başlık çubuğu
        title_bar = QWidget()
        title_bar.setFixedHeight(25)
        title_bar.setStyleSheet("""
            QWidget {
                background-color: #001100;
                border: 1px solid #00ff00;
                border-radius: 3px;
            }
        """)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)
        
        # Başlık
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
                font-size: 10px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)
        
        # Kontrol butonları
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(2)
        
        # Gizle/Göster butonu
        self.toggle_btn = QPushButton("−")
        self.toggle_btn.setFixedSize(15, 15)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                border: 1px solid #00ff00;
                color: #00ff00;
                font-weight: bold;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #004400;
            }
            QPushButton:pressed {
                background-color: #002200;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_visibility)
        controls_layout.addWidget(self.toggle_btn)
        
        # Çark butonu (sadece yüz bileşeni için)
        if self.widget_name == "kahya_yuzu":
            self.settings_btn = QPushButton("⚙")
            self.settings_btn.setFixedSize(15, 15)
            self.settings_btn.setStyleSheet("""
                QPushButton {
                    background-color: #003300;
                    border: 1px solid #00ff00;
                    color: #00ff00;
                    font-weight: bold;
                    border-radius: 2px;
                    font-size: 8px;
                }
                QPushButton:hover {
                    background-color: #004400;
                }
                QPushButton:pressed {
                    background-color: #002200;
                }
            """)
            self.settings_btn.clicked.connect(self.open_control_panel)
            controls_layout.addWidget(self.settings_btn)
        
        title_layout.addLayout(controls_layout)
        layout.addWidget(title_bar)
        
        # İçerik alanı
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.content_widget)
        
    def set_content_widget(self, widget):
        """İçerik widget'ını ayarla"""
        layout = self.content_widget.layout()
        if layout is None:
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(5, 5, 5, 5)
        
        # Mevcut widget'ları temizle
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        layout.addWidget(widget)
        
    def toggle_visibility(self):
        """Widget'ı gizle/göster"""
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.toggle_btn.setText("−")
            self.show()
        else:
            self.toggle_btn.setText("+")
            self.hide()
        
        # Widget yöneticiye bildir
        self.widget_toggled.emit(self.widget_name, self.is_visible)
        
    def set_visibility(self, visible):
        """Widget görünürlüğünü ayarla"""
        self.is_visible = visible
        if self.is_visible:
            self.toggle_btn.setText("−")
            self.show()
        else:
            self.toggle_btn.setText("+")
            self.hide()
        
    def mousePressEvent(self, event: QMouseEvent):
        """Fare basma olayı"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # Widget'a focus ver (tuş olaylarını yakalamak için)
            self.setFocus()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Fare hareket olayı"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            new_pos = event.globalPos() - self.drag_position
            
            # Sınırları kontrol et ve çakışmaları önle
            constrained_pos = self.constrain_position(new_pos)
            
            self.move(constrained_pos)
            self.widget_moved.emit(self.widget_name, constrained_pos.x(), constrained_pos.y())
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Fare bırakma olayı"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            
    def keyPressEvent(self, event):
        """Tuş basma olayı - space tuşunu engelle"""
        # Space tuşunu ve diğer tehlikeli tuşları engelle
        if event.key() in [Qt.Key_Space, Qt.Key_Escape, Qt.Key_Delete, Qt.Key_Backspace]:
            event.accept()  # Bu tuşları yakala ve işleme
            return
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        """Tuş bırakma olayı - space tuşunu engelle"""
        # Space tuşunu ve diğer tehlikeli tuşları engelle
        if event.key() in [Qt.Key_Space, Qt.Key_Escape, Qt.Key_Delete, Qt.Key_Backspace]:
            event.accept()  # Bu tuşları yakala ve işleme
            return
        super().keyReleaseEvent(event)
            
    def show_context_menu(self, pos):
        """Bağlam menüsünü göster"""
        menu = QMenu(self)
        
        # Gizle/Göster
        toggle_action = menu.addAction("Gizle" if self.is_visible else "Göster")
        toggle_action.triggered.connect(self.toggle_visibility)
        
        menu.addSeparator()
        
        # En üstte tut
        stay_on_top_action = menu.addAction("En Üstte Tut")
        stay_on_top_action.setCheckable(True)
        stay_on_top_action.setChecked(self.windowFlags() & Qt.WindowStaysOnTopHint)
        stay_on_top_action.triggered.connect(self.toggle_stay_on_top)
        
        menu.exec_(self.mapToGlobal(pos))
        
    def toggle_stay_on_top(self):
        """En üstte tutma durumunu değiştir"""
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        
    def open_control_panel(self):
        """Kontrol panelini aç"""
        if hasattr(self, 'widget_manager') and self.widget_manager:
            # Widget yönetici üzerinden kontrol panelini aç
            self.widget_manager.show_control_panel()
        
    def set_widget_manager(self, widget_manager):
        """Widget yönetici referansını ayarla"""
        self.widget_manager = widget_manager
        
    def set_monitor_manager(self, monitor_manager):
        """Monitör yönetici referansını ayarla"""
        self.monitor_manager = monitor_manager
        
    def constrain_position(self, pos):
        """Pozisyonu sınırlar içinde tut ve çakışmaları önle"""
        from PyQt5.QtWidgets import QDesktopWidget
        
        # Widget boyutlarını al
        widget_width = self.width()
        widget_height = self.height()
        
        # Çoklu monitör desteği
        if self.monitor_manager:
            x, y = self.constrain_to_all_monitors(pos, widget_width, widget_height)
        else:
            # Tek monitör için eski yöntem
            desktop = QDesktopWidget()
            screen_geometry = desktop.screenGeometry()
            x = max(0, min(pos.x(), screen_geometry.width() - widget_width))
            y = max(0, min(pos.y(), screen_geometry.height() - widget_height))
        
        # Diğer widget'larla çakışma kontrolü
        if self.widget_manager:
            x, y = self.prevent_collision(x, y, widget_width, widget_height)
        
        return QPoint(x, y)
        
    def prevent_collision(self, x, y, width, height):
        """Diğer widget'larla çakışmayı önle"""
        if not self.widget_manager:
            return x, y
            
        # Bu widget'ın yeni geometrisi
        new_rect = QRect(x, y, width, height)
        
        # Diğer widget'larla çakışma kontrolü
        for other_name, other_widget in self.widget_manager.widgets.items():
            if other_name == self.widget_name or not other_widget.is_visible:
                continue
                
            other_rect = other_widget.geometry()
            
            # Çakışma varsa pozisyonu ayarla
            if new_rect.intersects(other_rect):
                # En yakın boş alanı bul
                x, y = self.find_nearest_free_position(x, y, width, height, other_rect)
                new_rect = QRect(x, y, width, height)
        
        return x, y
        
    def find_nearest_free_position(self, x, y, width, height, obstacle_rect):
        """En yakın boş pozisyonu bul"""
        # Çoklu monitör desteği
        if self.monitor_manager:
            return self.find_nearest_free_position_multi_monitor(x, y, width, height, obstacle_rect)
        else:
            # Tek monitör için eski yöntem
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_geometry = desktop.screenGeometry()
            
            # Olası pozisyonları dene
            possible_positions = [
                # Sağa kaydır
                (obstacle_rect.x() + obstacle_rect.width(), y),
                # Sola kaydır
                (obstacle_rect.x() - width, y),
                # Aşağı kaydır
                (x, obstacle_rect.y() + obstacle_rect.height()),
                # Yukarı kaydır
                (x, obstacle_rect.y() - height),
                # Çapraz pozisyonlar
                (obstacle_rect.x() + obstacle_rect.width(), obstacle_rect.y() + obstacle_rect.height()),
                (obstacle_rect.x() - width, obstacle_rect.y() - height),
            ]
            
            # En yakın pozisyonu bul
            best_x, best_y = x, y
            min_distance = float('inf')
            
            for pos_x, pos_y in possible_positions:
                # Ekran sınırları içinde mi kontrol et
                if (0 <= pos_x <= screen_geometry.width() - width and 
                    0 <= pos_y <= screen_geometry.height() - height):
                    
                    # Bu pozisyonda çakışma var mı kontrol et
                    test_rect = QRect(pos_x, pos_y, width, height)
                    collision = False
                    
                    for other_name, other_widget in self.widget_manager.widgets.items():
                        if other_name == self.widget_name or not other_widget.is_visible:
                            continue
                        if test_rect.intersects(other_widget.geometry()):
                            collision = True
                            break
                    
                    if not collision:
                        # Orijinal pozisyona olan mesafeyi hesapla
                        distance = ((pos_x - x) ** 2 + (pos_y - y) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            best_x, best_y = pos_x, pos_y
            
            return best_x, best_y
            
    def find_nearest_free_position_multi_monitor(self, x, y, width, height, obstacle_rect):
        """Çoklu monitör için en yakın boş pozisyonu bul"""
        # Tüm monitörlerin birleşik geometrisini hesapla
        total_geometry = QRect()
        for screen in self.monitor_manager.screens:
            if total_geometry.isNull():
                total_geometry = screen['geometry']
            else:
                total_geometry = total_geometry.united(screen['geometry'])
        
        # Olası pozisyonları dene
        possible_positions = [
            # Sağa kaydır
            (obstacle_rect.x() + obstacle_rect.width(), y),
            # Sola kaydır
            (obstacle_rect.x() - width, y),
            # Aşağı kaydır
            (x, obstacle_rect.y() + obstacle_rect.height()),
            # Yukarı kaydır
            (x, obstacle_rect.y() - height),
            # Çapraz pozisyonlar
            (obstacle_rect.x() + obstacle_rect.width(), obstacle_rect.y() + obstacle_rect.height()),
            (obstacle_rect.x() - width, obstacle_rect.y() - height),
        ]
        
        # En yakın pozisyonu bul
        best_x, best_y = x, y
        min_distance = float('inf')
        
        for pos_x, pos_y in possible_positions:
            # Tüm monitörler sınırları içinde mi kontrol et
            if (total_geometry.left() <= pos_x <= total_geometry.right() - width and 
                total_geometry.top() <= pos_y <= total_geometry.bottom() - height):
                
                # Bu pozisyonda çakışma var mı kontrol et
                test_rect = QRect(pos_x, pos_y, width, height)
                collision = False
                
                for other_name, other_widget in self.widget_manager.widgets.items():
                    if other_name == self.widget_name or not other_widget.is_visible:
                        continue
                    if test_rect.intersects(other_widget.geometry()):
                        collision = True
                        break
                
                if not collision:
                    # Orijinal pozisyona olan mesafeyi hesapla
                    distance = ((pos_x - x) ** 2 + (pos_y - y) ** 2) ** 0.5
                    if distance < min_distance:
                        min_distance = distance
                        best_x, best_y = pos_x, pos_y
        
        return best_x, best_y
        
    def constrain_to_all_monitors(self, pos, widget_width, widget_height):
        """Tüm monitörler arasında pozisyonu sınırla"""
        x, y = pos.x(), pos.y()
        
        # Tüm monitörlerin birleşik geometrisini hesapla
        total_geometry = QRect()
        for screen in self.monitor_manager.screens:
            if total_geometry.isNull():
                total_geometry = screen['geometry']
            else:
                total_geometry = total_geometry.united(screen['geometry'])
        
        # Widget'ın tamamen görünür olması için sınırları kontrol et
        # Sol sınır
        if x < total_geometry.left():
            x = total_geometry.left()
        # Sağ sınır
        if x + widget_width > total_geometry.right():
            x = total_geometry.right() - widget_width
        # Üst sınır
        if y < total_geometry.top():
            y = total_geometry.top()
        # Alt sınır
        if y + widget_height > total_geometry.bottom():
            y = total_geometry.bottom() - widget_height
        
        return x, y
        
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Yarı şeffaf arka plan
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawRoundedRect(self.rect(), 8, 8) 