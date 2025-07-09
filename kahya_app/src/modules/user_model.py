import json
from datetime import datetime
from src.core.database import Database

class UserModel:
    def __init__(self, db_path):
        self.db = Database(db_path)
        self.user_data = self._load_user_data()
        
    def _load_user_data(self):
        """Kullanıcı verilerini yükle"""
        profile = self.db.get_user_profile()
        if profile:
            return {
                'id': profile[0],
                'name': profile[1],
                'preferences': json.loads(profile[2]) if profile[2] else {},
                'created_at': profile[3],
                'updated_at': profile[4]
                }
        else:
            # Varsayılan kullanıcı oluştur
            return {
                'id': None,
                'name': 'Kullanıcı',
                'preferences': {
                    'theme': 'retro',
                    'language': 'tr',
                    'notifications': True,
                    'auto_start': False
                },
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
    def save_user_data(self):
        """Kullanıcı verilerini kaydet"""
        preferences_json = json.dumps(self.user_data['preferences'])
        self.db.save_user_profile(self.user_data['name'], preferences_json)
        
    def get_name(self):
        """Kullanıcı adını getir"""
        return self.user_data['name']
        
    def set_name(self, name):
        """Kullanıcı adını ayarla"""
        self.user_data['name'] = name
        self.user_data['updated_at'] = datetime.now()
        self.save_user_data()
    
    def get_preference(self, key, default=None):
        """Tercih değerini getir"""
        return self.user_data['preferences'].get(key, default)
        
    def set_preference(self, key, value):
        """Tercih değerini ayarla"""
        self.user_data['preferences'][key] = value
        self.user_data['updated_at'] = datetime.now()
        self.save_user_data()
    
    def get_all_preferences(self):
        """Tüm tercihleri getir"""
        return self.user_data['preferences'].copy()
        
    def update_preferences(self, new_preferences):
        """Tercihleri güncelle"""
        self.user_data['preferences'].update(new_preferences)
        self.user_data['updated_at'] = datetime.now()
        self.save_user_data()
    
    def get_usage_patterns(self):
        """Kullanım kalıplarını analiz et"""
        stats = self.db.get_app_usage_stats(7)  # Son 7 gün
        
        patterns = {
            'most_used_apps': [],
            'total_usage_time': 0,
            'average_session_length': 0,
            'peak_usage_hours': []
        }
        
        if stats:
            # En çok kullanılan uygulamalar
            patterns['most_used_apps'] = [
                {'name': app[0], 'duration': app[2], 'count': app[1]} 
                for app in stats[:5]
            ]
            
            # Toplam kullanım süresi
            patterns['total_usage_time'] = sum(app[2] for app in stats)
            
            # Ortalama oturum süresi
            total_sessions = sum(app[1] for app in stats)
            if total_sessions > 0:
                patterns['average_session_length'] = patterns['total_usage_time'] / total_sessions
                
        return patterns
        
    def get_productivity_score(self):
        """Üretkenlik skorunu hesapla"""
        patterns = self.get_usage_patterns()
        
        # Basit üretkenlik hesaplama
        productive_apps = ['code', 'word', 'excel', 'powerpoint', 'notepad', 'vscode']
        productive_time = 0
        total_time = patterns['total_usage_time']
        
        for app in patterns['most_used_apps']:
            if any(prod_app in app['name'].lower() for prod_app in productive_apps):
                productive_time += app['duration']
                
        if total_time > 0:
            return (productive_time / total_time) * 100
        else:
            return 0
            
    def get_recommendations(self):
        """Kullanıcı için öneriler oluştur"""
        recommendations = []
        patterns = self.get_usage_patterns()
        productivity_score = self.get_productivity_score()
        
        # Uzun süreli kullanım uyarısı
        if patterns['total_usage_time'] > 8 * 3600:  # 8 saat
            recommendations.append("Günlük ekran kullanım süreniz yüksek. Göz sağlığınız için mola verin.")
        
        # Düşük üretkenlik uyarısı
        if productivity_score < 30:
            recommendations.append("Üretkenlik skorunuz düşük. Daha fazla çalışma uygulaması kullanmayı deneyin.")
            
        # Uzun oturum uyarısı
        if patterns['average_session_length'] > 2 * 3600:  # 2 saat
            recommendations.append("Ortalama oturum süreniz uzun. Düzenli molalar almayı unutmayın.")
            
        return recommendations 