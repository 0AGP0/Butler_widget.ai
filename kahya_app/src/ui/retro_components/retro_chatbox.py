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
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.grid_color = QColor(40, 80, 40, 60)  # Grid çizgileri
        self.text_color = QColor(80, 255, 120)  # Parlak yeşil metin
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.detail_color = QColor(80, 255, 120)  # Detay rengi
        
        self.setup_ui()
        self.setup_styling()
        
    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Başlık
        title = QLabel("KAHYA AI CHAT")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #50ff78;
                padding: 6px;
                background-color: #081410;
                font-family: 'Courier';
            }
        """)
        layout.addWidget(title)
        
        # Chat alanı
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setMaximumHeight(120)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #081410;
                color: #50ff78;
                border: 2px solid #50ff78;
                font-family: 'Courier';
                font-size: 10px;
                padding: 6px;
            }
        """)
        layout.addWidget(self.chat_area)
        
        # Giriş alanı
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Mesajınızı yazın...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #081410;
                color: #50ff78;
                border: 2px solid #50ff78;
                padding: 6px;
                font-family: 'Courier';
                font-size: 10px;
            }
            QLineEdit:focus {
                border: 2px solid #50ff78;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("GÖNDER")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #102010;
                color: #50ff78;
                border: 2px solid #50ff78;
                padding: 6px 12px;
                font-weight: bold;
                font-family: 'Courier';
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #183018;
                border: 2px solid #50ff78;
            }
            QPushButton:pressed {
                background-color: #081410;
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
                background-color: #081410;
                color: #50ff78;
                font-family: 'Courier';
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
        if any(keyword in message_lower for keyword in ['hatırlat', 'hatırlatıcı', 'reminder']):
            return f"reminder: {message}"
            
        # Not komutları
        if any(keyword in message_lower for keyword in ['not al', 'not ekle', 'kaydet', 'save']):
            return f"note: {message}"
            
        # Todo komutları
        if any(keyword in message_lower for keyword in ['todo', 'yapılacak', 'görev', 'task']):
            return f"todo: {message}"
            
        # Dosya işlemleri
        if any(keyword in message_lower for keyword in ['dosya aç', 'file open', 'klasör aç']):
            return f"file: {message}"
            
        # Web arama
        if any(keyword in message_lower for keyword in ['ara', 'search', 'google']):
            return f"search: {message}"
            
        return None
        
    def start_typing_animation(self):
        """Yazma animasyonunu başlat"""
        self.is_typing = True
        self.typing_dots = 0
        self.typing_timer.start(500)  # 500ms
        self.kahya_talking.emit(True)
        
        # Yazma mesajını ekle
        self.typing_message_id = f"typing_{int(time.time())}"
        self.add_system_message("Kahya yazıyor...")
        
    def update_typing_animation(self):
        """Yazma animasyonunu güncelle"""
        self.typing_dots += 1
        if self.typing_dots > 3:
            self.typing_dots = 0
            
        # Yazma mesajını güncelle
        dots = "." * self.typing_dots
        self.add_system_message(f"Kahya yazıyor{dots}")
        
    def handle_llm_response(self, response):
        """LLM yanıtını işle"""
        if not self.response_received:
            self.response_received = True
            self.is_typing = False
            self.typing_timer.stop()
            self.kahya_talking.emit(False)
            
            # Yazma mesajını kaldır ve yanıtı ekle
            self.add_kahya_message(response)
            
    def handle_llm_error(self, error):
        """LLM hatasını işle"""
        self.is_typing = False
        self.typing_timer.stop()
        self.kahya_talking.emit(False)
        self.add_system_message(f"Hata: {error}")
        
    def handle_llm_command(self, response):
        """LLM komut yanıtını işle"""
        if not self.response_received:
            self.response_received = True
            self.is_typing = False
            self.typing_timer.stop()
            self.kahya_talking.emit(False)
            
            # Yazma mesajını kaldır ve yanıtı ekle
            self.add_kahya_message(response)
            
    def add_user_message(self, message):
        """Kullanıcı mesajını ekle"""
        self.chat_area.append(f"<span style='color: #50ff78;'><b>Siz:</b> {message}</span>")
        self.scroll_to_bottom()
        
    def add_kahya_message(self, message):
        """Kahya mesajını ekle"""
        self.chat_area.append(f"<span style='color: #50ff78;'><b>Kahya:</b> {message}</span>")
        self.scroll_to_bottom()
        
    def add_system_message(self, message):
        """Sistem mesajını ekle"""
        self.chat_area.append(f"<span style='color: #50ff78; font-style: italic;'>{message}</span>")
        self.scroll_to_bottom()
        
    def add_response(self, response):
        """Yanıt ekle (router'dan gelen)"""
        if not self.response_received:
            self.response_received = True
            self.is_typing = False
            self.typing_timer.stop()
            self.kahya_talking.emit(False)
            
            # Yazma mesajını kaldır ve yanıtı ekle
            self.add_kahya_message(response)
            
    def scroll_to_bottom(self):
        """Chat alanını en alta kaydır"""
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)
        
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
        painter.drawLine(margin-8, h//2-25, margin, h//2-25)
        painter.drawLine(margin-8, h//2+25, margin, h//2+25)
        painter.drawLine(w-margin+8, h//2-25, w-margin, h//2-25)
        painter.drawLine(w-margin+8, h//2+25, w-margin, h//2+25)
        
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+24, margin-8, w-margin-24, margin-8)
        painter.drawLine(margin+24, h-margin+8, w-margin-24, h-margin+8)
        
    def cleanup(self):
        """Temizlik"""
        self.typing_timer.stop() 