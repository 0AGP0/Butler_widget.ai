# Kahya AI Desktop Assistant

Fallout Pip-Boy tarzı retro tam ekran şeffaf duvar kağıdı widget'ı olan Kahya AI Desktop Assistant.

## Özellikler

### 🎨 Retro Tasarım
- Fallout Pip-Boy tarzı yeşil terminal görünümü
- Pixel-art animasyonlu Kahya yüzü
- Retro dijital saat ve takvim
- Scan line efektleri ve glow animasyonları

### 🤖 AI Asistan
- LLM entegrasyonu (OpenAI GPT-3.5-turbo)
- Doğal dil komut işleme
- Threading ile arka plan işleme
- "Kahya yazıyor..." animasyonu

### 📝 Todo Yönetimi
- Retro todo listesi
- Gerçek zamanlı güncelleme
- Tamamlama/silme işlemleri
- İstatistik takibi

### 🎤 Ses Analizi
- Gerçek zamanlı mikrofon girişi
- FFT analizi ile ses dalgası görselleştirme
- Simülasyon modu (mikrofon yoksa)
- Peak seviyesi göstergesi

### 📅 Takvim ve Saat
- Retro dijital saat
- Güncel takvim görünümü
- Bugün vurgulaması
- Yılın günü ve hafta bilgisi

### 🖥️ Sistem Entegrasyonu
- Tam ekran şeffaf duvar kağıdı
- Sistem tray entegrasyonu
- Kısayol tuşları (ESC, F11, M)
- Sağ tık menüsü

### 📊 Kullanım Takibi
- Uygulama kullanım istatistikleri
- Üretkenlik skoru hesaplama
- Kullanım kalıpları analizi
- Akıllı öneriler

## Kurulum

### Gereksinimler
```bash
Python 3.8+
PyQt5
requests
numpy
pyaudio (opsiyonel)
scipy (opsiyonel)
psutil
python-dateutil
```

### Kurulum Adımları
1. Projeyi klonlayın:
```bash
git clone <repository-url>
cd kahya_app
```

2. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

3. (Opsiyonel) OpenAI API anahtarını ayarlayın:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

4. Uygulamayı çalıştırın:
```bash
python src/main.py
```

## Kullanım

### Temel Kontroller
- **ESC**: Gizle/Göster
- **F11**: Tam ekran modu
- **M**: Mikrofonu aç/kapat
- **Sağ Tık**: Bağlam menüsü

### Sistem Tray
- Sistem tray ikonuna sağ tıklayarak menüye erişin
- Gizle/Göster, mikrofon kontrolü ve çıkış seçenekleri

### Komutlar
Chatbox'ta şu komutları kullanabilirsiniz:

#### Todo Komutları
- `todo ekle [görev]` - Yeni todo ekle
- `todo listele` - Todoları listele
- `todo tamamla [id]` - Todo'yu tamamla
- `todo sil [id]` - Todo'yu sil

#### Hatırlatıcı Komutları
- `hatırlat [mesaj] saat [saat]:[dakika]` - Hatırlatıcı ekle
- `hatırlatıcı listele` - Hatırlatıcıları listele

#### Dosya Komutları
- `dosya ara [arama]` - Dosya ara
- `dosya aç [yol]` - Dosya aç

#### Tarayıcı Komutları
- `tarayıcı aç [url]` - URL'yi tarayıcıda aç

#### Sistem Komutları
- `uygulama aç [uygulama]` - Uygulama aç
- `klasör aç [yol]` - Klasör aç

## Proje Yapısı

```
kahya_app/
├── src/
│   ├── main.py                 # Ana uygulama
│   │   ├── core/
│   │   │   ├── database.py         # Veritabanı yönetimi
│   │   │   ├── command_router.py   # Komut yönlendirici
│   │   │   └── llm_client.py       # LLM istemci
│   │   ├── modules/
│   │   │   ├── todo.py             # Todo yönetimi
│   │   │   ├── reminder.py         # Hatırlatıcı yönetimi
│   │   │   ├── file_ops.py         # Dosya işlemleri
│   │   │   ├── file_search.py      # Dosya arama
│   │   │   ├── browser_control.py  # Tarayıcı kontrolü
│   │   │   ├── os_control.py       # İşletim sistemi kontrolü
│   │   │   ├── usage_tracker.py    # Kullanım takibi
│   │   │   └── user_model.py       # Kullanıcı modeli
│   │   └── ui/
│   │       ├── kahya_wallpaper.py  # Ana wallpaper
│   │       └── retro_components/   # Retro bileşenler
│   │           ├── kahya_face.py   # Kahya yüzü
│   │           ├── retro_clock.py  # Retro saat
│   │           ├── retro_todo.py   # Retro todo
│   │           ├── retro_calendar.py # Retro takvim
│   │           ├── retro_chatbox.py # Retro chatbox
│   │           └── sound_wave.py   # Ses dalgası
│   ├── data/
│   │   └── kahya.db               # SQLite veritabanı
│   ├── requirements.txt           # Python bağımlılıkları
│   └── README.md                 # Bu dosya
```

## Özelleştirme

### Renk Teması
Retro bileşenlerde renkleri değiştirmek için ilgili dosyalardaki `QColor` değerlerini düzenleyin.

### Animasyon Hızları
Animasyon zamanlayıcılarını `QTimer.start()` değerlerini değiştirerek ayarlayabilirsiniz.

### Mikrofon Ayarları
`sound_wave.py` dosyasında mikrofon parametrelerini düzenleyebilirsiniz.

## Sorun Giderme

### Mikrofon Çalışmıyor
- PyAudio ve scipy paketlerinin yüklü olduğundan emin olun
- Mikrofon izinlerini kontrol edin
- Simülasyon modu otomatik olarak devreye girer

### LLM Yanıt Vermiyor
- OpenAI API anahtarının doğru ayarlandığından emin olun
- İnternet bağlantısını kontrol edin
- API anahtarı yoksa basit yanıtlar verilir

### Performans Sorunları
- Animasyon hızlarını azaltın
- Gereksiz bileşenleri devre dışı bırakın
- Sistem kaynaklarını kontrol edin

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## İletişim

Sorularınız için issue açabilir veya pull request gönderebilirsiniz.

---

**Not**: Bu proje eğitim amaçlı geliştirilmiştir. Gerçek kullanımda güvenlik ve gizlilik konularına dikkat edin. 