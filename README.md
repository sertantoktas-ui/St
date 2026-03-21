# 🤖 Claude AI Kişisel Asistan

Claude API'si ile güçlendirilmiş, özelleştirilebilir bir kişisel asistan uygulaması.

## ✨ Özellikler

- **📧 Email Yazma**: Profesyonel email taslakları oluşturma
- **📄 Rapor Oluşturma**: Detaylı raporlar hazırlama (Markdown, HTML, Text)
- **🔍 Web Arama**: İnternet'ten bilgi toplama
- **✅ Görev Yönetimi**: Görevleri planlama, takip etme ve tamamlama

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Anthropic API Anahtarı

### Kurulum Adımları

```bash
# Proje dizinine gir
cd /home/user/St

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate

# Paketleri yükle
pip install -r requirements.txt
```

### API Anahtarını Ayarla

```bash
cp .env.example .env
# .env dosyasını düzenle ve API anahtarını ekle
```

## 📖 Kullanım

### Basit Versiyon
```bash
python personal_assistant.py
```

### İleri Versiyon (Tool Use)
```bash
python advanced_assistant.py
```

## 📚 Örnek Komutlar

```
"Email yaz: Müşteriye yeni fiyat listesi hakkında"
"Rapor yap: Q4 2024 Performans Analizi"
"Ara: Python'da en iyi web framework'leri"
"Görev ekle: Sunuyu PowerPoint'e dönüştür"
```

## 🔧 Teknoloji Stack

- **Framework**: Anthropic SDK
- **Model**: Claude Opus 4.6
- **Language**: Python 3.8+
- **Architecture**: Multi-turn conversations, Tool Use (Beta)

## 🚢 Sonraki Özellikler

- Database entegrasyonu
- SMTP email gönderme
- PDF rapor export
- Dosya işleme
- Web UI (Streamlit)
- Multi-user support

---

**Oluşturulma**: 2024 | **MIT Lisansı**
