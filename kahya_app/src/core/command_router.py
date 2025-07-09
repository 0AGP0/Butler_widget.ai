import re
import threading
import json
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
from src.modules.todo import TodoManager
from src.modules.reminder import ReminderManager
from src.modules.file_ops import FileOperations
from src.modules.file_search import FileSearch
from src.modules.browser_control import BrowserControl
from src.modules.os_control import OSControl
from src.core.llm_client import LLMClient

class CommandRouter(QObject):
    command_processed = pyqtSignal(str)  # Yanıt sinyali
    
    def __init__(self, db_path, chatbox=None):
        super().__init__()
        self.db_path = db_path
        self.chatbox = chatbox
        
        # Modülleri başlat
        self.todo_manager = TodoManager(db_path)
        self.reminder_manager = ReminderManager(db_path)
        self.file_ops = FileOperations()
        self.file_search = FileSearch()
        self.browser_control = BrowserControl()
        self.os_control = OSControl()
        self.llm_client = LLMClient()
        
        # Doğal dil komut pattern'leri
        self.natural_patterns = {
            # Not alma
            r'(not|not al|not tut|kaydet|yaz)\s+(.+)': self.handle_note_add,
            r'(perşembe|pazartesi|salı|çarşamba|cuma|cumartesi|pazar)\s+(günü|gün)\s+(.+)': self.handle_day_note,
            r'(notlar|notlarım|kayıtlar)': self.handle_notes_list,
            
            # Hatırlatıcı silme (önce gelmeli)
            r'(.+)\s+(hatırlatıcısını|alarmını)\s+(sil|kaldır|iptal)': self.handle_reminder_delete,
            r'(sil|kaldır|iptal)\s+(.+)': self.handle_reminder_delete,
            # Hatırlatıcı - gelişmiş tarih algılama
            r'(hatırlat|hatırlatıcı|alarm)\s+(.+)': self.handle_reminder_natural,
            r'(saat)\s+(\d{1,2}):(\d{2})\s+(.+)': self.handle_time_reminder,
            r'(hatırlatıcılar|alarmlar)': self.handle_reminder_list_natural,
            r'(perşembe|pazartesi|salı|çarşamba|cuma|cumartesi|pazar)\s+(günü|gün)\s+(.+)': self.handle_day_reminder,
            r'(bu ayın|ayın)\s+(\d{1,2})\s+(günü|gün|sinde|sında)\s+(.+)': self.handle_month_day_reminder,
            r'(\d{1,2})\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)\s+(.+)': self.handle_month_name_reminder,
            r'(\d{1,2})/(\d{1,2})\s+(.+)': self.handle_date_reminder,
            r'(\d{1,2})\.(\d{1,2})\s+(.+)': self.handle_date_dot_reminder,
            
            # Todo
            r'(yapılacak|todo|görev|task)\s+(.+)': self.handle_todo_natural,
            r'(listele|göster|bak)\s+(yapılacak|todo|görev)': self.handle_todo_list_natural,
            r'(yapılacaklar|görevler)': self.handle_todo_list_natural,
            
            # İnternet
            r'(ara|google|internet)\s+(.+)': self.handle_web_search,
            r'(aç|git)\s+(.+)': self.handle_web_open,
            
            # Müzik
            r'(müzik|şarkı|çal|aç)\s+(.+)': self.handle_music,
            r'(spotify|youtube)\s+(.+)': self.handle_music_platform,
            
            # Dosya
            r'(dosya|belge)\s+(ara|bul)\s+(.+)': self.handle_file_search_natural,
            r'(dosya|belge)\s+(aç|göster)\s+(.+)': self.handle_file_open_natural,
        }
        
        # Eski komut pattern'leri (geriye uyumluluk için)
        self.command_patterns = {
            r'todo\s+ekle\s+(.+)': self.handle_todo_add,
            r'todo\s+listele': self.handle_todo_list,
            r'todo\s+sil\s+(\d+)': self.handle_todo_delete,
            r'todo\s+tamamla\s+(\d+)': self.handle_todo_complete,
            r'hatırlat\s+(.+?)\s+saat\s+(\d{1,2}):(\d{2})': self.handle_reminder_add,
            r'hatırlatıcı\s+listele': self.handle_reminder_list,
            r'dosya\s+ara\s+(.+)': self.handle_file_search,
            r'dosya\s+aç\s+(.+)': self.handle_file_open,
            r'tarayıcı\s+aç\s+(.+)': self.handle_browser_open,
            r'uygulama\s+aç\s+(.+)': self.handle_app_open,
            r'klasör\s+aç\s+(.+)': self.handle_folder_open,
        }
        
    def handle_command(self, command):
        """Komutu işle ve uygun modüle yönlendir"""
        command = command.strip()
        print(f"Router handle_command çağrıldı: '{command}'")
        
        # Yeni komut formatlarını kontrol et (chatbox'tan gelen)
        if command.startswith("hatırlatıcı_ekle "):
            content = command[16:]  # "hatırlatıcı_ekle " kısmını çıkar
            thread = threading.Thread(target=self._process_natural_reminder, args=(content,))
            thread.daemon = True
            thread.start()
            return
        elif command.startswith("not_al "):
            content = command[7:]  # "not_al " kısmını çıkar
            thread = threading.Thread(target=self._process_note_add, args=(content,))
            thread.daemon = True
            thread.start()
            return
        elif command.startswith("todo_ekle "):
            content = command[10:]  # "todo_ekle " kısmını çıkar
            thread = threading.Thread(target=self._process_todo_add, args=(content,))
            thread.daemon = True
            thread.start()
            return
        elif command == "hatırlatıcılar":
            thread = threading.Thread(target=self._process_reminder_list)
            thread.daemon = True
            thread.start()
            return
        elif command == "notlar":
            thread = threading.Thread(target=self._process_notes_list)
            thread.daemon = True
            thread.start()
            return
        
        # Doğal dil pattern'lerini kontrol et
        command_lower = command.lower()
        print(f"Komut kontrol ediliyor: '{command_lower}'")
        for pattern, handler in self.natural_patterns.items():
            match = re.match(pattern, command_lower)
            if match:
                print(f"Pattern eşleşti: {pattern}")
                thread = threading.Thread(target=self._process_command, args=(handler, match))
                thread.daemon = True
                thread.start()
                return
        
        # Eski pattern'leri kontrol et
        for pattern, handler in self.command_patterns.items():
            match = re.match(pattern, command_lower)
            if match:
                thread = threading.Thread(target=self._process_command, args=(handler, match))
                thread.daemon = True
                thread.start()
                return
        
        # Hiçbiri eşleşmezse LLM'e gönder
        thread = threading.Thread(target=self._process_llm_command, args=(command,))
        thread.daemon = True
        thread.start()
        
    def _process_command(self, handler, match):
        """Komutu arka planda işle"""
        try:
            result = handler(match)
            self.command_processed.emit(result)
        except Exception as e:
            self.command_processed.emit(f"Hata: {str(e)}")
            
    def _process_llm_command(self, command):
        """LLM komutunu arka planda işle"""
        try:
            response = self.llm_client.get_response(command)
            self.command_processed.emit(response)
        except Exception as e:
            self.command_processed.emit(f"LLM hatası: {str(e)}")
    
    def _process_natural_reminder(self, content):
        """Doğal hatırlatıcı işleme"""
        try:
            # Tarih/saat algılama
            import re
            from datetime import datetime, timedelta
            
            # Tarih pattern'leri
            date_patterns = [
                (r'(\d{1,2})\s*(?:ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)', self._parse_month_name),
                (r'(\d{1,2})/(\d{1,2})', self._parse_slash_date),
                (r'(\d{1,2})\.(\d{1,2})', self._parse_dot_date),
                (r'ayın\s+(\d{1,2})', self._parse_month_day),
                (r'bu ayın\s+(\d{1,2})', self._parse_month_day),
                (r'(\d{1,2})\s+sinde', self._parse_sinde_date),  # "20 sinde"
                (r'(\d{1,2})\s+sında', self._parse_sinde_date),  # "20 sında"
                (r'(\d{1,2})\s+günü', self._parse_sinde_date),   # "20 günü"
                (r'(\d{1,2})\s+gün', self._parse_sinde_date),    # "20 gün"
                (r'cumartesi', self._parse_day_name),  # Daha uzun olanları önce koy
                (r'pazartesi', self._parse_day_name),
                (r'çarşamba', self._parse_day_name),
                (r'perşembe', self._parse_day_name),
                (r'cuma', self._parse_day_name),
                (r'salı', self._parse_day_name),
                (r'pazar', self._parse_day_name),
                (r'yarın', lambda m: datetime.now() + timedelta(days=1)),
                (r'bugün', lambda m: datetime.now()),
            ]
            
            target_date = None
            target_time = datetime.now().replace(hour=9, minute=0)  # Varsayılan: sabah 9
            
            # Tarih algıla
            for pattern, parser in date_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    target_date = parser(match)
                    break
            
            if not target_date:
                target_date = datetime.now() + timedelta(days=1)  # Varsayılan: yarın
            
            # Saat algıla
            time_match = re.search(r'(\d{1,2}):(\d{2})', content)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                target_time = target_date.replace(hour=hour, minute=minute)
            else:
                target_time = target_date.replace(hour=9, minute=0)
            
            # Hatırlatıcı başlığını temizle
            clean_title = content.replace("hatırlat", "").replace("  ", " ").strip()
            
            # Tarih bilgilerini temizle
            import re
            clean_title = re.sub(r'\d{1,2}\s+sinde', '', clean_title)
            clean_title = re.sub(r'\d{1,2}\s+sında', '', clean_title)
            # Gün adlarını daha spesifik temizle
            clean_title = re.sub(r'\bcumartesi\b', '', clean_title)
            clean_title = re.sub(r'\bpazartesi\b', '', clean_title)
            clean_title = re.sub(r'\bsalı\b', '', clean_title)
            clean_title = re.sub(r'\bçarşamba\b', '', clean_title)
            clean_title = re.sub(r'\bperşembe\b', '', clean_title)
            clean_title = re.sub(r'\bcuma\b', '', clean_title)
            clean_title = re.sub(r'\bpazar\b', '', clean_title)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()
            
            # Hatırlatıcı ekle
            self.reminder_manager.add_reminder(clean_title, content, target_time.hour, target_time.minute, target_time.date())
            
            # Takvimi güncelle
            if hasattr(self, 'chatbox') and self.chatbox:
                # Chatbox'ın parent'ına eriş (KahyaWallpaper)
                parent = self.chatbox.parent()
                if parent and hasattr(parent, 'calendar'):
                    # Ana thread'de güncelle
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, parent.calendar.update_reminders)
            
            result = f"⏰ Hatırlatıcı eklendi: {clean_title}\n📅 Tarih: {target_time.strftime('%d.%m.%Y %H:%M')}"
            self.command_processed.emit(result)
            
        except Exception as e:
            self.command_processed.emit(f"❌ Hatırlatıcı eklenirken hata: {str(e)}")
    
    def _process_note_add(self, content):
        """Not ekleme işleme"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Dosyaya kaydet
            with open("kahya_notes.txt", "a", encoding="utf-8") as f:
                f.write(f"{timestamp}: {content}\n")
                
            result = f"📝 Not kaydedildi: {content}"
            self.command_processed.emit(result)
            
        except Exception as e:
            self.command_processed.emit(f"❌ Not eklenirken hata: {str(e)}")
    
    def _process_todo_add(self, content):
        """Todo ekleme işleme"""
        try:
            self.todo_manager.add_todo(content)
            result = f"✅ Yapılacak eklendi: {content}"
            self.command_processed.emit(result)
            
        except Exception as e:
            self.command_processed.emit(f"❌ Todo eklenirken hata: {str(e)}")
    
    def _process_reminder_list(self):
        """Hatırlatıcı listesi işleme"""
        try:
            reminders = self.reminder_manager.get_reminders()
            if not reminders:
                result = "📅 Henüz hatırlatıcı yok"
            else:
                result = "📅 Hatırlatıcılarınız:\n"
                for reminder in reminders:
                    reminder_time = datetime.fromisoformat(reminder[3])
                    status = "✅" if reminder[5] else "⏳"
                    result += f"{status} {reminder_time.strftime('%d.%m.%Y %H:%M')} - {reminder[1]}\n"
            
            self.command_processed.emit(result)
            
        except Exception as e:
            self.command_processed.emit(f"❌ Hatırlatıcılar listelenirken hata: {str(e)}")
    
    def _process_notes_list(self):
        """Notlar listesi işleme"""
        try:
            try:
                with open("kahya_notes.txt", "r", encoding="utf-8") as f:
                    notes = f.readlines()
                
                if not notes:
                    result = "📝 Henüz not yok"
                else:
                    result = "📝 Notlarınız:\n"
                    for note in notes[-10:]:  # Son 10 not
                        result += f"• {note.strip()}\n"
                        
            except FileNotFoundError:
                result = "📝 Henüz not yok"
            
            self.command_processed.emit(result)
            
        except Exception as e:
            self.command_processed.emit(f"❌ Notlar listelenirken hata: {str(e)}")
    
    # Tarih ayrıştırma yardımcı fonksiyonları
    def _parse_month_name(self, match):
        """Ay adı ile tarih ayrıştırma"""
        day = int(match.group(1))
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Ay adlarını sayıya çevir
        month_names = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
            'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        
        # Metinden ay adını bul
        import re
        for month_name, month_num in month_names.items():
            if re.search(month_name, match.string.lower()):
                month = month_num
                break
        else:
            month = current_month
        
        # Gelecek yıl kontrolü
        if month < current_month:
            year = current_year + 1
        else:
            year = current_year
            
        return datetime(year, month, day)
    
    def _parse_slash_date(self, match):
        """Slash ile tarih ayrıştırma (DD/MM)"""
        day = int(match.group(1))
        month = int(match.group(2))
        current_year = datetime.now().year
        
        # Gelecek yıl kontrolü
        if month < datetime.now().month:
            year = current_year + 1
        else:
            year = current_year
            
        return datetime(year, month, day)
    
    def _parse_dot_date(self, match):
        """Nokta ile tarih ayrıştırma (DD.MM)"""
        day = int(match.group(1))
        month = int(match.group(2))
        current_year = datetime.now().year
        
        # Gelecek yıl kontrolü
        if month < datetime.now().month:
            year = current_year + 1
        else:
            year = current_year
            
        return datetime(year, month, day)
    
    def _parse_month_day(self, match):
        """Ayın X. günü formatı"""
        day = int(match.group(1))
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        return datetime(current_year, current_month, day)
    
    def _parse_sinde_date(self, match):
        """X sinde/sında/günü formatı (bu ayın X. günü)"""
        day = int(match.group(1))
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # Bu ayın belirtilen günü
        target_date = datetime(current_year, current_month, day)
        
        # Eğer bu ay geçtiyse gelecek ay
        if target_date < datetime.now():
            if current_month == 12:
                target_date = datetime(current_year + 1, 1, day)
            else:
                target_date = datetime(current_year, current_month + 1, day)
        
        return target_date
    
    def _parse_day_name(self, match):
        """Gün adı formatı (cumartesi, pazartesi vb.)"""
        day_name = match.group(0).lower()
        
        print(f"Gün adı parse ediliyor: '{day_name}'")
        
        # Gün adlarını sayıya çevir
        day_map = {
            'pazartesi': 0, 'salı': 1, 'çarşamba': 2, 'perşembe': 3,
            'cuma': 4, 'cumartesi': 5, 'pazar': 6
        }
        
        target_day = day_map.get(day_name)
        if target_day is not None:
            # Bu hafta veya gelecek hafta
            current_day = datetime.now().weekday()
            days_ahead = target_day - current_day
            if days_ahead <= 0:  # Bu hafta geçtiyse gelecek hafta
                days_ahead += 7
            
            target_date = datetime.now() + timedelta(days=days_ahead)
            print(f"Gün hesaplaması: {day_name} -> {target_day}, bugün: {current_day}, günler: {days_ahead}, tarih: {target_date}")
            return target_date
        
        return datetime.now() + timedelta(days=1)  # Varsayılan: yarın
    
    # Doğal dil işleyicileri
    def handle_note_add(self, match):
        """Not alma işleyicisi"""
        content = match.group(2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = f"📝 Not ({timestamp}): {content}"
        
        # Dosyaya kaydet
        try:
            with open("kahya_notes.txt", "a", encoding="utf-8") as f:
                f.write(f"{timestamp}: {content}\n")
        except:
            pass
            
        return f"✅ Not kaydedildi: {content}"
    
    def handle_day_note(self, match):
        """Günlük not alma işleyicisi"""
        day = match.group(1)
        content = match.group(3)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        note = f"📅 {day.capitalize()} notu: {content}"
        
        # Dosyaya kaydet
        try:
            with open("kahya_notes.txt", "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - {day.capitalize()}: {content}\n")
        except:
            pass
            
        return f"✅ {day.capitalize()} notu kaydedildi: {content}"
    
    def handle_reminder_natural(self, match):
        """Doğal hatırlatıcı işleyicisi"""
        content = match.group(2)
        # Varsayılan olarak 1 saat sonra
        reminder_time = datetime.now() + timedelta(hours=1)
        self.reminder_manager.add_reminder(content, content, reminder_time.hour, reminder_time.minute)
        return f"⏰ Hatırlatıcı eklendi: {content} (saat {reminder_time.strftime('%H:%M')})"
    
    def handle_time_reminder(self, match):
        """Zamanlı hatırlatıcı işleyicisi"""
        hour = int(match.group(2))
        minute = int(match.group(3))
        content = match.group(4)
        self.reminder_manager.add_reminder(content, content, hour, minute)
        return f"⏰ Hatırlatıcı eklendi: {content} saat {hour:02d}:{minute:02d}"
    
    def handle_todo_natural(self, match):
        """Doğal todo işleyicisi"""
        content = match.group(2)
        self.todo_manager.add_todo(content)
        return f"✅ Yapılacak eklendi: {content}"
    
    def handle_todo_list_natural(self, match):
        """Doğal todo listesi işleyicisi"""
        todos = self.todo_manager.get_todos()
        if not todos:
            return "📝 Henüz yapılacak görev yok"
        
        result = "📝 Yapılacaklar:\n"
        for todo in todos:
            status = "✅" if todo[4] else "⏳"
            result += f"{status} {todo[1]}\n"
        return result
    
    def handle_web_search(self, match):
        """Web arama işleyicisi"""
        query = match.group(2)
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        success = self.browser_control.open_url(search_url)
        if success:
            return f"🔍 Google'da aranıyor: {query}"
        else:
            return f"❌ Arama yapılamadı: {query}"
    
    def handle_web_open(self, match):
        """Web sitesi açma işleyicisi"""
        url = match.group(2)
        # URL kontrolü
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        success = self.browser_control.open_url(url)
        if success:
            return f"🌐 Site açıldı: {url}"
        else:
            return f"❌ Site açılamadı: {url}"
    
    def handle_music(self, match):
        """Müzik işleyicisi"""
        query = match.group(2)
        # YouTube'da müzik ara
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+müzik"
        success = self.browser_control.open_url(search_url)
        if success:
            return f"🎵 YouTube'da müzik aranıyor: {query}"
        else:
            return f"❌ Müzik açılamadı: {query}"
    
    def handle_music_platform(self, match):
        """Müzik platformu işleyicisi"""
        platform = match.group(1)
        query = match.group(2)
        
        if platform == "spotify":
            url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
        else:  # youtube
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        success = self.browser_control.open_url(url)
        if success:
            return f"🎵 {platform.capitalize()} açıldı: {query}"
        else:
            return f"❌ {platform.capitalize()} açılamadı: {query}"
    
    def handle_file_search_natural(self, match):
        """Doğal dosya arama işleyicisi"""
        query = match.group(3)
        results = self.file_search.search_files(query)
        if not results:
            return f"🔍 '{query}' için dosya bulunamadı"
        
        result = f"🔍 '{query}' için bulunan dosyalar:\n"
        for file_path in results[:5]:
            result += f"📄 {file_path}\n"
        return result
    
    def handle_file_open_natural(self, match):
        """Doğal dosya açma işleyicisi"""
        file_path = match.group(3)
        success = self.file_ops.open_file(file_path)
        if success:
            return f"📄 Dosya açıldı: {file_path}"
        else:
            return f"❌ Dosya açılamadı: {file_path}"
    
    def handle_notes_list(self, match):
        """Notları listele"""
        try:
            with open("kahya_notes.txt", "r", encoding="utf-8") as f:
                notes = f.readlines()
            
            if not notes:
                return "📝 Henüz not yok"
            
            result = "📝 Notlarınız:\n"
            for i, note in enumerate(notes[-10:], 1):  # Son 10 not
                result += f"{i}. {note.strip()}\n"
            return result
        except FileNotFoundError:
            return "📝 Henüz not yok"
        except Exception as e:
            return f"❌ Notlar okunamadı: {str(e)}"
    
    def handle_reminder_list_natural(self, match):
        """Doğal hatırlatıcı listesi"""
        reminders = self.reminder_manager.get_reminders()
        print(f"Router: {len(reminders)} hatırlatıcı bulundu")
        if not reminders:
            return "⏰ Henüz hatırlatıcı yok"
        
        result = "⏰ Hatırlatıcılarınız:\n"
        for i, reminder in enumerate(reminders, 1):
            print(f"  Router: Hatırlatıcı {i}: {reminder}")
            result += f"{i}. {reminder[1]} - {reminder[3]}\n"
        return result
    
    def handle_reminder_delete(self, match):
        """Hatırlatıcı silme"""
        try:
            print(f"Silme komutu algılandı: {match.groups()}")
            # Silme kriterlerini belirle
            if len(match.groups()) >= 3:  # "11 temmuz hatırlatıcısını sil" formatı
                search_text = match.group(1)  # "11 temmuz"
            else:  # "sil 11 temmuz" formatı
                search_text = match.group(2)
            
            print(f"Aranan metin: '{search_text}'")
            
            # Hatırlatıcıları al
            reminders = self.reminder_manager.get_reminders()
            if not reminders:
                return "📅 Silinecek hatırlatıcı bulunamadı."
            
            # Eşleşen hatırlatıcıları bul
            matched_reminders = []
            for reminder in reminders:
                title = reminder[1].lower()
                reminder_date = datetime.fromisoformat(reminder[3])
                date_str = reminder_date.strftime("%d.%m.%Y")
                
                print(f"Kontrol edilen: '{title}' - {date_str}")
                
                # Tarih eşleşmesi için doğal dil tarihini parse et
                search_lower = search_text.lower()
                matched = False
                
                # Başlık eşleşmesi
                if search_lower in title:
                    matched = True
                    print(f"Başlık eşleşti: {title}")
                
                # Tarih eşleşmesi - "11 temmuz" formatını kontrol et
                if not matched:
                    # "11 temmuz" formatını parse et
                    import re
                    date_match = re.search(r'(\d{1,2})\s+(ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık)', search_lower)
                    if date_match:
                        day = int(date_match.group(1))
                        month_name = date_match.group(2)
                        month_map = {
                            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
                            'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
                        }
                        month = month_map.get(month_name)
                        if month and reminder_date.day == day and reminder_date.month == month:
                            matched = True
                            print(f"Tarih eşleşti: {day}.{month} - {reminder_date}")
                
                # Normal tarih formatı eşleşmesi
                if not matched and (search_lower in date_str or date_str in search_lower):
                    matched = True
                    print(f"Tarih string eşleşti: {date_str}")
                
                if matched:
                    matched_reminders.append(reminder)
            
            if not matched_reminders:
                return f"📅 '{search_text}' ile eşleşen hatırlatıcı bulunamadı."
            
            # Eşleşen hatırlatıcıları sil
            deleted_count = 0
            for reminder in matched_reminders:
                if self.reminder_manager.delete_reminder(reminder[0]):  # reminder[0] = id
                    deleted_count += 1
            
            # Takvimi güncelle (ana thread'de)
            if hasattr(self, 'chatbox') and self.chatbox:
                parent = self.chatbox.parent()
                if parent and hasattr(parent, 'calendar'):
                    # Ana thread'de güncelle
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(0, parent.calendar.update_reminders)
            
            return f"🗑️ {deleted_count} hatırlatıcı silindi."
            
        except Exception as e:
            return f"❌ Hatırlatıcı silme hatası: {str(e)}"
    
    def handle_day_reminder(self, match):
        """Günlük hatırlatıcı işleyicisi"""
        day = match.group(1)
        content = match.group(3)
        
        print(f"Router: Günlük hatırlatıcı ekleniyor - {day}: {content}")
        
        # Günü tarihe çevir
        day_map = {
            'pazartesi': 0, 'salı': 1, 'çarşamba': 2, 'perşembe': 3,
            'cuma': 4, 'cumartesi': 5, 'pazar': 6
        }
        
        target_day = day_map.get(day.lower())
        if target_day is not None:
            # Bu hafta veya gelecek hafta
            current_day = datetime.now().weekday()
            days_ahead = target_day - current_day
            if days_ahead <= 0:  # Bu hafta geçtiyse gelecek hafta
                days_ahead += 7
            
            target_date = datetime.now() + timedelta(days=days_ahead)
            print(f"Router: Hedef tarih: {target_date}")
            
            success = self.reminder_manager.add_reminder(content, content, target_date.hour, target_date.minute)
            print(f"Router: Hatırlatıcı ekleme sonucu: {success}")
            
            return f"⏰ {day.capitalize()} hatırlatıcısı eklendi: {content}"
        else:
            return f"❌ Gün tanınmadı: {day}"
    
    def handle_month_day_reminder(self, match):
        """Bu ayın X günü hatırlatıcısı"""
        day = int(match.group(2))
        content = match.group(4)
        
        # Bu ayın belirtilen günü
        current_date = datetime.now()
        target_date = current_date.replace(day=day)
        
        # Eğer bu ay geçtiyse gelecek ay
        if target_date < current_date:
            if current_date.month == 12:
                target_date = target_date.replace(year=current_date.year + 1, month=1)
            else:
                target_date = target_date.replace(month=current_date.month + 1)
        
        success = self.reminder_manager.add_reminder(content, content, target_date.hour, target_date.minute)
        return f"⏰ {day}. gün hatırlatıcısı eklendi: {content}"
    
    def handle_month_name_reminder(self, match):
        """Ay adı ile tarih hatırlatıcısı"""
        day = int(match.group(1))
        month_name = match.group(2)
        content = match.group(3)
        
        month_map = {
            'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
            'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
        }
        
        month = month_map.get(month_name.lower())
        if month is None:
            return f"❌ Ay tanınmadı: {month_name}"
        
        current_date = datetime.now()
        target_date = current_date.replace(month=month, day=day)
        
        # Eğer bu yıl geçtiyse gelecek yıl
        if target_date < current_date:
            target_date = target_date.replace(year=current_date.year + 1)
        
        success = self.reminder_manager.add_reminder(content, content, target_date.hour, target_date.minute)
        return f"⏰ {day} {month_name.capitalize()} hatırlatıcısı eklendi: {content}"
    
    def handle_date_reminder(self, match):
        """DD/MM formatında tarih hatırlatıcısı"""
        day = int(match.group(1))
        month = int(match.group(2))
        content = match.group(3)
        
        current_date = datetime.now()
        target_date = current_date.replace(month=month, day=day)
        
        # Eğer bu yıl geçtiyse gelecek yıl
        if target_date < current_date:
            target_date = target_date.replace(year=current_date.year + 1)
        
        success = self.reminder_manager.add_reminder(content, content, target_date.hour, target_date.minute)
        return f"⏰ {day}/{month} hatırlatıcısı eklendi: {content}"
    
    def handle_date_dot_reminder(self, match):
        """DD.MM formatında tarih hatırlatıcısı"""
        day = int(match.group(1))
        month = int(match.group(2))
        content = match.group(3)
        
        current_date = datetime.now()
        target_date = current_date.replace(month=month, day=day)
        
        # Eğer bu yıl geçtiyse gelecek yıl
        if target_date < current_date:
            target_date = target_date.replace(year=current_date.year + 1)
        
        success = self.reminder_manager.add_reminder(content, content, target_date.hour, target_date.minute)
        return f"⏰ {day}.{month} hatırlatıcısı eklendi: {content}"
    
    # Eski komut işleyicileri (geriye uyumluluk)
    def handle_todo_add(self, match):
        title = match.group(1)
        self.todo_manager.add_todo(title)
        return f"✅ Todo eklendi: {title}"

    def handle_todo_list(self, match):
        todos = self.todo_manager.get_todos()
        if not todos:
            return "📝 Henüz todo yok"
        
        result = "📝 Todolar:\n"
        for todo in todos:
            status = "✅" if todo[4] else "⏳"
            result += f"{status} {todo[1]}\n"
        return result

    def handle_todo_delete(self, match):
        todo_id = int(match.group(1))
        self.todo_manager.delete_todo(todo_id)
        return f"🗑️ Todo silindi (ID: {todo_id})"

    def handle_todo_complete(self, match):
        todo_id = int(match.group(1))
        self.todo_manager.complete_todo(todo_id)
        return f"✅ Todo tamamlandı (ID: {todo_id})"
    
    def handle_reminder_add(self, match):
        message = match.group(1)
        hour = int(match.group(2))
        minute = int(match.group(3))
        self.reminder_manager.add_reminder(message, message, hour, minute)
        return f"⏰ Hatırlatıcı eklendi: {message} saat {hour:02d}:{minute:02d}"
        
    def handle_reminder_list(self, match):
        reminders = self.reminder_manager.get_reminders()
        if not reminders:
            return "⏰ Henüz hatırlatıcı yok"
        
        result = "⏰ Hatırlatıcılar:\n"
        for reminder in reminders:
            result += f"📅 {reminder[1]} - {reminder[3]}\n"
        return result
    
    def handle_file_search(self, match):
        query = match.group(1)
        results = self.file_search.search_files(query)
        if not results:
            return f"🔍 '{query}' için dosya bulunamadı"
        
        result = f"🔍 '{query}' için bulunan dosyalar:\n"
        for file_path in results[:5]:
            result += f"📄 {file_path}\n"
        return result
        
    def handle_file_open(self, match):
        file_path = match.group(1)
        success = self.file_ops.open_file(file_path)
        if success:
            return f"📄 Dosya açıldı: {file_path}"
        else:
            return f"❌ Dosya açılamadı: {file_path}"
    
    def handle_browser_open(self, match):
        url = match.group(1)
        success = self.browser_control.open_url(url)
        if success:
            return f"🌐 Tarayıcıda açıldı: {url}"
        else:
            return f"❌ URL açılamadı: {url}"
    
    def handle_app_open(self, match):
        app_name = match.group(1)
        success = self.os_control.open_application(app_name)
        if success:
            return f"🚀 Uygulama açıldı: {app_name}"
        else:
            return f"❌ Uygulama açılamadı: {app_name}"
            
    def handle_folder_open(self, match):
        folder_path = match.group(1)
        success = self.os_control.open_folder(folder_path)
        if success:
            return f"📁 Klasör açıldı: {folder_path}"
        else:
            return f"❌ Klasör açılamadı: {folder_path}" 