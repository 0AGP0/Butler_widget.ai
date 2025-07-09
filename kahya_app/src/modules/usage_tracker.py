import psutil
import time
import threading
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
from src.core.database import Database

class UsageTracker(QObject):
    app_changed = pyqtSignal(str, str)  # eski_app, yeni_app
    insight_ready = pyqtSignal(str)  # insight mesajı

    def __init__(self, db_path):
        super().__init__()
        self.db = Database(db_path)
        self.current_app = None
        self.app_start_time = None
        self.is_running = False
        self.tracking_thread = None
        
        # İstatistik ayarları
        self.check_interval = 2  # saniye
        self.insight_threshold = 30  # dakika
        
    def start_tracking(self):
        """Kullanım takibini başlat"""
        if self.is_running:
            return
            
        self.is_running = True
        self.tracking_thread = threading.Thread(target=self._track_usage, daemon=True)
        self.tracking_thread.start()
        print("Kullanım takibi başlatıldı")
        
    def stop_tracking(self):
        """Kullanım takibini durdur"""
        self.is_running = False
        if self.tracking_thread:
            self.tracking_thread.join(timeout=1)
        print("Kullanım takibi durduruldu")
        
    def _track_usage(self):
        """Arka planda kullanım takibi yap"""
        while self.is_running:
            try:
                current_app = self._get_active_application()

                if current_app != self.current_app:
                    # Uygulama değişti
                    if self.current_app and self.app_start_time:
                        duration = int((datetime.now() - self.app_start_time).total_seconds())
                        self._log_app_usage(self.current_app, duration)

                    # Yeni uygulamayı başlat
                    self.current_app = current_app
                    self.app_start_time = datetime.now()

                    # Sinyal gönder
                    if self.current_app:
                        self.app_changed.emit(self.current_app, current_app)

                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Kullanım takibi hatası: {e}")
                time.sleep(self.check_interval)
                
    def _get_active_application(self):
        """Aktif uygulamayı al"""
        try:
            # Windows için
            import win32gui
            import win32process
            
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            if pid:
                process = psutil.Process(pid)
                return process.name()
                
        except ImportError:
            # win32gui yoksa basit yöntem
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name']:
                        return proc.info['name']
            except:
                pass
                
        return "unknown"
        
    def _log_app_usage(self, app_name, duration):
        """Uygulama kullanımını logla"""
        try:
            self.db.log_app_usage(app_name, duration=duration)
            
            # Uzun süreli kullanım için insight
            if duration > self.insight_threshold * 60:  # dakikayı saniyeye çevir
                insight = f"{app_name} uygulamasını {duration//60} dakika kullandınız"
                self.insight_ready.emit(insight)
        
        except Exception as e:
            print(f"Kullanım loglama hatası: {e}")

    def get_usage_stats(self, days=7):
        """Kullanım istatistiklerini getir"""
        try:
            return self.db.get_app_usage_stats(days)
        except Exception as e:
            print(f"İstatistik alma hatası: {e}")
            return []
            
    def get_top_apps(self, limit=5):
        """En çok kullanılan uygulamaları getir"""
        stats = self.get_usage_stats()
        return stats[:limit]

    def cleanup(self):
        """Temizlik işlemleri"""
        self.stop_tracking()
        
        # Mevcut uygulamayı logla
        if self.current_app and self.app_start_time:
            duration = int((datetime.now() - self.app_start_time).total_seconds())
            self._log_app_usage(self.current_app, duration) 