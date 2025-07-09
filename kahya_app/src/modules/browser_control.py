import webbrowser
import subprocess
import platform
import os

class BrowserControl:
    def __init__(self):
        self.system = platform.system().lower()
        self.default_browser = self._get_default_browser()
        
    def _get_default_browser(self):
        """Varsayılan tarayıcıyı tespit et"""
        try:
            if self.system == "windows":
                # Windows'ta varsayılan tarayıcıyı al
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                    browser = winreg.QueryValueEx(key, "ProgId")[0]
                    return browser
            else:
                # Linux/macOS için basit tespit
                return "default"
        except:
            return "default"
            
    def open_url(self, url):
        """URL'yi varsayılan tarayıcıda aç"""
        try:
            # URL'yi düzelt
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"URL açma hatası: {e}")
            return False
            
    def open_url_in_browser(self, url, browser_name):
        """URL'yi belirli bir tarayıcıda aç"""
        try:
            # URL'yi düzelt
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            browser_name = browser_name.lower()
            
            if browser_name in ['chrome', 'google chrome']:
                return self._open_in_chrome(url)
            elif browser_name in ['firefox', 'mozilla']:
                return self._open_in_firefox(url)
            elif browser_name in ['edge', 'microsoft edge']:
                return self._open_in_edge(url)
            elif browser_name in ['safari']:
                return self._open_in_safari(url)
            else:
                # Varsayılan tarayıcıda aç
                return self.open_url(url)
                
        except Exception as e:
            print(f"Tarayıcıda URL açma hatası: {e}")
            return False
            
    def _open_in_chrome(self, url):
        """Chrome'da aç"""
        try:
            if self.system == "windows":
                subprocess.run(["chrome", url], check=True)
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", "-a", "Google Chrome", url], check=True)
            else:  # Linux
                subprocess.run(["google-chrome", url], check=True)
            return True
        except:
            # Chrome bulunamadıysa varsayılan tarayıcıda aç
            return self.open_url(url)
            
    def _open_in_firefox(self, url):
        """Firefox'ta aç"""
        try:
            if self.system == "windows":
                subprocess.run(["firefox", url], check=True)
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", "-a", "Firefox", url], check=True)
            else:  # Linux
                subprocess.run(["firefox", url], check=True)
            return True
        except:
            return self.open_url(url)
            
    def _open_in_edge(self, url):
        """Edge'de aç"""
        try:
            if self.system == "windows":
                subprocess.run(["msedge", url], check=True)
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", "-a", "Microsoft Edge", url], check=True)
            else:  # Linux
                subprocess.run(["microsoft-edge", url], check=True)
            return True
        except:
            return self.open_url(url)
            
    def _open_in_safari(self, url):
        """Safari'de aç"""
        try:
            if self.system == "darwin":  # macOS
                subprocess.run(["open", "-a", "Safari", url], check=True)
                return True
            else:
                return self.open_url(url)
        except:
            return self.open_url(url)
            
    def search_web(self, query, search_engine="google"):
        """Web'de arama yap"""
        search_engines = {
            "google": "https://www.google.com/search?q={}",
            "bing": "https://www.bing.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "youtube": "https://www.youtube.com/results?search_query={}",
            "wikipedia": "https://en.wikipedia.org/wiki/{}"
        }
        
        if search_engine.lower() in search_engines:
            url = search_engines[search_engine.lower()].format(query)
            return self.open_url(url)
        else:
            # Varsayılan olarak Google'da ara
            url = search_engines["google"].format(query)
            return self.open_url(url)
            
    def open_common_sites(self, site_name):
        """Yaygın siteleri aç"""
        common_sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://www.reddit.com",
            "wikipedia": "https://www.wikipedia.org",
            "amazon": "https://www.amazon.com",
            "ebay": "https://www.ebay.com",
            "netflix": "https://www.netflix.com",
            "spotify": "https://open.spotify.com",
            "gmail": "https://mail.google.com",
            "outlook": "https://outlook.live.com",
            "yahoo": "https://mail.yahoo.com"
        }
        
        site_name = site_name.lower()
        if site_name in common_sites:
            return self.open_url(common_sites[site_name])
        else:
            return False
            
    def get_available_browsers(self):
        """Mevcut tarayıcıları listele"""
        browsers = []
        
        # Windows
        if self.system == "windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ]
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    browsers.append("Chrome")
                    break
                    
            for path in firefox_paths:
                if os.path.exists(path):
                    browsers.append("Firefox")
                    break
                    
            for path in edge_paths:
                if os.path.exists(path):
                    browsers.append("Edge")
                    break
                    
        # macOS
        elif self.system == "darwin":
            browsers = ["Safari", "Chrome", "Firefox", "Edge"]
            
        # Linux
        else:
            browsers = ["Chrome", "Firefox", "Edge"]
            
        return browsers 