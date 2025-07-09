from datetime import datetime, timedelta
from src.core.database import Database

class ReminderManager:
    def __init__(self, db_path):
        self.db = Database(db_path)
        
    def add_reminder(self, title, message, hour, minute, date=None):
        """Hatırlatıcı ekle"""
        try:
            if date is None:
                date = datetime.now().date()
                
            reminder_time = datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))
            
            # Eğer zaman geçmişse, yarına ayarla
            if reminder_time < datetime.now():
                reminder_time += timedelta(days=1)
                
            self.db.add_reminder(title, message, reminder_time)
            return True
        except Exception as e:
            print(f"Hatırlatıcı ekleme hatası: {e}")
            return False
            
    def get_reminders(self, triggered=None):
        """Hatırlatıcıları getir"""
        try:
            return self.db.get_reminders(triggered)
        except Exception as e:
            print(f"Hatırlatıcı getirme hatası: {e}")
            return []
            
    def get_active_reminders(self):
        """Aktif hatırlatıcıları getir"""
        return self.get_reminders(triggered=False)
        
    def get_triggered_reminders(self):
        """Tetiklenmiş hatırlatıcıları getir"""
        return self.get_reminders(triggered=True)
        
    def get_upcoming_reminders(self, hours=24):
        """Yaklaşan hatırlatıcıları getir"""
        try:
            future_time = datetime.now() + timedelta(hours=hours)
            return self.db.execute_query(
                "SELECT * FROM reminders WHERE reminder_time <= ? AND triggered = 0 ORDER BY reminder_time",
                (future_time,)
            )
        except Exception as e:
            print(f"Yaklaşan hatırlatıcı getirme hatası: {e}")
            return []
            
    def trigger_reminder(self, reminder_id):
        """Hatırlatıcıyı tetikle"""
        try:
            self.db.update_reminder(reminder_id, triggered=True)
            return True
        except Exception as e:
            print(f"Hatırlatıcı tetikleme hatası: {e}")
            return False
            
    def untrigger_reminder(self, reminder_id):
        """Hatırlatıcıyı tetiklenmemiş yap"""
        try:
            self.db.update_reminder(reminder_id, triggered=False)
            return True
        except Exception as e:
            print(f"Hatırlatıcı geri alma hatası: {e}")
            return False
            
    def update_reminder(self, reminder_id, **kwargs):
        """Hatırlatıcı güncelle"""
        try:
            self.db.update_reminder(reminder_id, **kwargs)
            return True
        except Exception as e:
            print(f"Hatırlatıcı güncelleme hatası: {e}")
            return False
            
    def delete_reminder(self, reminder_id):
        """Hatırlatıcı sil"""
        try:
            self.db.delete_reminder(reminder_id)
            return True
        except Exception as e:
            print(f"Hatırlatıcı silme hatası: {e}")
            return False
            
    def get_reminder_by_id(self, reminder_id):
        """ID'ye göre hatırlatıcı getir"""
        try:
            reminders = self.db.execute_query("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
            return reminders[0] if reminders else None
        except Exception as e:
            print(f"Hatırlatıcı getirme hatası: {e}")
            return None
            
    def check_due_reminders(self):
        """Vadesi gelen hatırlatıcıları kontrol et"""
        try:
            now = datetime.now()
            due_reminders = self.db.execute_query(
                "SELECT * FROM reminders WHERE reminder_time <= ? AND triggered = 0",
                (now,)
            )
            return due_reminders
        except Exception as e:
            print(f"Vadesi gelen hatırlatıcı kontrol hatası: {e}")
            return []
            
    def get_reminder_stats(self):
        """Hatırlatıcı istatistiklerini getir"""
        try:
            total = self.db.execute_query("SELECT COUNT(*) FROM reminders")[0][0]
            triggered = self.db.execute_query("SELECT COUNT(*) FROM reminders WHERE triggered = 1")[0][0]
            active = total - triggered
            
            return {
                'total': total,
                'triggered': triggered,
                'active': active,
                'trigger_rate': (triggered / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Hatırlatıcı istatistik hatası: {e}")
            return {'total': 0, 'triggered': 0, 'active': 0, 'trigger_rate': 0}
            
    def search_reminders(self, query):
        """Hatırlatıcı ara"""
        try:
            return self.db.execute_query(
                "SELECT * FROM reminders WHERE title LIKE ? OR message LIKE ? ORDER BY reminder_time",
                (f"%{query}%", f"%{query}%")
            )
        except Exception as e:
            print(f"Hatırlatıcı arama hatası: {e}")
            return []
            
    def clear_triggered_reminders(self):
        """Tetiklenmiş hatırlatıcıları temizle"""
        try:
            self.db.execute_query("DELETE FROM reminders WHERE triggered = 1")
            return True
        except Exception as e:
            print(f"Tetiklenmiş hatırlatıcı temizleme hatası: {e}")
            return False 