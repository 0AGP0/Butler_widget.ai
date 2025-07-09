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
        self.setup_ui()
        self.load_notes()
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.load_notes)
        self.update_timer.start(5000)  # 5 saniyede bir güncelle
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title_label = QLabel("NOTLAR")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 18px;
                font-weight: bold;
                font-family: 'Courier';
                border: 2px solid #00ff00;
                background-color: #000000;
                padding: 5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Not listesi
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: #000000;
                border: 2px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier';
                font-size: 12px;
                selection-background-color: #003300;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #003300;
            }
            QListWidget::item:selected {
                background-color: #004400;
            }
        """)
        layout.addWidget(self.notes_list)
        
        # Yeni not ekleme alanı
        input_layout = QHBoxLayout()
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Yeni not ekle...")
        self.note_input.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                border: 2px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier';
                font-size: 12px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
            }
        """)
        self.note_input.returnPressed.connect(self.add_note)
        input_layout.addWidget(self.note_input)
        
        add_button = QPushButton("+")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: 2px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier';
                font-size: 16px;
                font-weight: bold;
                padding: 5px 10px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #003300;
                border: 2px solid #00ff88;
            }
            QPushButton:pressed {
                background-color: #004400;
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
                color: #00ff00;
                font-family: 'Courier';
                font-size: 10px;
                border: 1px solid #00ff00;
                background-color: #000000;
                padding: 3px;
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
        
    def cleanup(self):
        """Temizlik"""
        self.update_timer.stop()


class NoteItem(QFrame):
    def __init__(self, note_text, note_index, parent=None):
        super().__init__(parent)
        self.note_text = note_text
        self.note_index = note_index
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Not metni
        self.note_label = QLabel(self.note_text)
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
                font-size: 11px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.note_label, 1)
        
        # Silme butonu
        delete_button = QPushButton("×")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                border: 1px solid #ff0000;
                color: #ff0000;
                font-family: 'Courier';
                font-size: 14px;
                font-weight: bold;
                padding: 2px 6px;
                min-width: 20px;
                max-width: 20px;
            }
            QPushButton:hover {
                background-color: #330000;
                border: 1px solid #ff4444;
            }
            QPushButton:pressed {
                background-color: #440000;
            }
        """)
        delete_button.clicked.connect(self.delete_note)
        layout.addWidget(delete_button)
        
    def delete_note(self):
        """Notu sil"""
        # Doğrudan RetroNotes referansını kullan
        if hasattr(self, 'notes_widget') and self.notes_widget:
            print(f"Not silme çağrıldı: index={self.note_index}")
            self.notes_widget.delete_note(self.note_index)
        else:
            print("notes_widget referansı bulunamadı!")
        
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Alt kenarlık
        painter.setPen(QPen(QColor(0, 100, 0), 1))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1) 