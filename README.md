# 🤖 Claude AI Kişisel Asistan

Claude API'si ile güçlendirilmiş, **tam özellikli** kişisel asistan uygulaması.

## ✨ Özellikler

### ✅ Temel Özellikler
- **📧 Email Yazma & Gönderme**: Profesyonel emailler yazma ve SMTP ile gönderme
- **📄 PDF Rapor Oluşturma**: Text, Markdown, HTML'den PDF üretme
- **✅ Görev Yönetemi**: SQLite ile kalıcı görev depolama
- **📊 İstatistikler**: Sistem istatistiklerini göster

### 🔧 İleri Özellikler
- **🗄️ Veritabanı Entegrasyonu**: SQLite ile kalıcı depolama (emailler, raporlar, görevler)
- **📧 SMTP Email Gönderme**: Gmail, Outlook, Custom SMTP desteği
- **📊 Raporlama**: Fatura stili, Markdown, HTML raporlar
- **🎯 Tool Use (Agentic Loops)**: Claude'un araçları otomatik çağırması

## 📦 Kurulum (30 saniye)

### Hızlı Başlangıç

```bash
# 1. Paketleri yükle
cd /home/user/St
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Yapılandır
cp .env.example .env
# .env dosyasını açıp ANTHROPIC_API_KEY'i ekle

# 3. Çalıştır
python full_featured_assistant.py
```

**Detaylı kurulum rehberi**: [SETUP.md](SETUP.md)

## 🚀 Kullanım

### 3 Versiyon Mevcut

| Versiyon | Komut | Özellikler |
|----------|-------|-----------|
| **Basit** | `python personal_assistant.py` | 💬 Konuşma |
| **İleri** | `python advanced_assistant.py` | 🔧 Tool Use |
| **Tam** ✅ | `python full_featured_assistant.py` | ✅ HERŞEYİ |

### Örnek Komutlar

```
📝 Siz: Email yaz: Müşteriye proje tamamlandı raporu
🤖 Asistan: [Email oluşturur, kaydeder ve gönderir]

📝 Siz: Rapor yap: 2024 Satış Analizi
🤖 Asistan: [PDF rapor oluşturur]

📝 Siz: Görev ekle: Sunuyu hazırla
🤖 Asistan: [Görev veritabanına kaydeder]

📝 Siz: Görevleri listele
🤖 Asistan: [Tüm görevleri gösterir]

📝 Siz: İstatistikleri göster
🤖 Asistan: [Sistem stats: 5 görev, 12 email, 8 rapor]
```

## 🔧 Teknoloji Stack

| Bileşen | Teknoloji |
|---------|-----------|
| **AI Model** | Claude Opus 4.6 |
| **SDK** | Anthropic Python SDK |
| **Veritabanı** | SQLite |
| **Email** | smtplib (Gmail/Outlook) |
| **PDF** | ReportLab |

## 📁 Dosya Yapısı

```
/home/user/St/
├── full_featured_assistant.py    # ⭐ Ana uygulama
├── database.py                   # SQLite yönetimi
├── email_service.py              # SMTP email
├── pdf_generator.py              # PDF oluşturma
├── requirements.txt              # Bağımlılıklar
├── .env.example                  # Yapılandırma
├── assistant.db                  # Veritabanı
├── reports/                      # PDF dosyaları
├── SETUP.md                      # Kurulum rehberi
└── README.md                     # Bu dosya
```

## 🎯 Özellik Karşılaştırması

| Özellik | Basit | İleri | Tam |
|---------|-------|-------|-----|
| Konuşma | ✅ | ✅ | ✅ |
| Tool Use | ❌ | ✅ | ✅ |
| Veritabanı | ❌ | ❌ | ✅ |
| Email Gönderme | ❌ | ❌ | ✅ |
| PDF Rapor | ❌ | ❌ | ✅ |
| İstatistikler | ❌ | ❌ | ✅ |

## 🔐 Güvenlik

⚠️ **Önemli:**
- `.env` dosyasını repository'ye commit etmeyin
- `git config` ile API anahtarlarını yönetin

## 📚 Dokümantasyon

- [SETUP.md](SETUP.md) - Detaylı kurulum & yapılandırma
- [Email Ayarı](SETUP.md#3-email-gönderme-ayarı-opsiyonel) - Gmail/Outlook kurulumu
- [Sorun Çözme](SETUP.md#7-sorun-giderme) - Sık sorulan hatalar

## 🚀 Geliştirme Yol Haritası

- [ ] Web UI (Streamlit)
- [ ] Dosya işleme (PDF analizi)
- [ ] Zamanlama (Cron jobs)
- [ ] Cloud entegrasyonu
- [ ] Multi-user desteği

## 🆘 Hızlı Yardım

| Sorun | Çözüm |
|-------|-------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `API_KEY not found` | `.env` dosyasında `ANTHROPIC_API_KEY` kontrol et |
| Email gönderilmiyor | [SETUP.md#email-ayarı](SETUP.md) okuyun |
| PDF oluşturulmuyor | `reportlab` yüklü mü? `pip install reportlab` |

## 📝 Lisans

MIT License - Özgürce kullan ve dağıt

---

**Başlamak için**: `python full_featured_assistant.py` 🚀
