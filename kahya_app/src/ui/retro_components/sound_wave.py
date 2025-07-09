import numpy as np
import sounddevice as sd
import threading, time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient

class SoundWave(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 180)

        # --- Parametreler ---
        self.num_bands         = 32
        self.fft_size          = 1024
        self.sample_rate       = 44100
        self.attack_rate       = 0.8
        self.release_rate      = 0.2
        self.silence_threshold = 1e-4
        self.peak_decay        = 0.9995  # Çok yavaş decay

        # --- Durum ---
        self.buffer    = np.zeros(self.fft_size, dtype=np.float32)
        self.envelope  = np.zeros(self.num_bands, dtype=np.float32)
        self.target    = np.zeros(self.num_bands, dtype=np.float32)
        # Başlangıçta düşük ama sabit bir değer
        self.peaks     = np.full(self.num_bands, 1.0, dtype=np.float32)
        self.phase     = 0.0
        self.is_listening = False  # Mikrofon dinleme durumu

        # --- FFT frekans ekseni ve eşit bant indeksleri ---
        self.freqs = np.fft.rfftfreq(self.fft_size, 1/self.sample_rate)
        all_idx = np.arange(len(self.freqs))
        splits  = np.array_split(all_idx, self.num_bands)
        self.band_indices = [idx for idx in splits]

        # --- Cihaz seçimi (VB-Cable Output) ---
        self.device = next((i for i,d in enumerate(sd.query_devices())
                            if "CABLE Output" in d['name'] and d['max_input_channels']>0), None)
        if self.device is None:
            raise RuntimeError("VB-Cable Output bulunamadı")

        # --- UI Timer & Audio Thread ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(16)
        threading.Thread(target=self._audio_loop, daemon=True).start()

    def _audio_callback(self, indata, frames, t, status):
        self.buffer = indata[:,0]

    def _audio_loop(self):
        stream = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.sample_rate,
            blocksize=self.fft_size,
            callback=self._audio_callback
        )
        with stream:
            while True:
                buf = self.buffer * np.hanning(len(self.buffer))
                rms = np.sqrt(np.mean(buf**2))

                if rms < self.silence_threshold:
                    self.target.fill(2.0)
                else:
                    mag = np.abs(np.fft.rfft(buf))
                    vals = np.empty(self.num_bands, dtype=np.float32)
                    for i, idx in enumerate(self.band_indices):
                        vals[i] = mag[idx].mean()
                    # Önce yeni peak'leri al
                    self.peaks = np.maximum(self.peaks, vals)
                    # Hedef yükseklik: oran * pencere yüksekliği
                    h = self.height() - 20
                    self.target = (vals / self.peaks) * h

                time.sleep(1/60)

    def _update(self):
        self.phase += 0.003
        # Peak decay burada uygulanıyor çok yavaş
        self.peaks *= self.peak_decay

        for i in range(self.num_bands):
            t = self.target[i]
            e = self.envelope[i]
            if t > e:
                e += (t - e) * self.attack_rate
            else:
                e += (t - e) * self.release_rate
            self.envelope[i] = e

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor(10, 10, 20))

        spacing = 1
        bar_w = int((w - 20 - spacing*(self.num_bands-1)) / self.num_bands)

        for i, e_val in enumerate(self.envelope):
            x = 10 + i * (bar_w + spacing)
            y = h - int(e_val) - 10

            col = QColor.fromHsvF((self.phase + i/self.num_bands) % 1, 1, 1)
            grad = QLinearGradient(x, y, x, y + e_val)
            grad.setColorAt(0.0, col.lighter(140))
            grad.setColorAt(1.0, col.darker(200))

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_w, int(e_val), 3, 3)

        painter.setPen(QPen(QColor(180, 255, 200), 1))
        painter.drawText(12, 18, "Ses Spektrum — Stabil Peak Tracking")

    def cleanup(self):
        self.timer.stop()
    
    def toggle_listening(self):
        """Mikrofon dinleme durumunu değiştir"""
        self.is_listening = not self.is_listening
        return self.is_listening
    
    def start_listening(self):
        """Mikrofon dinlemeyi başlat"""
        self.is_listening = True
    
    def stop_listening(self):
        """Mikrofon dinlemeyi durdur"""
        self.is_listening = False
