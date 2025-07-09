import os
import glob
import fnmatch
from pathlib import Path

class FileSearch:
    def __init__(self):
        self.search_paths = [
            os.path.expanduser("~"),  # Kullanıcı klasörü
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        
    def search_files(self, query, max_results=20):
        """Dosya ara"""
        results = []
        query_lower = query.lower()
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                # Recursive arama
                for root, dirs, files in os.walk(search_path):
                    # Dosya adlarında ara
                    for file in files:
                        if query_lower in file.lower():
                            file_path = os.path.join(root, file)
                            results.append(file_path)
                            if len(results) >= max_results:
                                return results
                                
                    # Klasör adlarında ara
                    for dir_name in dirs:
                        if query_lower in dir_name.lower():
                            dir_path = os.path.join(root, dir_name)
                            results.append(dir_path)
                            if len(results) >= max_results:
                                return results
                                
            except (PermissionError, OSError):
                # Erişim izni yoksa atla
                continue
                
        return results
        
    def search_by_extension(self, extension, max_results=20):
        """Uzantıya göre dosya ara"""
        results = []
        extension = extension.lower()
        if not extension.startswith('.'):
            extension = '.' + extension
            
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                pattern = os.path.join(search_path, f"**/*{extension}")
                files = glob.glob(pattern, recursive=True)
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        results.append(file_path)
                        if len(results) >= max_results:
                            return results
                            
            except (PermissionError, OSError):
                continue
                
        return results
        
    def search_by_pattern(self, pattern, max_results=20):
        """Pattern'e göre dosya ara"""
        results = []
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if fnmatch.fnmatch(file.lower(), pattern.lower()):
                            file_path = os.path.join(root, file)
                            results.append(file_path)
                            if len(results) >= max_results:
                                return results
                                
            except (PermissionError, OSError):
                continue
                
        return results
        
    def search_recent_files(self, days=7, max_results=20):
        """Son kullanılan dosyaları ara"""
        import time
        results = []
        cutoff_time = time.time() - (days * 24 * 3600)
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            mtime = os.path.getmtime(file_path)
                            if mtime > cutoff_time:
                                results.append((file_path, mtime))
                        except (OSError, PermissionError):
                            continue
                            
            except (PermissionError, OSError):
                continue
                
        # Zaman sırasına göre sırala
        results.sort(key=lambda x: x[1], reverse=True)
        return [path for path, _ in results[:max_results]]
        
    def search_large_files(self, min_size_mb=10, max_results=20):
        """Büyük dosyaları ara"""
        results = []
        min_size_bytes = min_size_mb * 1024 * 1024
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            if size > min_size_bytes:
                                results.append((file_path, size))
                        except (OSError, PermissionError):
                            continue
                            
            except (PermissionError, OSError):
                continue
                
        # Boyut sırasına göre sırala
        results.sort(key=lambda x: x[1], reverse=True)
        return [path for path, _ in results[:max_results]]
        
    def get_file_info(self, file_path):
        """Dosya hakkında detaylı bilgi getir"""
        try:
            if not os.path.exists(file_path):
                return None
                
            stat = os.stat(file_path)
            size = stat.st_size
            
            # Boyutu formatla
            size_str = self._format_size(size)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': size_str,
                'size_bytes': size,
                'modified': stat.st_mtime,
                'is_file': os.path.isfile(file_path),
                'is_dir': os.path.isdir(file_path),
                'extension': os.path.splitext(file_path)[1] if os.path.isfile(file_path) else ''
            }
        except Exception as e:
            print(f"Dosya bilgi alma hatası: {e}")
            return None
            
    def _format_size(self, size_bytes):
        """Boyutu okunabilir formata çevir"""
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"
        
    def add_search_path(self, path):
        """Arama yoluna yeni klasör ekle"""
        if os.path.exists(path) and path not in self.search_paths:
            self.search_paths.append(path)
            
    def remove_search_path(self, path):
        """Arama yolundan klasör çıkar"""
        if path in self.search_paths:
            self.search_paths.remove(path)
            
    def get_search_paths(self):
        """Mevcut arama yollarını getir"""
        return self.search_paths.copy() 