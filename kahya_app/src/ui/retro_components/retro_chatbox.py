import threading
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor, QPainter, QPen, QBrush

class LLMWorker(QThread):
    """LLM yanıtlarını arka planda işleyen thread"""
    response_ready = pyqtSignal(str)
    command_detected = pyqtSignal(str)  # Komut algılandı sinyali
    error_occurred = pyqtSignal(str)
    
    def __init__(self, llm_client, message, router=None):
        super().__init__()
        self.llm_client = llm_client
        self.message = message
        self.router = router
        
    def run(self):
        try:
            # LLM'den yanıt al
            response = self.llm_client.get_response(self.message)
            
            # LLM yanıtında komut işaretleri var mı kontrol et
            if any(keyword in response.lower() for keyword in [
                'hatırlatıcı eklendi', 'not kaydedildi', 'todo eklendi', 
                'hatırlatıcılar', 'notlar', 'yapılacaklar', 'unutmayalım'
            ]):
                # LLM komut işlemi yapmış, router'a gönder
                if self.router:
                    # Orijinal mesajı router'a gönder
                    self.command_detected.emit(self.message)
                else:
                    self.response_ready.emit(response)
            else:
                # Normal yanıt
                self.response_ready.emit(response)
                
        except Exception as e:
            self.error_occurred.emit(str(e))

