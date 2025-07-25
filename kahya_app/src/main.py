import sys
import os

# Proje kök dizinini Python path'ine ekle
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
from src.ui.kahya_wallpaper import KahyaWallpaper
from src.core.command_router import CommandRouter
from src.core.llm_client import LLMClient
from src.modules.usage_tracker import UsageTracker

from src.modules.reminder import ReminderManager
from src.core.database import Database

def main():
    # Uygulama başlat
    app = QApplication(sys.argv)
    
    # Veritabanı yolunu ayarla
    db_path = os.path.join(project_root, 'data', 'kahya.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Veritabanını başlat
    db = Database(db_path)
    
    # LLM istemcisini başlat
    llm_client = LLMClient()
    
    # Kullanıcı modeli ve istatistik takip sistemini başlat
    usage_tracker = UsageTracker(db_path)
    reminder_manager = ReminderManager(db_path)
    
    # UI bileşenlerini oluştur (sadece KahyaWallpaper)
    kahya = KahyaWallpaper(db_path, usage_tracker)
    
    # Takvime hatırlatıcı yöneticisini bağla
    kahya.calendar.set_reminder_manager(reminder_manager)
    
    # Chatbox'a LLM istemcisini bağla
    kahya.retro_chatbox.set_llm_client(llm_client)
    
    # Komut yönlendiriciyi başlat (chatbox wallpaper içinde)
    router = CommandRouter(db_path, kahya.retro_chatbox)
    
    # Wallpaper içindeki chatbox'a router'ı bağla
    kahya.retro_chatbox.set_router(router)
    
    # Sinyal bağlantıları
    kahya.command_received.connect(router.handle_command)
    kahya.retro_chatbox.command_sent.connect(router.handle_command)
    
    # Router'ın yanıtlarını retro_chatbox'a bağla
    router.command_processed.connect(kahya.retro_chatbox.add_response)
    
    # İstatistik takip sistemini başlat
    usage_tracker.app_changed.connect(lambda old, new: kahya.show_notification(
        f"Uygulama değişti: {new}",
        f"Önceki uygulama: {old}"
    ))
    
    usage_tracker.insight_ready.connect(lambda insight: kahya.show_notification(
        "Yeni İçgörü",
        insight
    ))
    
    # Uygulama kapanırken temizlik
    app.aboutToQuit.connect(usage_tracker.cleanup)
    app.aboutToQuit.connect(kahya.cleanup)
    
    # Global kısayol tuşları (uygulama seviyesinde)
    def setup_global_shortcuts():
        # Ctrl+Shift+C: Kontrol menüsünü göster
        control_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), kahya)
        control_shortcut.activated.connect(kahya.show_control_menu)
        
        # Ctrl+Shift+W: Gizli widget'ları göster
        widget_shortcut = QShortcut(QKeySequence("Ctrl+Shift+W"), kahya)
        widget_shortcut.activated.connect(kahya.show_hidden_widgets)
        
        # Ctrl+Shift+A: Tüm widget'ları gizle/göster
        toggle_all_shortcut = QShortcut(QKeySequence("Ctrl+Shift+A"), kahya)
        toggle_all_shortcut.activated.connect(kahya.toggle_all_widgets)
        
        # Ctrl+Shift+H: Ana uygulamayı gizle/göster
        hide_shortcut = QShortcut(QKeySequence("Ctrl+Shift+H"), kahya)
        hide_shortcut.activated.connect(kahya.toggle_visibility)
    
    # Global kısayol tuşlarını kur
    setup_global_shortcuts()
    
    # Pencereyi göster (sadece KahyaWallpaper)
    kahya.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 