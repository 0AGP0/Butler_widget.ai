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
        
        # Güncelleme zamanlayıcısı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_calendar)
        self.update_timer.start(60000)  # Her dakika güncelle
        
        self.setup_ui()
        self.update_calendar()
        
    def setup_ui(self):
        """UI'yi kur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Courier';
                border: 2px solid #00ff00;
                background-color: #000000;
                padding: 5px;
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
                    color: #00ff00;
                    font-family: 'Courier';
                    font-size: 12px;
                    font-weight: bold;
                    background-color: #001100;
                    border: 1px solid #00ff00;
                    padding: 3px;
                }
            """)
            days_layout.addWidget(day_label)
            
        layout.addLayout(days_layout)
        
        # Takvim ızgarası
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(2)
        layout.addLayout(self.calendar_grid)
        
        # Alt bilgi
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-family: 'Courier';
                font-size: 10px;
                border: 1px solid #00ff00;
                background-color: #000000;
                padding: 3px;
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
        day_label.setMinimumSize(35, 25)
        
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
                        font-size: 12px;
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
                        font-size: 12px;
                        font-weight: bold;
                        background-color: #00ff00;
                        border: 1px solid #00ff00;
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
                        font-size: 12px;
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
                        color: #00ff00;
                        font-family: 'Courier';
                        font-size: 12px;
                        background-color: #000000;
                        border: 1px solid #003300;
                        padding: 3px;
                    }
                    QLabel:hover {
                        background-color: #001100;
                        border: 1px solid #00ff00;
                    }
                """)
        
        # Tooltip ekle
        if has_reminder:
            reminder_text = self.get_reminders_for_date(day, current_month, current_year)
            day_label.setToolTip(f"📅 Hatırlatıcılar:\n{reminder_text}")
            
        return day_label
        
    def paintEvent(self, event):
        """Özel çizim"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Ana kenarlık
        painter.setPen(QPen(QColor(0, 200, 0), 2))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # İç kenarlık
        painter.setPen(QPen(QColor(0, 100, 0), 1))
        painter.drawRect(self.rect().adjusted(2, 2, -3, -3))
        
        # Köşe dekorasyonları
        self.draw_corners(painter)
        
    def draw_corners(self, painter):
        """Köşe dekorasyonlarını çiz"""
        width = self.width()
        height = self.height()
        corner_size = 10
        
        painter.setPen(QPen(QColor(0, 200, 0), 2))
        
        # Sol üst köşe
        painter.drawLine(5, 5, corner_size, 5)
        painter.drawLine(5, 5, 5, corner_size)
        
        # Sağ üst köşe
        painter.drawLine(width - corner_size, 5, width - 5, 5)
        painter.drawLine(width - 5, 5, width - 5, corner_size)
        
        # Sol alt köşe
        painter.drawLine(5, height - corner_size, 5, height - 5)
        painter.drawLine(5, height - 5, corner_size, height - 5)
        
        # Sağ alt köşe
        painter.drawLine(width - corner_size, height - 5, width - 5, height - 5)
        painter.drawLine(width - 5, height - corner_size, width - 5, height - 5)
        
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
        print(f"Takvim güncelleniyor...")
        if self.reminder_manager:
            self.reminders = self.reminder_manager.get_reminders()
            print(f"Takvim: {len(self.reminders)} hatırlatıcı bulundu")
            for r in self.reminders:
                print(f"Takvimde: {r[1]} - {r[3]}")
        self.update_calendar()
    
    def has_reminder_on_date(self, day, month, year):
        """Belirli bir tarihte hatırlatıcı var mı kontrol et"""
        if not self.reminders:
            return False
        
        target_date = date(year, month, day)
        
        for reminder in self.reminders:
            try:
                reminder_date = datetime.fromisoformat(reminder[3]).date()
                if reminder_date == target_date:
                    return True
            except:
                continue
        return False
    
    def get_reminders_for_date(self, day, month, year):
        """Belirli bir tarihteki hatırlatıcıları getir"""
        if not self.reminders:
            return ""
        
        target_date = date(year, month, day)
        reminders_text = []
        
        for reminder in self.reminders:
            try:
                reminder_date = datetime.fromisoformat(reminder[3]).date()
                if reminder_date == target_date:
                    time_str = datetime.fromisoformat(reminder[3]).strftime("%H:%M")
                    reminders_text.append(f"• {time_str} - {reminder[1]}")
            except:
                continue
        
        return "\n".join(reminders_text)
        
    def cleanup(self):
        """Temizlik"""
        self.update_timer.stop() 