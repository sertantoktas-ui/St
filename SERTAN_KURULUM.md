# SERTAN + NotebookLM Entegrasyonu - Kurulum Rehberi

## 🔑 Adım 1: API Anahtarını Hazırla

### Claude API Anahtarını Al
1. [https://console.anthropic.com/](https://console.anthropic.com/) adresine git
2. Oturum aç (Google hesabı ile)
3. Sol menüde "API Keys" seç
4. "+ Create Key" butonuna tıkla
5. Anahtarı kopyala (gizli tut!)

```
Örnek: sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📝 Adım 2: .env Dosyasını Oluştur

Proje klasöründe `.env` dosyası oluştur:

```bash
cp .env.example .env
```

Sonra `.env` dosyasını düzenle:

```env
# Claude API Configuration
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Kullanıcı Ayarları
USER_NAME=Sertan
USER_EMAIL=sertan@example.com

# Email Ayarları (İsteğe bağlı)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

---

## 🚀 Adım 3: SERTAN Dosyasını İşle

### Kütüphaneleri Kur (Bir Kez)
```bash
pip install anthropic python-dotenv
```

### SERTAN'ı İşle
```bash
python3 process_sertan.py
```

---

## 📊 Beklenen Çıktı

```
================================================================================
📚 SERTAN - NotebookLM Entegrasyonu ile İşleme
================================================================================

────────────────────────────────────────────────────────────────────────────────
1️⃣  KISA ÖZET
────────────────────────────────────────────────────────────────────────────────
Sertan, bilgisayar mühendisliğinin temel ilkelerini ve uygulamalarını kapsayan
kapsamlı bir eğitim platformudur. Yazılım geliştirme, veri bilimi ve yapay zeka
alanlarında teorik ve pratik bilgiyi birleştirerek kariyer odaklı çözümler sunmaktadır.

────────────────────────────────────────────────────────────────────────────────
2️⃣  ANA NOKTALAR (8 Nokta)
────────────────────────────────────────────────────────────────────────────────
  1. Sertan bilgisayar mühendisliğinin temel alanlarını kapsar
  2. Frontend, Backend, DevOps ve AI/ML teknolojileri öğretilir
  3. Teorik ve pratik öğrenme yöntemi birleştirilmiştir
  4. Proje tabanlı öğrenme yaklaşımı kullanılır
  5. Mentoring ve kariyer rehberliği sağlanır
  6. SOLID prensipleri ve tasarım desenleri öğretilir
  7. Agile metodolojisi ve takım çalışması vurgulanır
  8. %80+ iş bulma oranı ve kariyer gelişimi hedeflenmiştir

────────────────────────────────────────────────────────────────────────────────
3️⃣  SORU-CEVAP SETİ (5 Soru)
────────────────────────────────────────────────────────────────────────────────

  ❓ Soru 1: Sertan platformu hangi alanlara odaklanmaktadır?
  ✅ Cevap: Sertan yazılım geliştirme, veri bilimi ve yapay zeka alanlarında
      eğitim sunan kapsamlı bir platformdur. Frontend ve backend teknolojileri,
      bulut altyapısı, DevOps ve makine öğrenmesi gibi modern yazılım mühendisliğinin
      tüm aspektlerini kapsamaktadır.

  ❓ Soru 2: Sertan'ın hedef kitlesi kimlerdir?
  ✅ Cevap: Sertan'ın hedef kitlesi başlangıç seviyesi öğrenciler, kariyerini
      değiştirmek isteyenler, mühendislik öğrencileri ve profesyonel gelişim arayanları
      içermektedir. Platform her seviyedeki öğrenenlere uygun şekilde yapılandırılmıştır.

  ❓ Soru 3: Sertan'da kullanılan temel öğrenme yöntemi nedir?
  ✅ Cevap: Sertan dört ana öğrenme yöntemi kullanmaktadır: Teorik eğitim,
      pratik uygulamalar, proje tabanlı öğrenme ve deneyimli profesyonellerden
      mentoring. Bu yaklaşım kavramların derinlemesine anlaşılmasını sağlamaktadır.

  ❓ Soru 4: SOLID prensipleri nedir ve neden önemlidir?
  ✅ Cevap: SOLID, yazılım tasarımının beş temel prensibini temsil eder:
      Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation
      ve Dependency Inversion. Bu prensipleri takip etmek, kodun kalitesini,
      bakımlanabilirliğini ve ölçeklenebilirliğini arttırır.

  ❓ Soru 5: Sertan'da hangi kariyer yolları sunulmaktadır?
  ✅ Cevap: Sertan dört ana kariyer yolunu sunar: Junior Geliştirici (0-2 yıl),
      Mid-Level Geliştirici (2-5 yıl), Senior Geliştirici (5+ yıl) ve Uzmanlaşmış
      Roller (DevOps Engineer, Data Scientist, ML Engineer, Security Engineer).

────────────────────────────────────────────────────────────────────────────────
4️⃣  YAPILI ÇALIŞMA REHBERİ
────────────────────────────────────────────────────────────────────────────────

## SERTAN Kapsamlı Çalışma Rehberi

### I. TEMEL KONSEPTLER
1. **Sertan Platformu**
   - Tanım: Bilgisayar mühendisliğinin temel ilkelerini kapsayan eğitim platformu
   - Kuruluş: 2024 yılında
   - Alanlar: Yazılım geliştirme, veri bilimi, yapay zeka

2. **Dört Ana Öğrenme Yöntemi**
   - Teorik eğitim
   - Pratik uygulamalar
   - Proje tabanlı öğrenme
   - Mentoring

### II. TEKNOLOJI ALANLARI

#### Frontend Stack
- HTML5, CSS3, JavaScript
- React, Vue.js, Angular

#### Backend Stack
- Python, Java, Node.js
- Express, Flask, Django

#### Veri Bilimi Stack
- Python, R, SQL
- Pandas, NumPy, Scikit-learn

#### Yapay Zeka Stack
- TensorFlow, PyTorch
- NLP (BERT, GPT)
- Bilgisayar Görüşü (OpenCV)

### III. KARIYER GELIŞIM YOL HARİTASI

```
Başlangıç
   ↓
Junior Developer (0-2 yıl)
   ↓
Mid-Level Developer (2-5 yıl)
   ↓
Senior Developer (5+ yıl)
   ↓
Uzmanlaşmış Roller veya Liderlik
```

### IV. ÖNEMLİ PRENSİPLER

1. **SOLID Prensipleri**
   - S: Single Responsibility
   - O: Open/Closed
   - L: Liskov Substitution
   - I: Interface Segregation
   - D: Dependency Inversion

2. **Yazılım Mimarisi**
   - MVC, MVVM
   - Microservices
   - Event-Driven Architecture

3. **Agile Metodolojisi**
   - Sprint Planning
   - Daily Standup
   - Sprint Review
   - Kanban Board

### V. BAŞARI METRİKLERİ

- Kursları tamamlama: 95%+
- Proje portföyü: 5+ proje
- İş bulma oranı: 80%+
- Maaş artışı: 35% ortalama

### VI. ÖĞRENME KAYNAKLARI

- **Online Platform**: Udemy, Coursera, Pluralsight
- **Video**: YouTube Kanalları
- **Kod**: GitHub Repositories
- **Kitaplar**: Clean Code, Design Patterns
- **Komunite**: Stack Overflow, Reddit, Discord

────────────────────────────────────────────────────────────────────────────────
5️⃣  SONUÇLAR DOSYAYA KAYDEDILIYOR
────────────────────────────────────────────────────────────────────────────────
✅ SERTAN_PROCESSED.md dosyası oluşturuldu!
📁 Dosya yolu: ./SERTAN_PROCESSED.md

================================================================================
✨ İşlem Tamamlandı!
================================================================================

💡 İpuçları:
   - SERTAN_PROCESSED.md dosyasını görüntüle
   - Sonuçları NotebookLM'e kopyala
   - Sorularla kendinizi test et
   - Rehberi çalışma materyali olarak kullan
```

---

## ✅ Kurulum Kontrol Listesi

- [ ] API anahtarını aldım
- [ ] `.env` dosyası oluşturdum
- [ ] `ANTHROPIC_API_KEY` ayarladım
- [ ] Kütüphaneleri kurdum (`pip install anthropic python-dotenv`)
- [ ] `process_sertan.py` çalıştırdım
- [ ] `SERTAN_PROCESSED.md` dosyasını oluşturdum

---

## 🐛 Sorun Giderme

### ❌ "Could not resolve authentication"
```
Çözüm: .env dosyasında ANTHROPIC_API_KEY doğru ayarlandığından emin ol
```

### ❌ "ModuleNotFoundError: No module named 'anthropic'"
```
Çözüm: pip install anthropic çalıştır
```

### ❌ "File not found: SERTAN.md"
```
Çözüm: process_sertan.py dosyasını SERTAN.md ile aynı klasörde çalıştır
```

---

## 🔄 Çalışma Akışı

```
1. SERTAN.md dosyasını okur
       ↓
2. Claude API'ye gönderir
       ↓
3. Özet, noktalar, sorular, rehber oluşturur
       ↓
4. SERTAN_PROCESSED.md dosyasına kaydeder
       ↓
5. NotebookLM'e kopyala ve kullan
```

---

## 🎯 Sonraki Adımlar

1. ✅ Kurulumu tamamla
2. 📊 `SERTAN_PROCESSED.md` dosyasını oluştur
3. 📋 Soru-cevap setini kullanarak kendinizi test et
4. 📚 Çalışma rehberini ders materyali olarak kullan
5. 💾 Sonuçları NotebookLM'e kopyala

---

**Sorular mı var?** Yardıma ihtiyacın varsa yazabilirsin! 💬
