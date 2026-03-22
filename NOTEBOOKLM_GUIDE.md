# NotebookLM - Claude API Entegrasyonu

Google NotebookLM'deki notlarınızı Claude API kullanarak güçlendirilmiş hale getirin!

## 🎯 Özellikler

### 1. **Notları Özetleme** (`summarize_notes`)
- Kısa, orta veya uzun özet oluştur
- Türkçe veya İngilizce dilinde
- Önemli noktaları vurgula

```python
from notebooklm_integration import summarize_notes

notlar = "Yapay Zeka hakkında uzun notlar..."
özet = summarize_notes(notlar, summary_length="medium", language="tr")
print(özet)
```

### 2. **Ana Noktaları Çıkarma** (`extract_key_points`)
- En önemli 5-10 noktayı otomatik çıkart
- Kavramları yapılandırılmış listede göster
- JSON formatında sonuç

```python
from notebooklm_integration import extract_key_points

notlar = "..."
noktalar = extract_key_points(notlar, max_points=7)
print(noktalar)
```

### 3. **Soru-Cevap Oluşturma** (`generate_qa`)
- Otomatik test soruları üret
- 3 zorluk seviyesi: Easy, Medium, Hard
- Doğru cevaplarla birlikte

```python
from notebooklm_integration import generate_qa

notlar = "..."
qa = generate_qa(notlar, question_count=10, difficulty="medium")
print(qa)
```

### 4. **Çalışma Rehberi Oluşturma** (`create_study_guide`)
- Yapılandırılmış ders notları
- Mind map formatı
- Zaman çizelgesi

```python
from notebooklm_integration import create_study_guide

notlar = "..."
rehber = create_study_guide(notlar, format="structured")
print(rehber)
```

## 🚀 Kurulum

### 1. Gerekli Kütüphaneleri Yükle
```bash
pip install anthropic python-dotenv requests
```

### 2. API Anahtarını Ayarla
`.env` dosyası oluştur:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 3. Scriptı Çalıştır
```bash
python notebooklm_integration.py
```

## 📝 Kullanım Örnekleri

### Örnek 1: NotebookLM Notlarını Hızlı Özetle
```python
from notebooklm_integration import process_notebook_content

# NotebookLM'den kopyaladığınız notlar
my_notes = """
Veri Analizi ve Python

Python, veri bilimi için en popüler programlama dilidir.
Kütüphaneler:
- Pandas: Veri işleme
- NumPy: Matematiksel işlemler
- Matplotlib: Görselleştirme
"""

# Özetle
özet = process_notebook_content(my_notes, operation="summarize")
print(özet)
```

### Örnek 2: İnteraktif Oturum
```python
from notebooklm_integration import interactive_notebooklm_session

# Etkileşimli moda gir
interactive_notebooklm_session()
```

Komutlar:
- `/özetlet` - Özetleme
- `/noktalar` - Ana noktaları çıkart
- `/sorular` - Soru-cevap oluştur
- `/rehber` - Çalışma rehberi
- `/çıkış` - Çıkış

### Örnek 3: Python Scripti ile Otomasyonu
```python
from notebooklm_integration import (
    summarize_notes,
    extract_key_points,
    generate_qa,
    create_study_guide
)

# NotebookLM'den kaynaklanan notlar
notes = open("notebooklm_export.txt").read()

# Tüm işlemleri yap
print("1. ÖZET:")
print(summarize_notes(notes))

print("\n2. ANA NOKTALAR:")
print(extract_key_points(notes))

print("\n3. SORULAR:")
print(generate_qa(notes, 5))

print("\n4. ÇALIŞMA REHBERİ:")
print(create_study_guide(notes))
```

## 🔧 İleri Özellikleri

### Custom Model Kullanma
Kodda `claude-opus-4-6` yerine başka model kullan:
```python
response = client.messages.create(
    model="claude-sonnet-4-6",  # veya claude-haiku-4-5
    max_tokens=2000,
    ...
)
```

### Türkçe vs İngilizce
```python
# İngilizce özet
özet_en = summarize_notes(notes, language="en")

# Türkçe özet
özet_tr = summarize_notes(notes, language="tr")
```

### Zorluk Seviyeleri
```python
# Kolay sorular
easy_qa = generate_qa(notes, question_count=10, difficulty="easy")

# Zor sorular
hard_qa = generate_qa(notes, question_count=10, difficulty="hard")
```

## 📊 Çıktı Formatları

### Özetleme
```
Yapay Zeka, bilgisayarların insan zekasını taklit etme...
```

### Ana Noktalar
```json
[
  "Yapay Zeka, makine öğrenmesini kullanır",
  "Veri algoritmaların temelini oluşturur",
  "Tahminler modeller tarafından yapılır"
]
```

### Soru-Cevap
```json
[
  {
    "question": "Makine Öğrenmesi nedir?",
    "answer": "Veri kullanarak sistemlerin öğrenebilmesi..."
  }
]
```

## ⚠️ Dikkat Edilecekler

1. **API Limitleri**: Büyük notlar için `max_tokens` artır
2. **Dil Uyumluluğu**: NotebookLM diliyle eşleştir
3. **Token Maliyeti**: Uzun notlar daha fazla token kullanır
4. **Gizlilik**: Hassas bilgileri paylaşma

## 🎓 NotebookLM + Claude İş Akışı

```
NotebookLM (Not Almak)
         ↓
   Notları Export Et
         ↓
   Claude API (İşleme)
         ↓
   Özet/Sorular/Rehber
         ↓
   Çalışma Materyali
```

## 📱 Uyumlu Cihazlar

- Mac, Windows, Linux
- Cloud'da çalıştırılabilir
- Google Colab desteği

## 💡 Öneriler

- NotebookLM'de detaylı notlar al
- İlk olarak özet ile başla
- Zor konular için `hard` soruları kullan
- Study guide'ı sınav öncesi kullan

## 🐛 Sorun Giderme

**API Hatası**: `ANTHROPIC_API_KEY` doğru ayarlandığından emin ol
**Encoding Hatası**: Dosya kodlaması UTF-8 olsun
**Timeout**: Çok uzun metinler için `max_tokens` artır

## 📚 Kaynaklar

- [Claude API Docs](https://platform.claude.com/docs)
- [NotebookLM](https://notebooklm.google.com)
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python)

---

**Versiyon**: 1.0
**Dil**: Turkish (Türkçe)
**Güncelleme**: 2026-03-22
