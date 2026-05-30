# ⚡ AXTEA CNC HMI — Hızlı Başlangıç

## Windows 11 / macOS / Linux

### 1️⃣ Repository'yi indir

```bash
git clone https://github.com/sertantoktas-ui/St.git
cd St
```

(Veya ZIP indir: https://github.com/sertantoktas-ui/St/archive/refs/heads/claude/nifty-ride-Qmdgb.zip)

---

### 2️⃣ Server başlat

#### Windows (PowerShell):
```powershell
python serve.py
```

#### macOS / Linux:
```bash
python3 serve.py
```

Göreceksiniz:
```
✅ Server running at http://localhost:8000/hmi/index.html
✅ External: http://0.0.0.0:8000/hmi/index.html
```

---

### 3️⃣ Tarayıcıda aç

Aşağıdaki linki **tarayıcıya yapıştır:**

```
http://localhost:8000/hmi/index.html
```

---

## 🎮 Simülasyon Kontrolleri

| Tuş | İşlev |
|---|---|
| **1-5** | Sayfalar (Home, Design, Work, Inspect, Analyze) |
| **S** | Programı başlat |
| **P** | Duraklat/devam |
| **ESC** | Durdur |
| **F5/F12** | DevTools |

---

## ✨ Ne göreceksin

- 🔴 X/Y/Z eksen hareket (simülasyon)
- 📊 Yük barları (0-100%)
- 🎯 Hız göstergeleri (Feed/Spindle)
- 📈 Enerji grafiği
- 🛠️ Program start/stop/reset
- 📝 Notlar ekle/sil
- 🌍 7 dil desteği (TR, EN, DE, FR, IT, ES, ZH)

---

## 🆘 Sorun?

**Python yok?**
- Windows: https://www.python.org/downloads/
- macOS: `brew install python3`
- Linux: `sudo apt install python3`

**Port 8000 kullanımda?**
```bash
python3 serve.py --port 9000
# → http://localhost:9000/hmi/index.html
```

**Hala sorun?** → `/TROUBLESHOOT.md` oku

---

**Başladı mı? Ekran görüntüsü gönder!** 📸
