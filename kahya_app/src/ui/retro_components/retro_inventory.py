from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QPushButton, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap

class InventorySlot(QFrame):
    """Envanter slot'u - Minecraft tarzında"""
    
    item_clicked = pyqtSignal(int, str)  # slot_index, item_name
    
    def __init__(self, slot_index, parent=None):
        super().__init__(parent)
        self.slot_index = slot_index
        self.item_name = ""
        self.item_count = 0
        self.item_icon = None
        self.is_selected = False
        self.is_hovered = False
        
        # Slot ayarları
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.hover_color = QColor(120, 255, 160)  # Hover rengi
        self.selected_color = QColor(160, 255, 200)  # Seçili rengi
        
    def set_item(self, item_name, count=1, icon=None):
        """Slot'a item ekle"""
        self.item_name = item_name
        self.item_count = count
        self.item_icon = icon
        self.update()
        
    def clear_item(self):
        """Slot'u temizle"""
        self.item_name = ""
        self.item_count = 0
        self.item_icon = None
        self.update()
        
    def mousePressEvent(self, event):
        """Fare tıklama olayı"""
        if event.button() == Qt.LeftButton:
            self.item_clicked.emit(self.slot_index, self.item_name)
            
    def enterEvent(self, event):
        """Fare giriş olayı"""
        self.is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        """Fare çıkış olayı"""
        self.is_hovered = False
        self.update()
        
    def paintEvent(self, event):
        """Özel çizim - Minecraft tarzında slot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # Pixel art için
        
        w, h = self.width(), self.height()
        
        # Slot arka planı
        if self.is_selected:
            bg_color = self.selected_color
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.bg_color
            
        painter.fillRect(0, 0, w, h, bg_color)
        
        # Slot kenarlığı (Minecraft tarzında)
        painter.setPen(QPen(self.border_color, 2))
        painter.drawRect(1, 1, w-2, h-2)
        
        # İç kenarlık (daha açık)
        painter.setPen(QPen(self.border_color.lighter(150), 1))
        painter.drawRect(3, 3, w-6, h-6)
        
        # Item varsa çiz
        if self.item_name:
            # Item ikonu (basit renkli kare)
            item_color = self.get_item_color(self.item_name)
            painter.setBrush(QBrush(item_color))
            painter.setPen(QPen(item_color.darker(150), 1))
            painter.drawRect(6, 6, w-12, h-12)
            
            # Item sayısı
            if self.item_count > 1:
                painter.setPen(QPen(QColor(255, 255, 255), 1))
                painter.setFont(QFont("Courier", 8, QFont.Bold))
                count_text = str(self.item_count)
                painter.drawText(w-12, h-8, count_text)
                
    def get_item_color(self, item_name):
        """Item'a göre renk döndür"""
        colors = {
            "sword": QColor(192, 192, 192),  # Gümüş
            "axe": QColor(139, 69, 19),      # Kahverengi
            "pickaxe": QColor(105, 105, 105), # Gri
            "shovel": QColor(160, 82, 45),   # Kahverengi
            "helmet": QColor(255, 215, 0),   # Altın
            "chestplate": QColor(255, 215, 0), # Altın
            "leggings": QColor(255, 215, 0), # Altın
            "boots": QColor(255, 215, 0),    # Altın
            "apple": QColor(255, 0, 0),      # Kırmızı
            "bread": QColor(210, 180, 140),  # Bej
            "diamond": QColor(185, 242, 255), # Açık mavi
            "emerald": QColor(0, 255, 0),    # Yeşil
            "gold": QColor(255, 215, 0),     # Altın
            "iron": QColor(192, 192, 192),   # Gümüş
            "coal": QColor(64, 64, 64),      # Koyu gri
            "stone": QColor(128, 128, 128),  # Gri
            "wood": QColor(139, 69, 19),     # Kahverengi
            "book": QColor(255, 255, 255),   # Beyaz
            "potion": QColor(255, 0, 255),   # Mor
            "torch": QColor(255, 255, 0),    # Sarı
        }
        return colors.get(item_name.lower(), QColor(128, 128, 128))

