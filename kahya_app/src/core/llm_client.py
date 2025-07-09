import requests
import json
import os
import random
from datetime import datetime

class LLMClient:
    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/generate"
        
        # Eğer Ollama çalışmıyorsa, basit yanıtlar ver
        self.fallback_responses = [
            "Anlıyorum, size nasıl yardımcı olabilirim?",
            "Bu konuda daha fazla bilgi verebilir misiniz?",
            "İlginç bir soru. Bunu araştırmaya değer.",
            "Bu konuda size yardımcı olmaya çalışayım.",
            "Anladım, devam edin lütfen.",
            "Bu konuda ne düşünüyorsunuz?",
            "Size nasıl yardımcı olabilirim?",
            "Bu konuda daha detaylı bilgi verebilir misiniz?",
            "Anlıyorum, başka bir şey sormak ister misiniz?",
            "Bu konuda size rehberlik edebilirim."
        ]
        
    def get_response(self, message):
        """LLM'den yanıt al"""
        if not self.is_available():
            return self._get_fallback_response(message)
            
        try:
            # Ollama API formatı
            system_prompt = """Sen Kahya adında yardımcı bir AI asistanısın. 
            Kullanıcıya Türkçe olarak yanıt ver. 
            Kısa, öz ve yardımcı ol.
            
            ÖNEMLİ: Eğer kullanıcı aşağıdaki işlemlerden birini istiyorsa, 
            sadece işlemi gerçekleştir ve kısa bir onay mesajı ver:
            
            HATIRLATICI İŞLEMLERİ:
            - "20 sinde sınav var" → Hatırlatıcı ekle
            - "cumartesi piknik var" → Hatırlatıcı ekle  
            - "yarın 14:30 toplantı" → Hatırlatıcı ekle
            - "bu ayın 15'inde doğum günü" → Hatırlatıcı ekle
            
            NOT ALMA İŞLEMLERİ:
            - "not al bu önemli" → Not kaydet
            - "kaydet alışveriş listesi" → Not kaydet
            - "yaz önemli bilgi" → Not kaydet
            
            TODO İŞLEMLERİ:
            - "yapılacak alışveriş yap" → Todo ekle
            - "görev ev temizliği" → Todo ekle
            
            LİSTELEME İŞLEMLERİ:
            - "hatırlatıcılarım" → Hatırlatıcıları listele
            - "notlarım" → Notları listele
            - "yapılacaklarım" → Todo'ları listele
            
            Eğer bu işlemlerden biri değilse, normal sohbet yanıtı ver."""
            
            full_prompt = f"{system_prompt}\n\nKullanıcı: {message}\nKahya:"
            
            data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "num_predict": 200,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(self.api_url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Yanıt alınamadı").strip()
            else:
                return f"Ollama API hatası: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return "Yanıt zaman aşımına uğradı. Ollama servisinin çalıştığından emin olun."
        except requests.exceptions.ConnectionError:
            return "Ollama servisine bağlanılamadı. Ollama'nın çalıştığından emin olun."
        except requests.exceptions.RequestException as e:
            return f"Bağlantı hatası: {str(e)}"
        except Exception as e:
            return f"Beklenmeyen hata: {str(e)}"
            
    def _get_fallback_response(self, message):
        """Ollama çalışmıyorsa basit yanıt ver"""
        return random.choice(self.fallback_responses)
        
    def is_available(self):
        """Ollama servisinin kullanılabilir olup olmadığını kontrol et"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Kullanılabilir modelleri listele"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                result = response.json()
                return [model["name"] for model in result.get("models", [])]
            return []
        except:
            return []
        
    def test_connection(self):
        """Ollama bağlantısını test et"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return True, "Ollama servisi çalışıyor"
            else:
                return False, f"Ollama servisi hatası: {response.status_code}"
        except Exception as e:
            return False, f"Ollama bağlantı hatası: {str(e)}"
    
    def analyze_and_process_command(self, message, command_router):
        """LLM yanıtını analiz edip komutları işle"""
        try:
            # LLM'den yanıt al
            llm_response = self.get_response(message)
            
            # LLM yanıtında komut işaretleri var mı kontrol et
            if any(keyword in llm_response.lower() for keyword in [
                'hatırlatıcı eklendi', 'not kaydedildi', 'todo eklendi', 
                'hatırlatıcılar', 'notlar', 'yapılacaklar'
            ]):
                # LLM komut işlemi yapmış, yanıtı döndür
                return llm_response, True
            
            # LLM komut işlemi yapmamış, chatbox'ın komut algılama sistemini kullan
            return llm_response, False
            
        except Exception as e:
            return f"LLM analiz hatası: {str(e)}", False 