class RetroChatbox(QWidget):
    command_sent = pyqtSignal(str)
    kahya_talking = pyqtSignal(bool)  # Kahya konuşma durumu sinyali
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.router = None
        self.llm_client = None
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.update_typing_animation)
        self.typing_dots = 0
        self.is_typing = False
        self.typing_message_id = None
        self.response_received = False  # Çift mesajı engellemek için
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("KAHYA AI CHAT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #00ff00;
                padding: 5px;
                background-color: #001100;
            }
        """)
        layout.addWidget(title)
        
        # Chat alanı
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setMaximumHeight(150)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #001100;
                color: #00ff00;
                border: 2px solid #00ff00;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Giriş alanı
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Mesajınızı yazın...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #001100;
                color: #00ff00;
                border: 2px solid #00ff00;
                padding: 5px;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #00ff88;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("GÖNDER")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #003300;
                color: #00ff00;
                border: 2px solid #00ff00;
                padding: 5px 10px;
                font-weight: bold;
                font-family: 'Courier New';
            }
            QPushButton:hover {
                background-color: #004400;
                border: 2px solid #00ff88;
            }
            QPushButton:pressed {
                background-color: #002200;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Başlangıç mesajı
        self.add_system_message("Kahya AI Asistan'a hoş geldiniz! Size nasıl yardımcı olabilirim?")
        
    def setup_styling(self):
        """Genel stil ayarları"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000800;
                color: #00ff00;
                font-family: 'Courier New';
            }
        """)
        
    def set_router(self, router):
        """Komut yönlendiriciyi ayarla"""
        self.router = router
        
    def set_llm_client(self, llm_client):
        """LLM istemcisini ayarla"""
        self.llm_client = llm_client
        
    def send_message(self):
        """Mesaj gönder"""
        message = self.input_field.text().strip()
        if not message:
            return
            
        # Kullanıcı mesajını ekle
        self.add_user_message(message)
        self.input_field.clear()
        
        # Yanıt durumunu sıfırla
        self.response_received = False
        
        # Önce doğal dil işleme ile komut algılama
        detected_command = self._detect_command(message)
        
        if detected_command:
            # Komut algılandı, router'a gönder
            print(f"Chatbox: Komut algılandı: '{detected_command}'")
            if self.router:
                self.command_sent.emit(detected_command)
        else:
            # Komut algılanmadı, LLM'e gönder
            if self.llm_client:
                self.start_typing_animation()
                # LLM'i daha akıllı kullan
                self.worker = LLMWorker(self.llm_client, message, self.router)
                self.worker.response_ready.connect(self.handle_llm_response)
                self.worker.command_detected.connect(self.handle_llm_command)
                self.worker.error_occurred.connect(self.handle_llm_error)
                self.worker.start()
            else:
                self.add_system_message("LLM istemcisi bulunamadı.")
    
    def _detect_command(self, message):
        """Doğal dil işleme ile komut algılama"""
        message_lower = message.lower()
        
        # Hatırlatıcı komutları
        reminder_keywords = [
            'hatırlat', 'hatırlatma', 'hatırlatıcı', 'reminder', 'unutma',
            'aklında tut', 'not al', 'not et', 'kaydet', 'sakla'
        ]
        
        # Not alma komutları
        note_keywords = [
            'not al', 'not et', 'kaydet', 'yaz', 'not defteri', 'not tut'
        ]
        
        # Tarih/saat içeren mesajlar
        import re
        date_patterns = [
            r'\d{1,2}\s*(?:ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)',
            r'\d{1,2}\s*/\s*\d{1,2}',
            r'\d{1,2}\s*\.\s*\d{1,2}',
            r'bugün', 'yarın', 'yarın sabah', 'yarın akşam',
            r'bu akşam', 'bu sabah', 'bu gece',
            r'haftaya', 'gelecek hafta', 'bu hafta',
            r'ayın \d{1,2}', r'bu ayın \d{1,2}', r'gelecek ayın \d{1,2}',
            r'\d{1,2}\s+sinde', r'\d{1,2}\s+sında',  # "20 sinde", "15 sında" gibi
            r'\d{1,2}\s+günü', r'\d{1,2}\s+gün',  # "20 günü", "15 gün" gibi
            r'pazartesi', r'salı', r'çarşamba', r'perşembe', r'cuma', r'cumartesi', r'pazar'  # Günler
        ]
        
        # Hatırlatıcı silme komutları (ÖNCE KONTROL ET!)
        if any(keyword in message_lower for keyword in ['sil', 'kaldır', 'iptal']):
            # Tarih var mı kontrol et
            has_date = any(re.search(pattern, message_lower) for pattern in date_patterns)
            if has_date:
                return message  # Doğrudan router'a gönder
        
        # Hatırlatıcı komutu algıla
        if any(keyword in message_lower for keyword in reminder_keywords):
            # Tarih var mı kontrol et
            has_date = any(re.search(pattern, message_lower) for pattern in date_patterns)
            if has_date:
                return f"hatırlatıcı_ekle {message}"
        
        # Tarih içeren mesajlar (hatırlatıcı olabilir)
        has_date = any(re.search(pattern, message_lower) for pattern in date_patterns)
        if has_date:
            # Tarih var ama hatırlat kelimesi yok, yine de hatırlatıcı olabilir
            return f"hatırlatıcı_ekle {message}"
        
        # Not alma komutu algıla
        if any(keyword in message_lower for keyword in note_keywords):
            return f"not_al {message}"
        
        # Todo komutları
        if 'yapılacak' in message_lower or 'todo' in message_lower or 'görev' in message_lower:
            return f"todo_ekle {message}"
        
        # Hatırlatıcıları listele
        if 'hatırlatıcılarım' in message_lower or 'hatırlatıcılar' in message_lower:
            return "hatırlatıcılar"
        
        # Notları listele
        if 'notlarım' in message_lower or 'notlar' in message_lower:
            return "notlar"
        
        return None
    

            
    def start_typing_animation(self):
        """Yazma animasyonunu başlat"""
        self.is_typing = True
        self.typing_dots = 0
        self.typing_timer.start(500)
        
        # Tek bir "yazıyor" mesajı ekle
        timestamp = time.strftime("[%H:%M:%S]")
        self.typing_message_id = f"{timestamp} Sistem: Kahya yazıyor"
        self.chat_area.append(self.typing_message_id)
        self.scroll_to_bottom()
        
    def update_typing_animation(self):
        """Yazma animasyonunu güncelle"""
        if not self.is_typing:
            return
            
        self.typing_dots = (self.typing_dots + 1) % 4
        dots = "." * self.typing_dots
        
        # Mevcut scroll pozisyonunu kaydet
        scrollbar = self.chat_area.verticalScrollBar()
        was_at_bottom = scrollbar.value() == scrollbar.maximum()
        
        # Son satırı güncelle (yazıyor mesajını)
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        
        # Yeni dots ile güncelle
        timestamp = time.strftime("[%H:%M:%S]")
        new_typing_message = f"{timestamp} Sistem: Kahya yazıyor{dots}"
        cursor.insertText(new_typing_message)
        
        # Eğer en alttaysa, scroll pozisyonunu koru
        if was_at_bottom:
            self.scroll_to_bottom()
        
    def handle_llm_response(self, response):
        """LLM yanıtını işle"""
        self.typing_timer.stop()
        self.is_typing = False
        self.response_received = True
        
        # Son "yazıyor" mesajını kaldır
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Satır sonu karakterini kaldır
        
        # Yanıtı ekle
        self.add_kahya_message(response)
        
    def handle_llm_error(self, error):
        """LLM hatasını işle"""
        self.typing_timer.stop()
        self.is_typing = False
        self.response_received = True
        
        # Son "yazıyor" mesajını kaldır
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        
        self.add_system_message(f"Hata: {error}")
    
    def handle_llm_command(self, response):
        """LLM komut yanıtını işle"""
        self.typing_timer.stop()
        self.is_typing = False
        self.response_received = True
        
        # Son "yazıyor" mesajını kaldır
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        
        # LLM komut işlemi yapmış, yanıtı göster
        self.add_kahya_message(response)
        
    def add_user_message(self, message):
        """Kullanıcı mesajını ekle"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.chat_area.append(f"{timestamp} Siz: {message}")
        self.scroll_to_bottom()
        
    def add_kahya_message(self, message):
        """Kahya mesajını ekle"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.chat_area.append(f"{timestamp} Kahya: {message}")
        self.scroll_to_bottom()
        
        # Kahya konuşmaya başladı sinyali gönder
        self.kahya_talking.emit(True)
        
        # 3 saniye sonra konuşmayı durdur
        QTimer.singleShot(3000, lambda: self.kahya_talking.emit(False))
        
    def add_system_message(self, message):
        """Sistem mesajını ekle"""
        timestamp = time.strftime("[%H:%M:%S]")
        self.chat_area.append(f"{timestamp} Sistem: {message}")
        self.scroll_to_bottom()
        
    def add_response(self, response):
        """Dışarıdan yanıt ekle (router'dan)"""
        print(f"Chatbox: Router yanıtı alındı: {response}")
        
        # Router yanıtı geldiğinde LLM'e gitmeyi engelle
        self.response_received = True
        
        if self.is_typing:
            # Yazma animasyonu varsa, onu durdur ve yanıtı ekle
            self.typing_timer.stop()
            self.is_typing = False
            
            # Son "yazıyor" mesajını kaldır
            cursor = self.chat_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()
            
        self.add_kahya_message(response)
        
    def scroll_to_bottom(self):
        """Chat alanını en alta kaydır"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Kenarlık çiz
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # Köşe dekorasyonları
        corner_size = 8
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        
        # Sol üst köşe
        painter.drawLine(5, 5, corner_size, 5)
        painter.drawLine(5, 5, 5, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(self.width() - corner_size, 5, self.width() - 5, 5)
        painter.drawLine(self.width() - 5, 5, self.width() - 5, corner_size)
        
        # Sol alt köşe
        painter.drawLine(5, self.height() - corner_size, 5, self.height() - 5)
        painter.drawLine(5, self.height() - 5, corner_size, self.height() - 5)
        
        # Sağ alt köşe
        painter.drawLine(self.width() - corner_size, self.height() - 5, self.width() - 5, self.height() - 5)
        painter.drawLine(self.width() - 5, self.height() - corner_size, self.width() - 5, self.height() - 5)
        
    def cleanup(self):
        """Temizlik"""
        self.typing_timer.stop()
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait() 