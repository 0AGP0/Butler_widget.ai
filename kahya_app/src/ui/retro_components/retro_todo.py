from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QPushButton, QLineEdit, QLabel,
                             QCheckBox, QScrollArea, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from datetime import datetime
import os

class RetroNotes(QWidget):
    note_added = pyqtSignal(str)  # Yeni not eklendiğinde
    note_deleted = pyqtSignal(int)  # Not silindiğinde
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes_file = "kahya_notes.txt"
        
        self.setMinimumSize(300, 400)
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.grid_color = QColor(40, 80, 40, 60)  # Grid çizgileri
        self.text_color = QColor(80, 255, 120)  # Parlak yeşil metin
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.detail_color = QColor(80, 255, 120)  # Detay rengi
        
        self.setup_ui()
        self.load_notes()
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_notes)
        self.update_timer.start(5000)  # 5 saniyede bir güncelle
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Başlık
        title_label = QLabel("NOTLAR")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
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
        layout.addWidget(title_label)
        
        # Not listesi
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: #081410;
                border: 2px solid #50ff78;
                color: #50ff78;
                font-family: 'Courier';
                font-size: 10px;
                selection-background-color: #102010;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #102010;
            }
            QListWidget::item:selected {
                background-color: #183018;
            }
        """)
        layout.addWidget(self.notes_list)
        
        # Yeni not ekleme alanı
        input_layout = QHBoxLayout()
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Yeni not ekle...")
        self.note_input.setStyleSheet("""
            QLineEdit {
                background-color: #081410;
                border: 2px solid #50ff78;
                color: #50ff78;
                font-family: 'Courier';
                font-size: 10px;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 2px solid #50ff78;
            }
        """)
        self.note_input.returnPressed.connect(self.add_note)
        input_layout.addWidget(self.note_input)
        
        add_button = QPushButton("+")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #081410;
                border: 2px solid #50ff78;
                color: #50ff78;
                font-family: 'Courier';
                font-size: 14px;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 32px;
            }
            QPushButton:hover {
                background-color: #102010;
                border: 2px solid #50ff78;
            }
            QPushButton:pressed {
                background-color: #183018;
            }
        """)
        add_button.clicked.connect(self.add_note)
        input_layout.addWidget(add_button)
        
        layout.addLayout(input_layout)
        
        # İstatistik
        self.stats_label = QLabel("Toplam: 0 not")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-family: 'Courier';
                font-size: 9px;
                border: 1px solid #50ff78;
                background-color: #081410;
                padding: 4px;
            }
        """)
        layout.addWidget(self.stats_label)
        
    def add_note(self):
        """Yeni not ekle"""
        text = self.note_input.text().strip()
        if text:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            note_line = f"{timestamp}: {text}\n"
            
            try:
                with open(self.notes_file, "a", encoding="utf-8") as f:
                    f.write(note_line)
                self.note_input.clear()
                self.load_notes()
                self.note_added.emit(text)
            except Exception as e:
                print(f"Not ekleme hatası: {e}")
            
    def load_notes(self):
        """Notları yükle"""
        self.notes_list.clear()
        
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = f.readlines()
                
                # Son 20 notu göster (en yeniden en eskiye)
                recent_notes = notes[-20:]
                for i, note in enumerate(reversed(recent_notes)):
                    # Doğru index: en yeni notun index'i len(notes)-1, sonra len(notes)-2, ...
                    original_index = len(notes) - i - 1
                    item = NoteItem(note.strip(), original_index, self.notes_list)
                    item.notes_widget = self
                    list_item = QListWidgetItem()
                    self.notes_list.addItem(list_item)
                    self.notes_list.setItemWidget(list_item, item)
                    list_item.setSizeHint(item.sizeHint())
                
                # İstatistikleri güncelle
                self.stats_label.setText(f"Toplam: {len(notes)} not")
            else:
                self.stats_label.setText("Toplam: 0 not")
                
        except Exception as e:
            print(f"Not yükleme hatası: {e}")
            self.stats_label.setText("Hata: Notlar yüklenemedi")
        
    def delete_note(self, note_index):
        """Notu sil"""
        print(f"delete_note çağrıldı: index={note_index}")
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    notes = f.readlines()
                
                print(f"Toplam not sayısı: {len(notes)}")
                if 0 <= note_index < len(notes):
                    print(f"Silinecek not: {notes[note_index]}")
                    notes.pop(note_index)
                    
                    with open(self.notes_file, "w", encoding="utf-8") as f:
                        f.writelines(notes)
                    
                    print("Not silindi, liste yenileniyor...")
                    # UI güncellemesini ana thread'de yap
                    self.note_deleted.emit(note_index)
                    # Ana thread'de güncelle
                    self.parent().parent().parent().load_notes()
                else:
                    print(f"Geçersiz index: {note_index}")
        except Exception as e:
            print(f"Not silme hatası: {e}")
            
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
        painter.drawLine(w-margin+8, h//2-40, w-margin, h//2-40)
        painter.drawLine(w-margin+8, h//2+40, w-margin, h//2+40)
        
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+24, margin-8, w-margin-24, margin-8)
        painter.drawLine(margin+24, h-margin+8, w-margin-24, h-margin+8)
        
    def cleanup(self):
        """Temizlik"""
        self.update_timer.stop()

class NoteItem(QFrame):
    def __init__(self, note_text, note_index, parent=None):
        super().__init__(parent)
        self.note_text = note_text
        self.note_index = note_index
        self.notes_widget = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Not metni
        note_label = QLabel(self.note_text)
        note_label.setWordWrap(True)
        note_label.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-family: 'Courier';
                font-size: 10px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(note_label)
        
        # Silme butonu
        delete_button = QPushButton("×")
        delete_button.setFixedSize(20, 20)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #081410;
                border: 1px solid #50ff78;
                color: #50ff78;
                font-family: 'Courier';
                font-size: 12px;
                font-weight: bold;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                border: 1px solid #ff4444;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #cc3333;
            }
        """)
        delete_button.clicked.connect(self.delete_note)
        layout.addWidget(delete_button)
        
    def delete_note(self):
        """Notu sil"""
        if self.notes_widget:
            self.notes_widget.delete_note(self.note_index)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)  # Pixel art için
        
        # Widget boyutları
        w, h = self.width(), self.height()
        
        # Arka plan (şeffaf)
        painter.fillRect(0, 0, w, h, QColor(8, 20, 10, 100))
        
        # Alt çizgi
        painter.setPen(QPen(QColor(80, 255, 120, 50), 1))
        painter.drawLine(0, h-1, w, h-1) 