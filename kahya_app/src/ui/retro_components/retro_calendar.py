from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QToolTip
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from datetime import datetime, date
import calendar

class RetroCalendar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 250)
        
        # Şu anki tarih
        self.current_date = datetime.now()
        self.selected_date = self.current_date.date()
        
        # Hatırlatıcılar
        self.reminders = []
        self.reminder_manager = None
        
        # Renkler - pixel art teması
        self.bg_color = QColor(8, 20, 10)  # Koyu yeşil arka plan
        self.grid_color = QColor(40, 80, 40, 60)  # Grid çizgileri
        self.text_color = QColor(80, 255, 120)  # Parlak yeşil metin
        self.border_color = QColor(80, 255, 120)  # Yeşil kenarlık
        self.detail_color = QColor(80, 255, 120)  # Detay rengi
        self.today_color = QColor(80, 255, 120)  # Bugün rengi
        self.reminder_color = QColor(255, 136, 0)  # Hatırlatıcı rengi
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_calendar)
        self.update_timer.start(60000)  # Her dakika güncelle
        
        self.setup_ui()
        self.update_calendar()
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Başlık
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
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
        layout.addWidget(self.title_label)
        
        # Gün başlıkları
        days_layout = QHBoxLayout()
        days = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        
        for day in days:
            day_label = QLabel(day)
            day_label.setAlignment(Qt.AlignCenter)
            day_label.setStyleSheet("""
                QLabel {
                    color: #50ff78;
                    font-family: 'Courier';
                    font-size: 10px;
                    font-weight: bold;
                    background-color: #102010;
                    border: 1px solid #50ff78;
                    padding: 4px;
                }
            """)
            days_layout.addWidget(day_label)
            
        layout.addLayout(days_layout)
        
        # Takvim ızgarası
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(3)
        layout.addLayout(self.calendar_grid)
        
        # Alt bilgi
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #50ff78;
                font-family: 'Courier';
                font-size: 9px;
                border: 1px solid #50ff78;
                background-color: #081410;
                padding: 4px;
            }
        """)
        layout.addWidget(self.info_label)
        
    def update_calendar(self):
        """Takvimi güncelle"""
        # Başlığı güncelle
        month_name = self.current_date.strftime("%B %Y")
        self.title_label.setText(month_name.upper())
        
        # Takvim ızgarasını temizle
        for i in reversed(range(self.calendar_grid.count())):
            item = self.calendar_grid.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            self.calendar_grid.removeItem(item)
                
        # Takvim verilerini al
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Günleri yerleştir
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_widget = self.create_day_widget(day)
                    self.calendar_grid.addWidget(day_widget, week_num, day_num)
                    
        # Alt bilgiyi güncelle
        today = date.today()
        day_of_year = today.timetuple().tm_yday
        week_of_year = today.isocalendar()[1]
        
        info_text = f"Bugün: {today.strftime('%d.%m.%Y')} | Yılın {day_of_year}. günü | {week_of_year}. hafta"
        self.info_label.setText(info_text)
        
    def create_day_widget(self, day):
        """Gün widget'ı oluştur"""
        day_label = QLabel(str(day))
        day_label.setAlignment(Qt.AlignCenter)
        day_label.setMinimumSize(32, 22)
        
        # Bugün mü kontrol et
        today = date.today()
        current_month = self.current_date.month
        current_year = self.current_date.year
        
        # Bu günde hatırlatıcı var mı kontrol et
        has_reminder = self.has_reminder_on_date(day, current_month, current_year)
        
        if (day == today.day and current_month == today.month and current_year == today.year):
            # Bugün
            if has_reminder:
                day_label.setStyleSheet("""
                    QLabel {
                        color: #000000;
                        font-family: 'Courier';
                        font-size: 10px;
                        font-weight: bold;
                        background-color: #ff8800;
                        border: 1px solid #ff8800;
                        padding: 3px;
                    }
                """)
            else:
                day_label.setStyleSheet("""
                    QLabel {
                        color: #000000;
                        font-family: 'Courier';
                        font-size: 10px;
                        font-weight: bold;
                        background-color: #50ff78;
                        border: 1px solid #50ff78;
                        padding: 3px;
                    }
                """)
        else:
            # Normal gün
            if has_reminder:
                day_label.setStyleSheet("""
                    QLabel {
                        color: #000000;
                        font-family: 'Courier';
                        font-size: 10px;
                        font-weight: bold;
                        background-color: #ff6600;
                        border: 1px solid #ff6600;
                        padding: 3px;
                    }
                    QLabel:hover {
                        background-color: #ff8800;
                        border: 1px solid #ff8800;
                    }
                """)
            else:
                day_label.setStyleSheet("""
                    QLabel {
                        color: #50ff78;
                        font-family: 'Courier';
                        font-size: 10px;
                        background-color: #081410;
                        border: 1px solid #102010;
                        padding: 3px;
                    }
                    QLabel:hover {
                        background-color: #102010;
                        border: 1px solid #50ff78;
                    }
                """)
        
        # Tooltip ekle
        if has_reminder:
            reminder_text = self.get_reminders_for_date(day, current_month, current_year)
            day_label.setToolTip(reminder_text)
        
        return day_label
        
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
        painter.drawLine(margin-8, h//2-30, margin, h//2-30)
        painter.drawLine(margin-8, h//2+30, margin, h//2+30)
        painter.drawLine(w-margin+8, h//2-30, w-margin, h//2-30)
        painter.drawLine(w-margin+8, h//2+30, w-margin, h//2+30)
        
        # Üst ve alt detay çizgiler
        painter.drawLine(margin+24, margin-8, w-margin-24, margin-8)
        painter.drawLine(margin+24, h-margin+8, w-margin-24, h-margin+8)
        
        # Köşe dekorasyonları
        self.draw_corners(painter)
        
    def draw_corners(self, painter):
        """Köşe dekorasyonlarını çiz"""
        w, h = self.width(), self.height()
        corner_size = 12
        corner_color = self.detail_color
        
        painter.setPen(QPen(corner_color, 3))
        
        # Sol üst köşe
        painter.drawLine(4, 4, corner_size, 4)
        painter.drawLine(4, 4, 4, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(w - corner_size, 4, w - 4, 4)
        painter.drawLine(w - 4, 4, w - 4, corner_size)
        
        # Sol alt köşe
        painter.drawLine(4, h - corner_size, 4, h - 4)
        painter.drawLine(4, h - 4, corner_size, h - 4)
        
        # Sağ alt köşe
        painter.drawLine(w - corner_size, h - 4, w - 4, h - 4)
        painter.drawLine(w - 4, h - corner_size, w - 4, h - 4)
        
    def resizeEvent(self, event):
        """Widget yeniden boyutlandırıldığında"""
        super().resizeEvent(event)
        self.update()
        
    def set_reminder_manager(self, reminder_manager):
        """Hatırlatıcı yöneticisini ayarla"""
        self.reminder_manager = reminder_manager
        self.update_reminders()
        
    def update_reminders(self):
        """Hatırlatıcıları güncelle"""
        if self.reminder_manager:
            self.reminders = self.reminder_manager.get_all_reminders()
            self.update_calendar()
            
    def has_reminder_on_date(self, day, month, year):
        """Belirli bir tarihte hatırlatıcı var mı kontrol et"""
        if not self.reminder_manager:
            return False
            
        target_date = date(year, month, day)
        for reminder in self.reminders:
            if reminder['date'] == target_date:
                return True
        return False
        
    def get_reminders_for_date(self, day, month, year):
        """Belirli bir tarihteki hatırlatıcıları al"""
        if not self.reminder_manager:
            return ""
            
        target_date = date(year, month, day)
        reminders = []
        for reminder in self.reminders:
            if reminder['date'] == target_date:
                reminders.append(reminder['title'])
        
        if reminders:
            return f"Hatırlatıcılar:\n" + "\n".join(reminders)
        return ""
        
    def cleanup(self):
        """Temizlik"""
        self.update_timer.stop() 