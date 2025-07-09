from src.core.database import Database

class TodoManager:
    def __init__(self, db_path):
        self.db = Database(db_path)
        
    def add_todo(self, title, description="", priority=1):
        """Todo ekle"""
        try:
            self.db.add_todo(title, description, priority)
            return True
        except Exception as e:
            print(f"Todo ekleme hatası: {e}")
            return False
            
    def get_todos(self, completed=None):
        """Todoları getir"""
        try:
            return self.db.get_todos(completed)
        except Exception as e:
            print(f"Todo getirme hatası: {e}")
            return []
            
    def get_active_todos(self):
        """Aktif todoları getir"""
        return self.get_todos(completed=False)
        
    def get_completed_todos(self):
        """Tamamlanmış todoları getir"""
        return self.get_todos(completed=True)
        
    def complete_todo(self, todo_id):
        """Todo'yu tamamla"""
        try:
            self.db.update_todo(todo_id, completed=True)
            return True
        except Exception as e:
            print(f"Todo tamamlama hatası: {e}")
            return False
            
    def uncomplete_todo(self, todo_id):
        """Todo'yu tamamlanmamış yap"""
        try:
            self.db.update_todo(todo_id, completed=False)
            return True
        except Exception as e:
            print(f"Todo geri alma hatası: {e}")
            return False
            
    def update_todo(self, todo_id, **kwargs):
        """Todo güncelle"""
        try:
            self.db.update_todo(todo_id, **kwargs)
            return True
        except Exception as e:
            print(f"Todo güncelleme hatası: {e}")
            return False
            
    def delete_todo(self, todo_id):
        """Todo sil"""
        try:
            self.db.delete_todo(todo_id)
            return True
        except Exception as e:
            print(f"Todo silme hatası: {e}")
            return False
            
    def get_todo_by_id(self, todo_id):
        """ID'ye göre todo getir"""
        try:
            todos = self.db.execute_query("SELECT * FROM todos WHERE id = ?", (todo_id,))
            return todos[0] if todos else None
        except Exception as e:
            print(f"Todo getirme hatası: {e}")
            return None
            
    def get_todos_by_priority(self, priority):
        """Önceliğe göre todoları getir"""
        try:
            return self.db.execute_query(
                "SELECT * FROM todos WHERE priority = ? ORDER BY created_at DESC",
                (priority,)
            )
        except Exception as e:
            print(f"Öncelikli todo getirme hatası: {e}")
            return []
            
    def get_todo_stats(self):
        """Todo istatistiklerini getir"""
        try:
            total = self.db.execute_query("SELECT COUNT(*) FROM todos")[0][0]
            completed = self.db.execute_query("SELECT COUNT(*) FROM todos WHERE completed = 1")[0][0]
            active = total - completed
            
            return {
                'total': total,
                'completed': completed,
                'active': active,
                'completion_rate': (completed / total * 100) if total > 0 else 0
            }
        except Exception as e:
            print(f"Todo istatistik hatası: {e}")
            return {'total': 0, 'completed': 0, 'active': 0, 'completion_rate': 0}
            
    def search_todos(self, query):
        """Todo ara"""
        try:
            return self.db.execute_query(
                "SELECT * FROM todos WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC",
                (f"%{query}%", f"%{query}%")
            )
        except Exception as e:
            print(f"Todo arama hatası: {e}")
            return []
            
    def clear_completed_todos(self):
        """Tamamlanmış todoları temizle"""
        try:
            self.db.execute_query("DELETE FROM todos WHERE completed = 1")
            return True
        except Exception as e:
            print(f"Tamamlanmış todo temizleme hatası: {e}")
            return False 