class RetroInventory(QWidget):
    """Minecraft tarzında envanter bileşeni"""
    
    item_selected = pyqtSignal(int, str)  # slot_index, item_name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        
        # Envanter ayarları
        self.slots_per_row = 9
        self.hotbar_slots = 9
        self.inventory_rows = 3
        self.total_slots = self.hotbar_slots + (self.inventory_rows * self.slots_per_row)
        
        # Slot'lar
        self.slots = []
        self.selected_slot = -1
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.grid_color = QColor(40, 80, 40, 60)  # Grid çizgileri
        self.text_color = QColor(80, 255, 120)  # Parlak yeşil metin
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.detail_color = QColor(80, 255, 120)  # Detay rengi
        
        self.setup_ui()
        self.setup_demo_items()
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("ENVANTER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-size: 14px;
                font-weight: bold;
                font-family: 'Courier';
                border: 2px solid #50ff78;
                background-color: #081410;
                padding: 6px;
            }
        """)
        layout.addWidget(title)
        
        # Ana envanter alanı
        inventory_frame = QFrame()
        inventory_frame.setStyleSheet("""
            QFrame {
                background-color: #081410;
                border: 2px solid #50ff78;
            }
        """)
        
        inventory_layout = QVBoxLayout(inventory_frame)
        inventory_layout.setContentsMargins(10, 10, 10, 10)
        inventory_layout.setSpacing(5)
        
        # Envanter slot'ları (3 satır)
        for row in range(self.inventory_rows):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)
            
            for col in range(self.slots_per_row):
                slot_index = row * self.slots_per_row + col
                slot = InventorySlot(slot_index, self)
                slot.item_clicked.connect(self.on_slot_clicked)
                self.slots.append(slot)
                row_layout.addWidget(slot)
                
            inventory_layout.addLayout(row_layout)
            
        layout.addWidget(inventory_frame)
        
        # Hotbar (alt kısım)
        hotbar_frame = QFrame()
        hotbar_frame.setStyleSheet("""
            QFrame {
                background-color: #081410;
                border: 2px solid #50ff78;
            }
        """)
        
        hotbar_layout = QHBoxLayout(hotbar_frame)
        hotbar_layout.setContentsMargins(10, 10, 10, 10)
        hotbar_layout.setSpacing(2)
        
        # Hotbar slot'ları
        for i in range(self.hotbar_slots):
            slot_index = self.inventory_rows * self.slots_per_row + i
            slot = InventorySlot(slot_index, self)
            slot.item_clicked.connect(self.on_slot_clicked)
            self.slots.append(slot)
            hotbar_layout.addWidget(slot)
            
        layout.addWidget(hotbar_frame)
        
        # Bilgi paneli
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #081410;
                border: 1px solid #50ff78;
            }
        """)
        
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 5, 10, 5)
        
        self.info_label = QLabel("Envanter: 0/36 slot dolu")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-family: 'Courier';
                font-size: 10px;
            }
        """)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        
    def setup_demo_items(self):
        """Demo item'ları ekle - şimdilik boş"""
        # Envanter boş başlasın
        self.update_info()
        
    def on_slot_clicked(self, slot_index, item_name):
        """Slot tıklandığında"""
        # Önceki seçimi temizle
        if self.selected_slot >= 0 and self.selected_slot < len(self.slots):
            self.slots[self.selected_slot].is_selected = False
            self.slots[self.selected_slot].update()
            
        # Yeni seçimi ayarla
        self.selected_slot = slot_index
        if slot_index < len(self.slots):
            self.slots[slot_index].is_selected = True
            self.slots[slot_index].update()
            
        # Sinyal gönder
        self.item_selected.emit(slot_index, item_name)
        
    def add_item(self, item_name, count=1, slot_index=None):
        """Envantere item ekle"""
        if slot_index is None:
            # Boş slot bul
            for i, slot in enumerate(self.slots):
                if not slot.item_name:
                    slot_index = i
                    break
                    
        if slot_index is not None and slot_index < len(self.slots):
            self.slots[slot_index].set_item(item_name, count)
            self.update_info()
            return True
        return False
        
    def remove_item(self, slot_index):
        """Slot'tan item kaldır"""
        if 0 <= slot_index < len(self.slots):
            self.slots[slot_index].clear_item()
            self.update_info()
            return True
        return False
        
    def get_item_at_slot(self, slot_index):
        """Slot'taki item'ı getir"""
        if 0 <= slot_index < len(self.slots):
            slot = self.slots[slot_index]
            return {
                'name': slot.item_name,
                'count': slot.item_count,
                'slot': slot_index
            }
        return None
        
    def update_info(self):
        """Bilgi panelini güncelle"""
        filled_slots = sum(1 for slot in self.slots if slot.item_name)
        self.info_label.setText(f"Envanter: {filled_slots}/{len(self.slots)} slot dolu")
        
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
        painter.drawLine(margin-8, h//2-40, margin, h//2-40)
        painter.drawLine(margin-8, h//2+40, margin, h//2+40)
        painter.drawLine(w-margin+8, h//2-40, w-margin, h//2+40)
        painter.drawLine(w-margin+8, h//2+40, w-margin, h//2+40)
        
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+24, margin-8, w-margin-24, margin-8)
        painter.drawLine(margin+24, h-margin+8, w-margin-24, h-margin+8)
        
    def cleanup(self):
        """Temizlik"""
        pass 