import subprocess
import platform
import os
import psutil
import time

class OSControl:
    def __init__(self):
        self.system = platform.system().lower()
        
    def open_application(self, app_name):
        """Uygulamayı aç"""
        try:
            app_name = app_name.lower()
            
            # Yaygın uygulamalar
            common_apps = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "wordpad": "wordpad.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "control panel": "control.exe",
                "task manager": "taskmgr.exe",
                "regedit": "regedit.exe",
                "msconfig": "msconfig.exe",
                "disk cleanup": "cleanmgr.exe",
                "defragment": "dfrgui.exe",
                "system restore": "rstrui.exe",
                "device manager": "devmgmt.msc",
                "services": "services.msc",
                "event viewer": "eventvwr.msc",
                "computer management": "compmgmt.msc"
            }
            
            if app_name in common_apps:
                subprocess.Popen(common_apps[app_name])
                return True
            else:
                # Uygulama adını doğrudan çalıştırmayı dene
                subprocess.Popen(app_name)
                return True
                
        except Exception as e:
            print(f"Uygulama açma hatası: {e}")
            return False
            
    def open_folder(self, folder_path):
        """Klasörü aç"""
        try:
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
            
    def shutdown_system(self, delay_minutes=0):
        """Sistemi kapat"""
        try:
            if self.system == "windows":
                if delay_minutes > 0:
                    subprocess.run(["shutdown", "/s", "/t", str(delay_minutes * 60)])
                else:
                    subprocess.run(["shutdown", "/s", "/t", "0"])
            elif self.system == "darwin":  # macOS
                if delay_minutes > 0:
                    subprocess.run(["sudo", "shutdown", "-h", "+" + str(delay_minutes)])
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "now"])
            else:  # Linux
                if delay_minutes > 0:
                    subprocess.run(["sudo", "shutdown", "-h", "+" + str(delay_minutes)])
                else:
                    subprocess.run(["sudo", "shutdown", "-h", "now"])
            return True
        except Exception as e:
            print(f"Sistem kapatma hatası: {e}")
            return False
            
    def restart_system(self, delay_minutes=0):
        """Sistemi yeniden başlat"""
        try:
            if self.system == "windows":
                if delay_minutes > 0:
                    subprocess.run(["shutdown", "/r", "/t", str(delay_minutes * 60)])
                else:
                    subprocess.run(["shutdown", "/r", "/t", "0"])
            elif self.system == "darwin":  # macOS
                if delay_minutes > 0:
                    subprocess.run(["sudo", "shutdown", "-r", "+" + str(delay_minutes)])
                else:
                    subprocess.run(["sudo", "shutdown", "-r", "now"])
            else:  # Linux
                if delay_minutes > 0:
                    subprocess.run(["sudo", "shutdown", "-r", "+" + str(delay_minutes)])
                else:
                    subprocess.run(["sudo", "shutdown", "-r", "now"])
            return True
        except Exception as e:
            print(f"Sistem yeniden başlatma hatası: {e}")
            return False
            
    def cancel_shutdown(self):
        """Kapatma işlemini iptal et"""
        try:
            if self.system == "windows":
                subprocess.run(["shutdown", "/a"])
            elif self.system == "darwin":  # macOS
                subprocess.run(["sudo", "killall", "shutdown"])
            else:  # Linux
                subprocess.run(["sudo", "shutdown", "-c"])
            return True
        except Exception as e:
            print(f"Kapatma iptal hatası: {e}")
            return False
            
    def get_system_info(self):
        """Sistem bilgilerini getir"""
        try:
            info = {
                'os': platform.system(),
                'os_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'hostname': platform.node(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent if self.system != "windows" else psutil.disk_usage('C:\\').percent
            }
            return info
        except Exception as e:
            print(f"Sistem bilgi alma hatası: {e}")
            return None
            
    def get_running_processes(self, limit=20):
        """Çalışan işlemleri getir"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # CPU kullanımına göre sırala
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:limit]
        except Exception as e:
            print(f"İşlem listesi alma hatası: {e}")
            return []
            
    def kill_process(self, process_name):
        """İşlemi sonlandır"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    proc.terminate()
                    return True
            return False
        except Exception as e:
            print(f"İşlem sonlandırma hatası: {e}")
            return False
            
    def get_network_info(self):
        """Ağ bilgilerini getir"""
        try:
            network_info = {}
            
            # Ağ bağlantıları
            connections = psutil.net_connections()
            network_info['connections'] = len(connections)
            
            # Ağ istatistikleri
            net_io = psutil.net_io_counters()
            network_info['bytes_sent'] = net_io.bytes_sent
            network_info['bytes_recv'] = net_io.bytes_recv
            
            # IP adresleri
            addrs = psutil.net_if_addrs()
            network_info['interfaces'] = list(addrs.keys())
            
            return network_info
        except Exception as e:
            print(f"Ağ bilgi alma hatası: {e}")
            return None
            
    def set_volume(self, volume_percent):
        """Ses seviyesini ayarla"""
        try:
            if self.system == "windows":
                # Windows için PowerShell komutu
                cmd = f'(New-Object -ComObject WScript.Shell).SendKeys([char]173); (Get-AudioDevice -Playback).volume = {volume_percent}'
                subprocess.run(["powershell", "-Command", cmd])
            elif self.system == "darwin":  # macOS
                subprocess.run(["osascript", "-e", f"set volume output volume {volume_percent}"])
            else:  # Linux
                subprocess.run(["amixer", "set", "Master", f"{volume_percent}%"])
            return True
        except Exception as e:
            print(f"Ses seviyesi ayarlama hatası: {e}")
            return False
            
    def mute_audio(self):
        """Sesi kapat"""
        try:
            if self.system == "windows":
                subprocess.run(["powershell", "-Command", "(Get-AudioDevice -Playback).volume = 0"])
            elif self.system == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume 0"])
            else:  # Linux
                subprocess.run(["amixer", "set", "Master", "mute"])
            return True
        except Exception as e:
            print(f"Ses kapatma hatası: {e}")
            return False
            
    def unmute_audio(self):
        """Sesi aç"""
        try:
            if self.system == "windows":
                subprocess.run(["powershell", "-Command", "(Get-AudioDevice -Playback).volume = 50"])
            elif self.system == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume 50"])
            else:  # Linux
                subprocess.run(["amixer", "set", "Master", "unmute"])
            return True
        except Exception as e:
            print(f"Ses açma hatası: {e}")
            return False 