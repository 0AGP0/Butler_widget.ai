from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QGridLayout,
                             QSlider, QCheckBox, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient

class ControlMenu(QWidget):
    """Gelişmiş kontrol menü widget'ı"""
    
    widget_toggled = pyqtSignal(str, bool)  # widget_name, visible
    all_toggled = pyqtSignal(bool)  # visible
    positions_reset = pyqtSignal()
    monitor_changed = pyqtSignal(int)  # monitor_index
    
    def __init__(self, widget_manager, monitor_manager, parent=None):
        super().__init__(parent)
        self.widget_manager = widget_manager
        self.monitor_manager = monitor_manager
        self.is_collapsed = False
        self.is_dragging = False
        self.drag_position = None
        
        # Widget ayarları - sürüklenebilir
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # Focus policy - tuş olaylarını yakalamak için
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Widget ayarları
        self.setFixedWidth(300)
        self.setMinimumHeight(400)
        self.setMaximumHeight(600)
        
        # Stil
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 240);
                border: 2px solid #00ff00;
                border-radius: 15px;
                color: #00ff00;
                font-family: 'Courier';
            }
        """)
        
        # UI kurulumu
        self.setup_ui()
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_widget_states)
        self.update_timer.start(1000)  # Her saniye güncelle
        
    def mousePressEvent(self, event):
        """Fare basma olayı"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            # Widget'a focus ver (tuş olaylarını yakalamak için)
            self.setFocus()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Fare hareket olayı"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
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
        
    def setup_ui(self):
        """UI'yi kur"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Başlık
        self.setup_header()
        
        # Ana içerik alanı
        self.setup_content()
        
        # Alt kısım
        self.setup_footer()
        
        # Widget referanslarını sakla
        self.header = self.layout().itemAt(0).widget()
        self.content_widget = self.layout().itemAt(1).widget()
        self.footer = self.layout().itemAt(2).widget()
        
    def setup_header(self):
        """Başlık kısmını kur"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #001100, stop:1 #003300);
                border: 1px solid #00ff00;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 8, 15, 8)
        
        # Sürükleme göstergesi
        drag_icon = QLabel("☰")
        drag_icon.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        header_layout.addWidget(drag_icon)
        
        # Başlık
        title = QLabel("KAHYA KONTROL PANELİ")
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                border: none;

            }
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Daralt/Genişlet butonu
        self.collapse_btn = QPushButton("−")
        self.collapse_btn.setFixedSize(30, 30)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004400, stop:1 #005500);
                border: 2px solid #00ff00;
                color: #00ff00;
                font-weight: bold;
                font-size: 14px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005500, stop:1 #006600);
                border: 2px solid #00ff00;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003300, stop:1 #004400);
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        header_layout.addWidget(self.collapse_btn)
        
        self.layout().addWidget(header)
        
    def setup_content(self):
        """Ana içerik kısmını kur"""
        # Kaydırılabilir alan
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #001100;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #00ff00;
                border-radius: 5px;
            }
        """)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Widget kontrol grubu
        self.setup_widget_controls(content_layout)
        
        # Monitör kontrol grubu
        self.setup_monitor_controls(content_layout)
        
        # Sistem kontrol grubu
        self.setup_system_controls(content_layout)
        
        scroll_area.setWidget(content_widget)
        self.layout().addWidget(scroll_area)
        
    def setup_widget_controls(self, parent_layout):
        """Widget kontrollerini kur"""
        group = QGroupBox("WIDGET YÖNETİMİ")
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                border: 1px solid #00ff00;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Tümünü gizle/göster
        self.toggle_all_btn = QPushButton("TÜMÜNÜ GİZLE")
        self.toggle_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003300, stop:1 #004400);
                border: 2px solid #00ff00;
                color: #00ff00;
                font-weight: bold;
                font-size: 12px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004400, stop:1 #005500);
                border: 2px solid #00ff00;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #002200, stop:1 #003300);
            }
        """)
        self.toggle_all_btn.clicked.connect(self.toggle_all_widgets)
        group_layout.addWidget(self.toggle_all_btn)
        
        # Pozisyonları sıfırla
        reset_btn = QPushButton("POZİSYONLARI SIFIRLA")
        reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #330000, stop:1 #440000);
                border: 2px solid #ff0000;
                color: #ff0000;
                font-weight: bold;
                font-size: 12px;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #440000, stop:1 #550000);
                border: 2px solid #ff0000;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #220000, stop:1 #330000);
            }
        """)
        reset_btn.clicked.connect(self.positions_reset.emit)
        group_layout.addWidget(reset_btn)
        
        # Widget listesi
        self.widget_controls = {}
        widget_names = {
            "saat": "SAAT",
            "takvim": "TAKVİM", 
            "kahya_yuzu": "KAHYA YÜZÜ",
            "sohbet": "SOHBET",
            "ses_dalgasi": "SES DALGASI",
            "notlar": "NOTLAR"
        }
        
        for widget_name, display_name in widget_names.items():
            control = self.create_widget_control(widget_name, display_name)
            self.widget_controls[widget_name] = control
            group_layout.addWidget(control)
        
        parent_layout.addWidget(group)
        
    def create_widget_control(self, widget_name, display_name):
        """Widget kontrolü oluştur"""
        control = QFrame()
        control.setFixedHeight(50)
        control.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 30, 0, 120), stop:1 rgba(0, 20, 0, 100));
                border: 2px solid #00aa00;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 50, 0, 150), stop:1 rgba(0, 40, 0, 130));
                border: 2px solid #00ff00;
            }
        """)
        
        layout = QHBoxLayout(control)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Widget ikonu
        icon_map = {
            "saat": "🕐",
            "takvim": "📅", 
            "kahya_yuzu": "🤖",
            "sohbet": "💬",
            "ses_dalgasi": "🎵",
            "notlar": "📝"
        }
        
        icon = QLabel(icon_map.get(widget_name, "📋"))
        icon.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(icon)
        
        # Widget adı
        label = QLabel(display_name)
        label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-weight: bold;
                font-size: 12px;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(label)
        
        layout.addStretch()
        
        # Gizle/Göster checkbox
        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
            QCheckBox {
                color: #00ff00;
                background: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #00ff00;
                border-radius: 4px;
                background-color: #001100;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #00ff00;
                background-color: #002200;
            }
            QCheckBox::indicator:checked {
                background-color: #00ff00;
                border: 2px solid #00ff00;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzIDRMNiAxMUwzIDgiIHN0cm9rZT0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
        """)
        checkbox.setChecked(True)
        checkbox.toggled.connect(lambda checked, name=widget_name: self.widget_toggled.emit(name, checked))
        layout.addWidget(checkbox)
        
        return control
        
    def setup_monitor_controls(self, parent_layout):
        """Monitör kontrollerini kur"""
        if self.monitor_manager.get_monitor_count() <= 1:
            return
            
        group = QGroupBox("MONİTÖR SEÇİMİ")
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                border: 1px solid #00ff00;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        
        # Monitör seçici
        self.monitor_combo = QComboBox()
        self.monitor_combo.setStyleSheet("""
            QComboBox {
                background-color: #001100;
                border: 1px solid #00ff00;
                color: #00ff00;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIgNEw2IDhMMTAgNCIgc3Ryb2tlPSIjMDBmZjAwIiBzdHJva2Utd2lkdGg9IjIiLz4KPC9zdmc+);
            }
        """)
        
        for i, screen in enumerate(self.monitor_manager.screens):
            self.monitor_combo.addItem(
                f"{screen['name']} ({screen['geometry'].width()}x{screen['geometry'].height()})", 
                i
            )
        
        self.monitor_combo.setCurrentIndex(self.monitor_manager.get_current_monitor_index())
        self.monitor_combo.currentIndexChanged.connect(self.on_monitor_changed)
        group_layout.addWidget(self.monitor_combo)
        
        parent_layout.addWidget(group)
        
    def setup_system_controls(self, parent_layout):
        """Sistem kontrollerini kur"""
        group = QGroupBox("SİSTEM")
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                border: 1px solid #00ff00;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        
        # Şeffaflık ayarı
        opacity_layout = QHBoxLayout()
        opacity_label = QLabel("ŞEFFAFLIK:")
        opacity_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        opacity_layout.addWidget(opacity_label)
        
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #00ff00;
                height: 8px;
                background: #001100;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00ff00;
                border: 1px solid #00ff00;
                width: 16px;
                border-radius: 8px;
            }
        """)
        opacity_layout.addWidget(self.opacity_slider)
        
        group_layout.addLayout(opacity_layout)
        
        parent_layout.addWidget(group)
        
    def setup_footer(self):
        """Alt kısmı kur"""
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #003300, stop:1 #001100);
                border: 1px solid #00ff00;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 8, 15, 8)
        
        # Durum etiketi
        self.status_label = QLabel("🟢 Hazır")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        footer_layout.addWidget(self.status_label)
        
        footer_layout.addStretch()
        
        # Kapat butonu
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #440000, stop:1 #550000);
                border: 2px solid #ff0000;
                color: #ff0000;
                font-weight: bold;
                font-size: 16px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #550000, stop:1 #660000);
                border: 2px solid #ff0000;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #330000, stop:1 #440000);
            }
        """)
        close_btn.clicked.connect(self.hide)
        footer_layout.addWidget(close_btn)
        
        self.layout().addWidget(footer)
        
    def toggle_collapse(self):
        """Menüyü daralt/genişlet"""
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            # Daralt - çark sembolüne dönüştür
            self.collapse_btn.setText("⚙")
            self.collapse_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #004400, stop:1 #005500);
                    border: 2px solid #00ff00;
                    color: #00ff00;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #005500, stop:1 #006600);
                    border: 2px solid #00ff00;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #003300, stop:1 #004400);
                }
            """)
            # Tüm widget'ları gizle
            self.header.hide()
            self.content_widget.hide()
            self.footer.hide()
            
            # Sadece çark butonunu göster
            self.collapse_btn.setParent(self)
            self.collapse_btn.move(25, 15)  # Merkeze yerleştir
            self.collapse_btn.show()
            self.setFixedSize(80, 60)  # Küçük çark boyutu
        else:
            # Genişlet
            self.collapse_btn.setText("−")
            self.collapse_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #004400, stop:1 #005500);
                    border: 2px solid #00ff00;
                    color: #00ff00;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 15px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #005500, stop:1 #006600);
                    border: 2px solid #00ff00;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #003300, stop:1 #004400);
                }
            """)
            # Çark butonunu header'a geri ekle
            self.collapse_btn.setParent(self.header)
            header_layout = self.header.layout()
            header_layout.addWidget(self.collapse_btn)
            
            # Tüm kısımları göster
            self.header.show()
            self.content_widget.show()
            self.footer.show()
            self.setFixedSize(300, 400)  # Tam boyut
            
    def toggle_all_widgets(self):
        """Tüm widget'ları gizle/göster"""
        all_visible = all(control.findChild(QCheckBox).isChecked() 
                         for control in self.widget_controls.values())
        
        if all_visible:
            # Tümünü gizle
            for control in self.widget_controls.values():
                checkbox = control.findChild(QCheckBox)
                checkbox.setChecked(False)
            self.toggle_all_btn.setText("TÜMÜNÜ GÖSTER")
        else:
            # Tümünü göster
            for control in self.widget_controls.values():
                checkbox = control.findChild(QCheckBox)
                checkbox.setChecked(True)
            self.toggle_all_btn.setText("TÜMÜNÜ GİZLE")
            
    def on_monitor_changed(self, index):
        """Monitör değiştiğinde"""
        self.monitor_changed.emit(index)
        
    def update_widget_states(self):
        """Widget durumlarını güncelle"""
        if not hasattr(self, 'widget_controls'):
            return
            
        for widget_name, control in self.widget_controls.items():
            if widget_name in self.widget_manager.widgets:
                widget = self.widget_manager.widgets[widget_name]
                checkbox = control.findChild(QCheckBox)
                if checkbox.isChecked() != widget.is_visible:
                    checkbox.setChecked(widget.is_visible)
                    
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gölge efekti
        painter.setPen(QPen(QColor(0, 255, 0, 80), 4))
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawRoundedRect(self.rect().adjusted(4, 4, 4, 4), 18, 18)
        
        # İç gölge
        painter.setPen(QPen(QColor(0, 255, 0, 30), 2))
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 16, 16) 