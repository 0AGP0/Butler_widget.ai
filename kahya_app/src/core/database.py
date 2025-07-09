import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Kullanıcı profili tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                preferences TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        # Uygulama kullanım logları
        c.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                session_count INTEGER DEFAULT 1,
                duration INTEGER,
                last_used TEXT
            )
        ''')
        # Hatırlatıcılar tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                message TEXT,
                reminder_time TEXT,
                triggered INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        # Todo tablosu
        c.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    # Kullanıcı profilini getir
    def get_user_profile(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM user_profile ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        conn.close()
        return row

    # Kullanıcı profilini kaydet/güncelle
    def save_user_profile(self, name, preferences_json):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        # Eğer profil varsa güncelle, yoksa ekle
        c.execute('SELECT id FROM user_profile ORDER BY id DESC LIMIT 1')
        row = c.fetchone()
        if row:
            c.execute('UPDATE user_profile SET name=?, preferences=?, updated_at=? WHERE id=?',
                      (name, preferences_json, now, row[0]))
        else:
            c.execute('INSERT INTO user_profile (name, preferences, created_at, updated_at) VALUES (?, ?, ?, ?)',
                      (name, preferences_json, now, now))
            conn.commit()
            conn.close()

    # Uygulama kullanımını logla
    def log_app_usage(self, app_name, duration):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        # Eğer aynı gün içinde aynı uygulama varsa güncelle
        c.execute('SELECT id, session_count, duration FROM app_usage WHERE app_name=? AND last_used>=?',
                  (app_name, (datetime.now() - timedelta(days=1)).isoformat()))
        row = c.fetchone()
        if row:
            new_count = row[1] + 1
            new_duration = row[2] + duration
            c.execute('UPDATE app_usage SET session_count=?, duration=?, last_used=? WHERE id=?',
                      (new_count, new_duration, now, row[0]))
        else:
            c.execute('INSERT INTO app_usage (app_name, session_count, duration, last_used) VALUES (?, ?, ?, ?)',
                      (app_name, 1, duration, now))
        conn.commit()
        conn.close()

    # Son X günün uygulama kullanım istatistiklerini getir
    def get_app_usage_stats(self, days=7):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        since = (datetime.now() - timedelta(days=days)).isoformat()
        c.execute('SELECT app_name, session_count, duration, last_used FROM app_usage WHERE last_used>=? ORDER BY duration DESC', (since,))
        rows = c.fetchall()
        conn.close()
        return rows

    # Hatırlatıcı fonksiyonları
    def add_reminder(self, title, message, reminder_time):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        # reminder_time datetime objesi ise string'e çevir
        if isinstance(reminder_time, datetime):
            reminder_time_str = reminder_time.isoformat()
        else:
            reminder_time_str = str(reminder_time)
            
        c.execute('INSERT INTO reminders (title, message, reminder_time, created_at) VALUES (?, ?, ?, ?)',
                  (title, message, reminder_time_str, now))
        conn.commit()
        conn.close()
        
    def get_reminders(self, triggered=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if triggered is not None:
            c.execute('SELECT * FROM reminders WHERE triggered = ? ORDER BY reminder_time', (1 if triggered else 0,))
        else:
            c.execute('SELECT * FROM reminders ORDER BY reminder_time')
        rows = c.fetchall()
        conn.close()
        return rows
            
    def update_reminder(self, reminder_id, **kwargs):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if 'triggered' in kwargs:
            c.execute('UPDATE reminders SET triggered = ? WHERE id = ?', (1 if kwargs['triggered'] else 0, reminder_id))
        conn.commit()
        conn.close()
        
    def delete_reminder(self, reminder_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        conn.commit()
        conn.close()

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
        conn.commit()
        conn.close()
        return rows

    # Todo fonksiyonları
    def add_todo(self, title):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute('INSERT INTO todos (title, created_at) VALUES (?, ?)', (title, now))
        conn.commit()
        conn.close()
            
    def get_todos(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM todos ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        return rows

    def complete_todo(self, todo_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE todos SET completed = 1 WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close()
        
    def delete_todo(self, todo_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        conn.commit()
        conn.close() 