# NotebookLM + Claude Code Entegrasyonu

Bu rehber, Claude Code ortamında Google NotebookLM benzeri belge analizi özelliklerinin nasıl kullanılacağını açıklamaktadır.

## 🎯 Genel Bakış

NotebookLM entegrasyonu, kişisel asistanınıza aşağıdaki belge analizi yeteneklerini ekler:

- 📄 **Belge Özeti**: Uzun belgelerin önemli noktalarını öğrenin
- 📍 **Yapılandırılmış Anahat**: Belgenin yapısını anlaşılır bir şekilde göster
- 💬 **Belge Hakkında Sorular**: Belge içeriği hakkında doğal dil sorularını cevapla
- 🔄 **Belge Karşılaştırması**: Birden fazla belgeyi karşılaştır

## 🚀 Hızlı Başlangıç

### 1. Kurulum

Gerekli paketler `requirements.txt`'te zaten listelenmiştir. Güncelleyin:

```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Başlat

```bash
python full_featured_assistant.py
```

### 3. Belge Ekle

Asistana şu şekilde belge ekleyin:

```
Belge ekle: Proje Özeti, İmplementasyon Detayları, Zaman çizelgesi...
```

veya daha spesifik:

```
Lütfen bu belgeyi analiz et: 
[Belgenizin adı]

[Belgenin tam içeriği]
```

## 📚 Kullanım Örnekleri

### Örnek 1: Belge Özetini Al

```
Siz: "2024 Satış Raporu adında belge ekle. İçerik: [belge metni]"
Asistan: ✅ Belge eklendi

Siz: "Belgeyi analiz et ve özeti göster"
Asistan: 📋 Belgenin önemli noktalarını liste halinde gösterir
```

### Örnek 2: Belge Hakkında Sorular Sor

```
Siz: "Belge hakkında soru: Q3'te toplam satış ne kadarı?"
Asistan: 💬 Belgedeki bilgilere dayanarak cevap verir
```

### Örnek 3: Anahat Oluştur

```
Siz: "Belgenin yapısal anhatını oluştur"
Asistan: 📍 Belgenin hiyerarşik yapısını gösterir
```

## 🔧 Teknik Detaylar

### NotebookLMIntegration Sınıfı

Dosya: `notebooklm_integration.py`

#### Temel Metodlar:

1. **add_document(doc_id, content, title)**
   - Analiz için belge ekler
   - Parametreler:
     - `doc_id`: Benzersiz belge kimliği
     - `content`: Belgenin tam içeriği
     - `title`: Belge başlığı

2. **generate_summary(doc_id)**
   - Belgenin özetini oluşturur
   - Çıktı:
     - Ana Noktalar (3-5 madde)
     - Önemli İçgörüler
     - Eylem Öğeleri (varsa)

3. **generate_outline(doc_id)**
   - Yapılandırılmış anahat oluşturur
   - Hiyerarşik madde işareti formatında

4. **ask_document(doc_id, question)**
   - Belge hakkında doğal dil sorularını cevaplar
   - Konversasyon geçmişini saklar

5. **compare_documents(doc_ids, analysis_type)**
   - Birden fazla belgeyi karşılaştırır
   - `analysis_type`: "differences", "similarities", "synthesis"

6. **export_analysis(doc_id, format_type)**
   - Analizi dışa aktarır
   - Formatlar: "markdown", "json"

### Entegre Araçlar

`full_featured_assistant.py`'da şu araçlar uygulanır:

```python
TOOLS = [
    ...
    {
        "name": "add_document_notebooklm",
        "description": "NotebookLM benzeri analiz için belge ekle"
    },
    {
        "name": "analyze_document",
        "description": "Belgeyi analiz et (özet, anahat)"
    },
    {
        "name": "ask_document",
        "description": "Belge hakkında sorular sor"
    }
]
```

## 💡 İleri Kullanım

### Çoklu Belge Analizi

```python
# Python'da doğrudan kullanım
from notebooklm_integration import NotebookLMIntegration

nl = NotebookLMIntegration()

# Belgeleri ekle
nl.add_document("doc1", content1, "Rapor 1")
nl.add_document("doc2", content2, "Rapor 2")

# Karşılaştır
comparison = nl.compare_documents(
    ["doc1", "doc2"], 
    analysis_type="synthesis"
)
```

### Sonuçları Dışa Aktar

```python
# Markdown olarak
analysis = nl.export_analysis("doc1", format_type="markdown")

# JSON olarak
analysis = nl.export_analysis("doc1", format_type="json")
```

## 🔐 Güvenlik Notları

- NotebookLM entegrasyonu tamamen yerel olarak çalışır (Claude API'si kullanır)
- Belge verileriniz sadece Claude API'sine gönderilir
- `.env` dosyasında API anahtarınızı saklayın (repository'ye commit etmeyin)

## 🐛 Sorun Giderme

### Soruna: "Document not found"
**Çözüm**: Belge ID'sini kontrol edin, belgeyi önce ekledğinizden emin olun

### Soruna: "API_KEY not found"
**Çözüm**: `.env` dosyasında `ANTHROPIC_API_KEY` ayarlanmış mı kontrol edin

### Soruna: Yanıtlar çok kısasa
**Çözüm**: Belgenin açık ve yapılandırılmış biçimde olduğundan emin olun

## 📖 Referans

### Desteklenen Belge Türleri
- Metin dosyaları
- Markdown
- HTML
- JSON
- CSV (yapılandırılmış veriler)
- Email içeriği
- Chat transkriptleri

### Desteklenen Analiz Türleri
- **summary**: Özet ve ana noktalar
- **outline**: Yapılandırılmış anahat
- **comparison**: Belge karşılaştırması
- **synthesis**: Birden fazla kaynaktan sentez

## 🆚 Google NotebookLM vs Bu Entegrasyon

| Özellik | Google NotebookLM | Bu Entegrasyon |
|---------|------------------|-----------------|
| Web UI | ✅ | ❌ (CLI) |
| Belge Yükle | ✅ | ✅ (metin olarak) |
| Özet | ✅ | ✅ |
| Anahat | ✅ | ✅ |
| Q&A | ✅ | ✅ |
| Audio Özetler | ✅ | ❌ |
| Yerel Çalışma | ❌ | ✅ |
| Kişisel Asistan Entegrasyonu | ❌ | ✅ |

## 📞 Destek

Sorunlar veya öneriler için `full_featured_assistant.py` dosyasında güncellemeleri kontrol edin veya yeni bir issue oluşturun.

---

**Başlamak için**: `python full_featured_assistant.py` komutunu çalıştırın ve belge eklemeye başlayın! 🚀
