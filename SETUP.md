# 🚀 Tam Özellikli Kişisel Asistan - Kurulum Rehberi

## 📋 Sistem Gereksinimleri

- Python 3.8+
- pip (Python paket yöneticisi)
- 100 MB disk alanı
- İnternet bağlantısı

## 🔑 1. API Anahtarı Edinme

### Anthropic API Anahtarı

1. https://console.anthropic.com adresine git
2. Hesap oluştur/giriş yap
3. "API Keys" bölümüne git
4. Yeni anahtar oluştur
5. Anahtar: `sk-ant-...` formatında olacak

## 💾 2. Kurulum Adımları

### 2.1 Virtual Environment Oluştur

```bash
cd /home/user/St

# Virtual environment oluştur
python3 -m venv venv

# Aktif et
source venv/bin/activate  # Linux/macOS
# veya
venv\Scripts\activate  # Windows
```

### 2.2 Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

**Kurulu Kütüphaneler:**
- `anthropic>=0.30.0` - Claude API
- `python-dotenv>=1.0.0` - Ortam değişkenleri
- `requests>=2.31.0` - HTTP istekleri
- `reportlab>=4.0.0` - PDF oluşturma
- `weasyprint>=60.0` - HTML → PDF
- `streamlit>=1.28.0` - Web UI (opsiyonel)

### 2.3 Ortam Değişkenlerini Ayarla

```bash
# Şablon dosyası kopyala
cp .env.example .env

# .env dosyasını düzenle
nano .env  # Linux/macOS
# veya
notepad .env  # Windows
```

Minimum yapılandırma:
```env
ANTHROPIC_API_KEY=sk-ant-... (API anahtarınız)
USER_NAME=Adınız
USER_EMAIL=email@example.com
```

## 📧 3. Email Gönderme Ayarı (Opsiyonel)

### 3.1 Gmail Kullanarak

1. https://myaccount.google.com/security adresine git
2. "2-Step Verification" etkinleştir
3. "App Passwords" bölümüne git
4. "Mail" ve "Windows Computer" seç
5. 16 karakterli şifreyi kopyala

.env dosyasına ekle:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=xxxxxx xxxx xxxx xxxx
```

### 3.2 Outlook Kullanarak

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

## 🚀 4. Uygulamayı Çalıştırma

### Seçenek 1: Basit Versiyon (Hızlı Start)
```bash
python personal_assistant.py
```

### Seçenek 2: İleri Versiyon (Tool Use)
```bash
python advanced_assistant.py
```

### Seçenek 3: Tam Özellikli (Önerilen) ✅
```bash
python full_featured_assistant.py
```
- ✅ Veritabanı entegrasyonu
- ✅ Email gönderme
- ✅ PDF rapor oluşturma
- ✅ Tool Use desteği

## 📊 5. Veritabanı Yönetimi

Veriler otomatik olarak `assistant.db` dosyasında saklanır.

### Veritabanını Temizle
```bash
rm assistant.db
```

Uygulamayı çalıştırdığında otomatik yeniden oluşturulur.

## 📚 6. Kullanım Örnekleri

### Email Yazma
```
📝 Siz: Email yaz: Müşteriye yeni fiyat listesi hakkında

🔧 create_email çalıştırılıyor...
📧 EMAIL OLUŞTURULDU
===================================================
Alıcı: Müşteri Adı
Konu: Yeni Fiyat Listesi
...
✅ Email başarıyla gönderildi!
```

### Rapor Oluşturma
```
📝 Siz: Rapor yap: 2024 Satış Analizi

🔧 create_report çalıştırılıyor...
📄 RAPOR OLUŞTURULDU
===================================================
Başlık: 2024 Satış Analizi
Format: text
...
✅ PDF dosyası oluşturuldu: ./reports/report_20240115_143022.pdf
```

### Görev Yönetimi
```
📝 Siz: Görev ekle: Sunuyu PowerPoint'e dönüştür

✅ Görev eklendi (ID: 1): Sunuyu PowerPoint'e dönüştür
```

### İstatistikleri Göster
```
📝 Siz: İstatistikleri göster

📊 ASISTAN İSTATİSTİKLERİ
================================================
✅ Tamamlanan Görevler: 5
⭕ Beklemede Görevler: 3

📧 EMAIL
✉️  Gönderilen: 12
📬 Gönderilmeyen: 4

📄 RAPORLAR
📋 Toplam: 8
================================================
```

## 🔧 7. Sorun Giderme

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
# Virtual environment aktif olduğundan emin ol
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY not found"
```bash
# .env dosyası oluşturduğundan emin ol
ls -la .env  # Linux/macOS
dir .env     # Windows

# Eğer yoksa:
cp .env.example .env
# Sonra API anahtarını ekle
```

### Email gönderme hatası
```
❌ Email gönderme hatası: 535, b'5.7.8 Username and Password not accepted'
```

**Çözüm:**
- Gmail kullanıyorsanız: App Password kullandığınızdan emin olun (normal şifre değil)
- Outlook: SMTP ayarlarını kontrol et
- 2FA etkinse: App password oluştur

## 📁 8. Dosya Yapısı

```
/home/user/St/
├── personal_assistant.py        # Basit versiyon
├── advanced_assistant.py         # Tool Use versiyon
├── full_featured_assistant.py    # Tam özellikli ⭐
├── database.py                  # Veritabanı yönetimi
├── email_service.py             # Email gönderme
├── pdf_generator.py             # PDF oluşturma
├── requirements.txt             # Bağımlılıklar
├── .env.example                 # Yapılandırma şablonu
├── .env                         # Gerçek yapılandırma (git'te yok)
├── assistant.db                 # SQLite veritabanı
├── reports/                     # Oluşturulan PDF raporlar
├── SETUP.md                     # Bu dosya
└── README.md                    # Genel dokümantasyon
```

## 🔐 9. Güvenlik Notları

⚠️ **ÖNEMLI:**
1. `.env` dosyasını **asla** git repository'ye commit etme
   ```bash
   echo ".env" >> .gitignore
   ```

2. API anahtarlarını kamuya açıklamaktan kaçın

3. Çok hassas işlemler için:
   ```python
   # Kullanıcı onayı isteyin
   confirmation = input("Emin misiniz? (Y/n): ")
   if confirmation.lower() == 'y':
       # İşlemi yap
   ```

## 📖 10. Sonraki Adımlar

### Geliştirebileceğiniz Özellikler

1. **Web UI (Streamlit)**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Webhook entegrasyonu** - Harici uygulamalarla bağlantı

3. **Dosya işleme** - PDF/Word dosyalarını analiz et

4. **Zamanlama** - Belirli zamanlarda otomatik görevler

5. **Multi-user** - Birden fazla kullanıcı desteği

6. **Cloud depolama** - Google Drive/Dropbox entegrasyonu

## 💬 11. Yardım ve Destek

Sorunlarla karşılaştığınız takdirde:

1. Logları kontrol et (konsol çıktısı)
2. `.env` dosyasını doğrula
3. API anahtarının geçerli olduğunu kontrol et
4. İnternet bağlantısını test et

## 📝 12. Lisans

MIT License - Özgürce kullan, değiştir ve dağıt

---

**Başarıyla kuruldu! 🎉 Şimdi `python full_featured_assistant.py` çalıştırabilirsiniz.**
