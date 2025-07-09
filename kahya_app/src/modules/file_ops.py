import os
import subprocess
import platform
from pathlib import Path

class FileOperations:
    def __init__(self):
        self.system = platform.system().lower()
        
    def open_file(self, file_path):
        """Dosyayı varsayılan uygulamayla aç"""
        try:
            if not os.path.exists(file_path):
                return False
                
            if self.system == "windows":
                os.startfile(file_path)
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            return True
        except Exception as e:
            print(f"Dosya açma hatası: {e}")
            return False
            
    def open_folder(self, folder_path):
        """Klasörü dosya yöneticisinde aç"""
        try:
            if not os.path.exists(folder_path):
                return False
                
            if self.system == "windows":
                subprocess.run(["explorer", folder_path])
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
                
            return True
        except Exception as e:
            print(f"Klasör açma hatası: {e}")
            return False
            
    def create_file(self, file_path, content=""):
        """Dosya oluştur"""
        try:
            # Klasör yapısını oluştur
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Dosya oluşturma hatası: {e}")
            return False
            
    def delete_file(self, file_path):
        """Dosya sil"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Dosya silme hatası: {e}")
            return False
            
    def copy_file(self, source_path, dest_path):
        """Dosya kopyala"""
        try:
            import shutil
            shutil.copy2(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Dosya kopyalama hatası: {e}")
            return False
            
    def move_file(self, source_path, dest_path):
        """Dosya taşı"""
        try:
            import shutil
            shutil.move(source_path, dest_path)
            return True
        except Exception as e:
            print(f"Dosya taşıma hatası: {e}")
            return False
            
    def get_file_info(self, file_path):
        """Dosya bilgilerini getir"""
        try:
            if not os.path.exists(file_path):
                return None
                
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path)
            }
        except Exception as e:
            print(f"Dosya bilgi alma hatası: {e}")
            return None
            
    def list_directory(self, dir_path):
        """Klasör içeriğini listele"""
        try:
            if not os.path.exists(dir_path):
                return []
                
            items = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                info = self.get_file_info(item_path)
                if info:
                    items.append({
                        'name': item,
                        'path': item_path,
                        **info
                    })
            return items
        except Exception as e:
            print(f"Klasör listeleme hatası: {e}")
            return []
            
    def search_files_in_directory(self, dir_path, pattern):
        """Klasörde dosya ara"""
        try:
            import glob
            search_pattern = os.path.join(dir_path, f"*{pattern}*")
            return glob.glob(search_pattern)
        except Exception as e:
            print(f"Dosya arama hatası: {e}")
            return []
            
    def get_desktop_path(self):
        """Masaüstü yolunu getir"""
        try:
            if self.system == "windows":
                return os.path.join(os.path.expanduser("~"), "Desktop")
            elif self.system == "darwin":  # macOS
                return os.path.join(os.path.expanduser("~"), "Desktop")
            else:  # Linux
                return os.path.join(os.path.expanduser("~"), "Desktop")
        except Exception as e:
            print(f"Masaüstü yolu alma hatası: {e}")
            return os.path.expanduser("~")
            
    def get_documents_path(self):
        """Belgeler klasörü yolunu getir"""
        try:
            if self.system == "windows":
                return os.path.join(os.path.expanduser("~"), "Documents")
            elif self.system == "darwin":  # macOS
                return os.path.join(os.path.expanduser("~"), "Documents")
            else:  # Linux
                return os.path.join(os.path.expanduser("~"), "Documents")
        except Exception as e:
            print(f"Belgeler yolu alma hatası: {e}")
            return os.path.expanduser("~")
            
    def create_backup(self, file_path):
        """Dosya yedeği oluştur"""
        try:
            if not os.path.exists(file_path):
                return False
                
            backup_path = f"{file_path}.backup"
            return self.copy_file(file_path, backup_path)
        except Exception as e:
            print(f"Yedek oluşturma hatası: {e}")
            return False 